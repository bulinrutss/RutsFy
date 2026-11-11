"""Filtros aplicados a listas descobríveis (busca, mix, canal)."""

from __future__ import annotations

from typing import Any

from app.duration_policy import filter_discoverable_items
from app.title_dedupe import dedupe_similar_tracks


def prepare_discoverable_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return dedupe_similar_tracks(filter_discoverable_items(items))
