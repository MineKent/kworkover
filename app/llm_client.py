from __future__ import annotations

import httpx

from app.models import MatchedOffer


class ReplyGenerator:
    def __init__(
        self,
        api_key: str,
        model: str,
        skills_profile: str,
        base_url: str,
        site_url: str,
        site_name: str,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.skills_profile = skills_profile
        self.base_url = base_url.rstrip("/")
        self.site_url = site_url
        self.site_name = site_name

    def generate_reply(self, matched_offer: MatchedOffer) -> str:
        prompt = f"""
Ты помогаешь фрилансеру отвечать на заявки в Kwork.

Профиль навыков исполнителя:
{self.skills_profile}

Заявка:
Название: {matched_offer.offer.title}
Бюджет: {matched_offer.offer.budget}
Описание: {matched_offer.offer.description}

Причина совпадения:
{matched_offer.reasoning}

Сгенерируй короткий, уверенный и человеческий отклик на русском языке.
Требования:
- 500 символов максимум
- Без воды и шаблонных фраз
- Покажи релевантный опыт
- Заверши 1-2 уточняющими вопросами, если это уместно
""".strip()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Пиши отклики для фриланс-биржи кратко, конкретно и по делу."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()
