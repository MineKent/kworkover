from __future__ import annotations

import json
from pathlib import Path

from app.models import MatchedOffer


class StateStorage:
    def __init__(self, file_path: str = "./data/state.json") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({"seen_offer_ids": [], "matched_offers": {}})

    def get_seen_offer_ids(self) -> set[str]:
        data = self._read()
        return set(data.get("seen_offer_ids", []))

    def mark_offer_seen(self, offer_id: str) -> None:
        data = self._read()
        seen = set(data.get("seen_offer_ids", []))
        seen.add(offer_id)
        data["seen_offer_ids"] = sorted(seen)
        self._write(data)

    def save_match(self, matched_offer: MatchedOffer) -> None:
        data = self._read()
        data.setdefault("matched_offers", {})[matched_offer.offer.offer_id] = matched_offer.to_dict()
        self._write(data)

    def get_match(self, offer_id: str) -> MatchedOffer | None:
        data = self._read()
        item = data.get("matched_offers", {}).get(offer_id)
        if not item:
            return None
        return MatchedOffer.from_dict(item)

    def update_generated_reply(self, offer_id: str, generated_reply: str) -> MatchedOffer | None:
        matched = self.get_match(offer_id)
        if not matched:
            return None
        matched.generated_reply = generated_reply
        self.save_match(matched)
        return matched

    def _read(self) -> dict:
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
