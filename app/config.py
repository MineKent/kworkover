from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: int
    telegram_proxy: str
    kwork_projects_url: str
    kwork_storage_state_path: str
    kwork_storage_state_json: str
    kwork_poll_interval_seconds: int
    kwork_min_match_percent: int
    skills_profile: str
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str
    openrouter_site_url: str
    openrouter_site_name: str
    offer_card_selector: str
    offer_id_attribute: str
    title_selector: str
    description_selector: str
    budget_selector: str
    link_selector: str
    response_textarea_selector: str
    submit_button_selector: str


def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        telegram_bot_token=_get_required("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=int(_get_required("TELEGRAM_CHAT_ID")),
        telegram_proxy=os.getenv("TELEGRAM_PROXY", ""),
        kwork_projects_url=os.getenv("KWORK_PROJECTS_URL", "https://kwork.ru/projects"),
        kwork_storage_state_path=os.getenv("KWORK_STORAGE_STATE_PATH", "./data/kwork-storage.json"),
        kwork_storage_state_json=os.getenv("KWORK_STORAGE_STATE_JSON", ""),
        kwork_poll_interval_seconds=int(os.getenv("KWORK_POLL_INTERVAL_SECONDS", "120")),
        kwork_min_match_percent=int(os.getenv("KWORK_MIN_MATCH_PERCENT", "55")),
        skills_profile=_get_required("SKILLS_PROFILE"),
        openrouter_api_key=_get_required("OPENROUTER_API_KEY"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free"),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        openrouter_site_url=os.getenv("OPENROUTER_SITE_URL", "https://example.com"),
        openrouter_site_name=os.getenv("OPENROUTER_SITE_NAME", "Kwork Offer Analyzer"),
        offer_card_selector=os.getenv("KWORK_OFFER_CARD_SELECTOR", ".project-card"),
        offer_id_attribute=os.getenv("KWORK_OFFER_ID_ATTRIBUTE", "data-id"),
        title_selector=os.getenv("KWORK_TITLE_SELECTOR", "h1, h2"),
        description_selector=os.getenv("KWORK_DESCRIPTION_SELECTOR", ".description"),
        budget_selector=os.getenv("KWORK_BUDGET_SELECTOR", ".price"),
        link_selector=os.getenv("KWORK_LINK_SELECTOR", "a"),
        response_textarea_selector=os.getenv("KWORK_RESPONSE_TEXTAREA_SELECTOR", "textarea"),
        submit_button_selector=os.getenv("KWORK_SUBMIT_BUTTON_SELECTOR", "button[type='submit']"),
    )


def _get_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required")
    return value
