from __future__ import annotations

import asyncio
import logging

from app.bootstrap import prepare_runtime_files
from app.config import load_settings
from app.kwork_client import KworkClient
from app.llm_client import ReplyGenerator
from app.service import OfferMonitorService
from app.skill_matcher import SkillMatcher
from app.storage import StateStorage
from app.telegram_bot import TelegramNotifier
from app.web import run_healthcheck_server


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    settings = load_settings()
    prepare_runtime_files(settings)
    storage = StateStorage()
    matcher = SkillMatcher(settings.skills_profile)
    kwork_client = KworkClient(settings)
    reply_generator = ReplyGenerator(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        skills_profile=settings.skills_profile,
        base_url=settings.openrouter_base_url,
        site_url=settings.openrouter_site_url,
        site_name=settings.openrouter_site_name,
    )
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id, settings.telegram_proxy)
    service = OfferMonitorService(settings, storage, matcher, kwork_client, reply_generator, notifier)

    await asyncio.gather(service.run(), run_healthcheck_server(settings.port))


if __name__ == "__main__":
    asyncio.run(main())
