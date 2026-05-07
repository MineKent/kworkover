from __future__ import annotations

from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Bot, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from app.models import MatchedOffer

if TYPE_CHECKING:
    from app.service import OfferMonitorService


class TelegramNotifier:
    def __init__(self, token: str, chat_id: int, proxy: str = "") -> None:
        session = AiohttpSession(proxy=proxy) if proxy else None
        self.bot = Bot(token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.chat_id = chat_id

    async def send_match(self, matched_offer: MatchedOffer) -> None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Generate reply", callback_data=f"generate:{matched_offer.offer.offer_id}")],
                [InlineKeyboardButton(text="Open offer", url=matched_offer.offer.url)],
            ]
        )
        message = (
            f"<b>{escape(matched_offer.offer.title)}</b>\n"
            f"Match: <b>{matched_offer.match_percent}%</b>\n"
            f"Budget: {escape(matched_offer.offer.budget or '-')}\n"
            f"{escape(matched_offer.reasoning)}\n\n"
            f"{escape(matched_offer.offer.description[:800])}"
        )
        await self.bot.send_message(self.chat_id, message, reply_markup=keyboard)

    async def send_generated_reply(self, matched_offer: MatchedOffer) -> None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Send to Kwork", callback_data=f"send:{matched_offer.offer.offer_id}")],
                [InlineKeyboardButton(text="Open offer", url=matched_offer.offer.url)],
            ]
        )
        text = (
            f"Draft for: <b>{escape(matched_offer.offer.title)}</b>\n\n"
            f"<pre>{escape(matched_offer.generated_reply or '')}</pre>"
        )
        await self.bot.send_message(self.chat_id, text, reply_markup=keyboard)


def build_router(service: OfferMonitorService) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Бот запущен. Новые подходящие заявки будут приходить сюда.")

    @router.message(Command("debug"))
    async def debug(message: Message) -> None:
        html_path = Path("data/kwork_page.html")
        if not html_path.exists():
            await message.answer("Файл data/kwork_page.html не найден. Сначала дождись следующего запуска парсинга.")
            return
        
        html_content = html_path.read_text(encoding="utf-8")
        if len(html_content) > 4000:
            await message.answer(f"HTML файл слишком большой ({len(html_content)} символов). Вот начало:\n\n{escape(html_content[:4000])}")
            await message.answer(f"Продолжение:\n\n{escape(html_content[4000:8000])}")
        else:
            await message.answer(f"<pre>{escape(html_content)}</pre>")

    @router.callback_query(F.data.startswith("generate:"))
    async def generate_reply(callback: CallbackQuery) -> None:
        offer_id = callback.data.split(":", 1)[1]
        await callback.answer("Генерирую ответ...")
        matched_offer = await service.generate_reply_for_offer(offer_id)
        if not matched_offer:
            await callback.message.answer("Не нашел сохраненную заявку.")
            return
        await service.notifier.send_generated_reply(matched_offer)

    @router.callback_query(F.data.startswith("send:"))
    async def send_reply(callback: CallbackQuery) -> None:
        offer_id = callback.data.split(":", 1)[1]
        await callback.answer("Отправляю ответ в Kwork...")
        sent = await service.send_reply_for_offer(offer_id)
        if not sent:
            await callback.message.answer("Не удалось отправить ответ: нет сохраненного черновика.")
            return
        await callback.message.answer("Ответ отправлен в Kwork.")

    return router
