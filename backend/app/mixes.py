"""Mixes / playlists de descoberta (presets de busca).

Décadas antigas usam só palavras na busca — a data de publicação do vídeo
quase nunca coincide com o ano da música (reuploads, canais oficiais, etc.).
Filtro por data de upload só em mixes explícitos (ex.: novidades).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

FilterMode = Literal["query", "upload_date"]


def _mix(
    mix_id: str,
    label: str,
    query: str,
    subtitle: str = "Curadoria por busca",
    *,
    filter_mode: FilterMode = "query",
    published_after_days: int | None = None,
    order: str | None = None,
) -> dict[str, Any]:
    m: dict[str, Any] = {
        "id": mix_id,
        "label": label,
        "subtitle": subtitle,
        "query": query,
        "filterMode": filter_mode,
    }
    if published_after_days is not None:
        m["publishedAfterDays"] = published_after_days
    if order:
        m["order"] = order
    return m


MIX_CATEGORIES: list[dict[str, Any]] = [
    {
        "id": "destaques",
        "label": "Destaques",
        "mixes": [
            _mix(
                "novidades",
                "Novidades",
                "official audio",
                "Uploads recentes (12 meses)",
                filter_mode="upload_date",
                published_after_days=365,
                order="date",
            ),
            _mix("hits-mundo", "Hits globais", "top hits official audio", "Pop e chart"),
            _mix("ao-vivo", "Ao vivo", "live concert official audio", "Shows e sessões"),
            _mix("acustico", "Acústico", "acoustic official audio", "Versões unplugged"),
        ],
    },
    {
        "id": "rock",
        "label": "Rock",
        "mixes": [
            _mix("rock-classico", "Rock clássico", "classic rock official audio"),
            _mix("rock-hard", "Hard rock", "hard rock official audio"),
            _mix("rock-alternativo", "Alternativo", "alternative rock official audio"),
            _mix("rock-80s", "Rock anos 80", "80s rock hits official audio", "Década na busca"),
            _mix("rock-90s", "Rock anos 90", "90s rock hits official audio", "Década na busca"),
            _mix("rock-2000s", "Rock anos 2000", "2000s rock official audio", "Década na busca"),
            _mix("rock-2010s", "Rock anos 2010", "2010s rock official audio", "Década na busca"),
            _mix("rock-br", "Rock BR", "rock brasileiro official audio"),
            _mix("metal", "Metal", "heavy metal official audio"),
            _mix("punk", "Punk", "punk rock official audio"),
        ],
    },
    {
        "id": "pop",
        "label": "Pop",
        "mixes": [
            _mix("pop-hits", "Pop hits", "pop hits official audio"),
            _mix("pop-80s", "Pop anos 80", "80s pop hits official audio", "Década na busca"),
            _mix("pop-90s", "Pop anos 90", "90s pop hits official audio", "Década na busca"),
            _mix("pop-2000s", "Pop anos 2000", "2000s pop official audio", "Década na busca"),
            _mix("pop-2010s", "Pop anos 2010", "2010s pop official audio", "Década na busca"),
            _mix("pop-br", "Pop BR", "pop brasileiro official audio"),
            _mix("indie-pop", "Indie pop", "indie pop official audio"),
            _mix("k-pop", "K-pop", "kpop official audio"),
        ],
    },
    {
        "id": "hiphop",
        "label": "Hip-hop & R&B",
        "mixes": [
            _mix("hiphop-classico", "Hip-hop clássico", "90s hip hop official audio"),
            _mix("hiphop-2000s", "Hip-hop 2000", "2000s hip hop official audio", "Década na busca"),
            _mix("trap", "Trap", "trap official audio"),
            _mix("rap-br", "Rap BR", "rap brasileiro official audio"),
            _mix("rnb", "R&B", "r&b official audio"),
            _mix("soul", "Soul", "soul music official audio"),
        ],
    },
    {
        "id": "eletronica",
        "label": "Eletrônica",
        "mixes": [
            _mix("edm", "EDM", "edm official audio"),
            _mix("house", "House", "house music official audio"),
            _mix("techno", "Techno", "techno official audio"),
            _mix("trance", "Trance", "trance official audio"),
            _mix("eletronica-2000s", "Eletrônica 2000", "2000s electronic official audio"),
            _mix("eletronica-br", "Eletrônica BR", "eletronica brasileira official audio"),
            _mix("lofi", "Lo-fi", "lofi hip hop official audio"),
        ],
    },
    {
        "id": "mpb",
        "label": "MPB",
        "mixes": [
            _mix("mpb-classicos", "MPB clássicos", "mpb classicos official audio"),
            _mix("mpb-contemporanea", "MPB hoje", "mpb brasileira official audio"),
            _mix("bossa-nova", "Bossa nova", "bossa nova official audio"),
            _mix("samba", "Samba", "samba brasileiro official audio"),
            _mix("choro", "Choro", "choro brasileiro official audio"),
        ],
    },
    {
        "id": "sertanejo",
        "label": "Sertanejo",
        "mixes": [
            _mix("sertanejo-universitario", "Universitário", "sertanejo universitario official audio"),
            _mix("sertanejo-raiz", "Raiz", "sertanejo raiz official audio"),
            _mix("sertanejo-modao", "Modão", "modao sertanejo official audio"),
            _mix("sertanejo-90s", "Anos 90", "sertanejo anos 90 official audio", "Década na busca"),
            _mix("sertanejo-2000s", "Anos 2000", "sertanejo anos 2000 official audio", "Década na busca"),
            _mix("sertanejo-2010s", "Anos 2010", "sertanejo 2010 official audio", "Década na busca"),
            _mix("sertanejo-romantico", "Romântico", "sertanejo romantico official audio"),
            _mix("sertanejo-duplas", "Duplas clássicas", "dupla sertaneja classicos official audio"),
        ],
    },
    {
        "id": "pagode-funk",
        "label": "Pagode & funk",
        "mixes": [
            _mix("pagode", "Pagode", "pagode official audio"),
            _mix("pagode-90s", "Pagode anos 90", "pagode anos 90 official audio", "Década na busca"),
            _mix("samba-enredo", "Samba-enredo", "samba enredo official audio"),
            _mix("funk", "Funk carioca", "funk carioca official audio"),
            _mix("funk-melody", "Funk melody", "funk melody official audio"),
            _mix("funk-br-hits", "Funk hits", "brazilian funk official audio"),
        ],
    },
    {
        "id": "forro-regional",
        "label": "Forró & regional",
        "mixes": [
            _mix("forro", "Forró pé de serra", "forro pe de serra official audio"),
            _mix("forro-eletronico", "Forró eletrônico", "forro eletronico official audio"),
            _mix("axe", "Axé", "axe bahia official audio"),
            _mix("brega", "Brega", "brega official audio"),
        ],
    },
    {
        "id": "gospel-br",
        "label": "Gospel",
        "mixes": [
            _mix("gospel-br", "Gospel BR", "gospel brasileiro official audio"),
            _mix("gospel-louvor", "Louvor", "louvor gospel official audio"),
            _mix("gospel-adoracao", "Adoração", "adoracao gospel official audio"),
        ],
    },
    {
        "id": "decadas",
        "label": "Por década",
        "mixes": [
            _mix("anos-70", "Anos 70", "70s hits official audio", "Década na busca"),
            _mix("anos-80", "Anos 80", "80s hits official audio", "Década na busca"),
            _mix("anos-90", "Anos 90", "90s hits official audio", "Década na busca"),
            _mix("anos-2000", "Anos 2000", "2000s hits official audio", "Década na busca"),
            _mix("anos-2010", "Anos 2010", "2010s hits official audio", "Década na busca"),
        ],
    },
    {
        "id": "mundo",
        "label": "Mundo & outros",
        "mixes": [
            _mix("latin", "Latin", "latin pop official audio"),
            _mix("reggae", "Reggae", "reggae official audio"),
            _mix("jazz", "Jazz", "jazz official audio"),
            _mix("blues", "Blues", "blues official audio"),
            _mix("country", "Country", "country music official audio"),
            _mix("reggaeton", "Reggaeton", "reggaeton official audio"),
            _mix("afrobeat", "Afrobeat", "afrobeats official audio"),
        ],
    },
]


def _all_mixes_raw() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cat in MIX_CATEGORIES:
        out.extend(cat["mixes"])
    return out


def mix_for_client(mix: dict[str, Any]) -> dict[str, Any]:
    from app.mix_covers import enrich_mix_dict

    out = {k: v for k, v in mix.items() if k != "publishedAfterDays"}
    if mix.get("filterMode") == "upload_date" and mix.get("publishedAfterDays"):
        dt = datetime.now(timezone.utc) - timedelta(days=int(mix["publishedAfterDays"]))
        out["publishedAfter"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return enrich_mix_dict(out)


def list_mix_categories() -> list[dict[str, Any]]:
    return [
        {
            "id": cat["id"],
            "label": cat["label"],
            "mixes": [mix_for_client(m) for m in cat["mixes"]],
        }
        for cat in MIX_CATEGORIES
    ]


def list_mixes() -> list[dict[str, Any]]:
    return [mix_for_client(m) for m in _all_mixes_raw()]


def get_mix(mix_id: str) -> dict[str, Any] | None:
    for mix in _all_mixes_raw():
        if mix["id"] == mix_id:
            return mix
    return None
