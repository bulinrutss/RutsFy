from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    youtube_api_key: str = ""
    # 2ª, 3ª, 4ª… chaves (vírgula ou quebra de linha). Usadas quando a principal esgota cota.
    youtube_api_keys: str = ""
    host: str = "0.0.0.0"
    port: int = 8090
    cors_origins: str = "*"
    # Pasta onde os áudios baixados ficam salvos no servidor.
    # Pode ser relativa (resolvida a partir de backend/) ou absoluta.
    downloads_dir: str = "downloads"
    # Caminho fixo opcional para o binário do yt-dlp.
    # Se vazio, o backend autodetecta (PATH, venv, winget).
    ytdlp_bin: str = ""
    # Netscape cookies (exporte do navegador). Relativo a downloads_dir ou caminho absoluto.
    ytdlp_cookies_file: str = "youtube_cookies.txt"
    # Limite diário de unidades da API de busca (padrão: 10.000)
    youtube_daily_quota: int = 10_000
    # Bloqueia buscas novas (sem cache) se a estimativa restante for menor que isto (search ≈ 100).
    quota_min_remaining_search: int = 120
    # Buscas por conta não têm teto diário. O valor fica só para respostas antigas da API.
    user_search_daily_limit: int = 20
    # E-mails com busca diária ilimitada (separados por vírgula, case-insensitive).
    user_search_unlimited_emails: str = "svbulin@gmail.com"
    user_search_unlimited_nicknames: str = "svbulin"
    # Bitrate do áudio salvo (Opus). 64K é o padrão; 96K se quiser mais qualidade.
    audio_bitrate: str = "64K"
    # Novas faixas acima deste tempo (segundos) não aparecem em busca nem são baixadas.
    max_track_duration_seconds: int = 20 * 60
    # Tamanho máximo do arquivo de áudio salvo (MB). 0 = sem limite automático.
    max_track_file_size_mb: int = 20
    # local = yt-dlp neste servidor; lan_relay = worker na LAN baixa e envia o arquivo.
    download_mode: str = "local"
    lan_download_worker_token: str = ""
    session_cookie_secure: bool = False
    # Ex.: /rutsfy em https://ruts.dev/rutsfy/ — vazio no LAN (raiz).
    base_path: str = Field(
        default="",
        validation_alias=AliasChoices("BASE_PATH", "RUTSFY_BASE_PATH", "base_path"),
    )

    def normalized_base_path(self) -> str:
        p = (self.base_path or "").strip().rstrip("/")
        return p if p.startswith("/") else (f"/{p}" if p else "")

    def cookie_path(self) -> str:
        bp = self.normalized_base_path()
        return bp if bp else "/"


settings = Settings()