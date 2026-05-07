from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Offer:
    offer_id: str
    title: str
    description: str
    budget: str
    url: str
    raw_text: str


@dataclass(slots=True)
class MatchedOffer:
    offer: Offer
    match_percent: int
    reasoning: str
    generated_reply: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["offer"] = asdict(self.offer)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchedOffer":
        return cls(offer=Offer(**data["offer"]), match_percent=data["match_percent"], reasoning=data["reasoning"], generated_reply=data.get("generated_reply"), created_at=data.get("created_at", datetime.utcnow().isoformat()))
