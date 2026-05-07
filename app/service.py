from __future__ import annotations

import asyncio
import logging

from aiogram import Dispatcher

from app.config import Settings
from app.kwork_client import KworkClient
from app.llm_client import ReplyGenerator
from app.models import MatchedOffer
from app.skill_matcher import SkillMatcher
from app.storage import StateStorage
from app.telegram_bot import TelegramNotifier, build_router


class OfferMonitorService:
    def __init__(
        self,
        settings: Settings,
        storage: StateStorage,
        matcher: SkillMatcher,
        kwork_client: KworkClient,
        reply_generator: ReplyGenerator,
        notifier: TelegramNotifier,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.matcher = matcher
        self.kwork_client = kwork_client
        self.reply_generator = reply_generator
        self.notifier = notifier
        self.dispatcher = Dispatcher()
        self.dispatcher.include_router(build_router(self))

    async def run(self) -> None:
        await asyncio.gather(self._poll_offers(), self._run_bot())

    async def _run_bot(self) -> None:
        while True:
            try:
                await self.dispatcher.start_polling(self.notifier.bot)
                return
            except Exception:
                logging.exception("Telegram polling failed")
                await asyncio.sleep(10)

    async def _poll_offers(self) -> None:
        while True:
            try:
                await self.process_new_offers()
            except Exception:
                logging.exception("Offer polling failed")
            await asyncio.sleep(self.settings.kwork_poll_interval_seconds)

    async def process_new_offers(self) -> None:
        seen_offer_ids = self.storage.get_seen_offer_ids()
        offers = await self.kwork_client.fetch_offers()

        for offer in offers:
            if offer.offer_id in seen_offer_ids:
                continue

            self.storage.mark_offer_seen(offer.offer_id)
            match_percent, reasoning = self.matcher.score(offer)
            if match_percent < self.settings.kwork_min_match_percent:
                continue

            matched_offer = MatchedOffer(offer=offer, match_percent=match_percent, reasoning=reasoning)
            self.storage.save_match(matched_offer)
            await self.notifier.send_match(matched_offer)

    async def generate_reply_for_offer(self, offer_id: str) -> MatchedOffer | None:
        matched_offer = self.storage.get_match(offer_id)
        if not matched_offer:
            return None
        generated_reply = await asyncio.to_thread(self.reply_generator.generate_reply, matched_offer)
        return self.storage.update_generated_reply(offer_id, generated_reply)

    async def send_reply_for_offer(self, offer_id: str) -> bool:
        matched_offer = self.storage.get_match(offer_id)
        if not matched_offer or not matched_offer.generated_reply:
            return False
        await self.kwork_client.send_reply(matched_offer.offer.url, matched_offer.generated_reply)
        return True
