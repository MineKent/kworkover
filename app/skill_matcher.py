from __future__ import annotations

import math

from sentence_transformers import SentenceTransformer

from app.models import Offer


class SkillMatcher:
    def __init__(self, skills_profile: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.skills_profile = skills_profile
        self.model = SentenceTransformer(model_name)
        self.profile_embedding = self.model.encode(skills_profile, normalize_embeddings=True)

    def score(self, offer: Offer) -> tuple[int, str]:
        offer_text = "\n".join(filter(None, [offer.title, offer.description, offer.budget]))
        offer_embedding = self.model.encode(offer_text, normalize_embeddings=True)
        similarity = float(self.profile_embedding @ offer_embedding)
        percent = max(0, min(100, int(round((similarity + 1) * 50))))
        reasoning = self._build_reasoning(offer_text, percent)
        return percent, reasoning

    def _build_reasoning(self, offer_text: str, percent: int) -> str:
        skills = [item.strip() for item in self.skills_profile.split(",") if item.strip()]
        matched = [skill for skill in skills if skill.lower() in offer_text.lower()]
        if matched:
            return f"Совпадения по ключевым навыкам: {', '.join(matched[:5])}. Итоговая релевантность: {percent}%."
        if percent >= 70:
            return "Семантически задача близка к вашему профилю, даже если точные ключевые слова встречаются не все."
        if percent >= 50:
            return "Есть частичное пересечение по задачам и инструментам, стоит посмотреть вручную."
        return "Похоже на слабое совпадение с текущим профилем навыков."
