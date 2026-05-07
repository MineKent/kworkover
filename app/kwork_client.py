from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.async_api import Browser, BrowserContext, Locator, Page, async_playwright

from app.config import Settings
from app.models import Offer


class KworkClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage_state_path = Path(settings.kwork_storage_state_path)

    async def fetch_offers(self) -> list[Offer]:
        logging.info("Начинаю загрузку офферов с Kwork...")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await self._build_context(browser)
            page = await context.new_page()
            logging.info(f"Открываю страницу {self.settings.kwork_projects_url}...")
            await page.goto(self.settings.kwork_projects_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            html = await page.content()
            Path("data").mkdir(exist_ok=True)
            Path("data/kwork_page.html").write_text(html, encoding="utf-8")
            logging.info("Страница сохранена в data/kwork_page.html")
            
            logging.info("Страница загружена, извлекаю офферы...")
            offers = await self._extract_offers(page)
            logging.info(f"Извлечено {len(offers)} офферов")
            await context.close()
            await browser.close()
            return offers

    async def send_reply(self, offer_url: str, reply_text: str) -> None:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            if not self.storage_state_path.exists():
                await browser.close()
                raise FileNotFoundError(
                    f"Kwork session file not found: {self.storage_state_path}. Run scripts/save_kwork_session.py first."
                )
            context = await self._build_context(browser)
            page = await context.new_page()
            await page.goto(offer_url, wait_until="domcontentloaded")
            await page.locator(self.settings.response_textarea_selector).first.fill(reply_text)
            await page.locator(self.settings.submit_button_selector).first.click()
            await page.wait_for_timeout(2000)
            await context.close()
            await browser.close()

    async def _extract_offers(self, page: Page) -> list[Offer]:
        card_selector = self.settings.offer_card_selector
        logging.info(f"Ищу карточки по селектору: {card_selector}")
        
        cards = page.locator(card_selector)
        count = await cards.count()
        logging.info(f"Найдено карточек: {count}")
        
        offers: list[Offer] = []

        for index in range(count):
            card = cards.nth(index)
            title = await self._safe_text(card, self.settings.title_selector)
            description = await self._safe_text(card, self.settings.description_selector)
            budget = await self._safe_text(card, self.settings.budget_selector)
            href = await self._safe_href(card, self.settings.link_selector)
            
            if self.settings.offer_id_attribute:
                offer_id = await card.get_attribute(self.settings.offer_id_attribute)
            else:
                match = re.search(r"/projects/(\d+)", href or "")
                offer_id = match.group(1) if match else f"card-{index}"
            
            if not title and not description:
                continue

            offers.append(
                Offer(
                    offer_id=offer_id,
                    title=title,
                    description=description,
                    budget=budget,
                    url=urljoin(self.settings.kwork_projects_url, href or ""),
                    raw_text="\n".join(filter(None, [title, description, budget])),
                )
            )

        return offers

    async def _safe_text(self, scope: Locator | Page, selector: str) -> str:
        selectors = [item.strip() for item in selector.split(",") if item.strip()]
        for item in selectors:
            locator = scope.locator(item).first
            if await locator.count() == 0:
                continue
            text = (await locator.text_content()) or ""
            if text.strip():
                return " ".join(text.split())
        return ""

    async def _safe_href(self, scope: Locator | Page, selector: str) -> str:
        selectors = [item.strip() for item in selector.split(",") if item.strip()]
        for item in selectors:
            locator = scope.locator(item).first
            if await locator.count() == 0:
                continue
            href = await locator.get_attribute("href")
            if href:
                return href
        return ""

    async def _build_context(self, browser: Browser) -> BrowserContext:
        if self.storage_state_path.exists():
            return await browser.new_context(storage_state=str(self.storage_state_path))

        logging.warning(
            "Kwork session file %s not found. Running without authorization; sending replies will be unavailable until you save a session.",
            self.storage_state_path,
        )
        return await browser.new_context()
