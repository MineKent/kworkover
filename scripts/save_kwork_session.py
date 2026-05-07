from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main() -> None:
    Path("data").mkdir(exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://kwork.ru/login", wait_until="domcontentloaded")
        input("Войдите в Kwork и нажмите Enter...")
        await context.storage_state(path="data/kwork-storage.json")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
