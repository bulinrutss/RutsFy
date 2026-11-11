# RutsFy

Player de áudio com conta, biblioteca e catálogo. O site em [https://ruts.dev/rutsfy/](https://ruts.dev/rutsfy/) é um PWA (atalho do Chrome incluso). O app em `android/` é um cliente nativo (Kotlin, Compose, Media3) da mesma API.

O catálogo (busca, Explorar, prateleiras) vem da API pública do Deezer: gêneros, artistas, álbuns e playlists. O Deezer não entrega o áudio. Ao tocar uma faixa nova, o backend acha um vídeo correspondente no YouTube com o yt-dlp, baixa em Opus e passa a servir o arquivo do disco. Faixas já salvas tocam sem baixar de novo.

## O que o app faz

- **Conta:** apelido e senha, sessão em cookie HttpOnly (30 dias, uma sessão ativa por login). Perfil, avatar e, para admin, usuários e estatísticas.
- **Biblioteca:** músicas salvas na conta, playlists do usuário e atalhos de artista, álbum ou playlist.
- **Explorar:** lançamentos, gêneros, playlists e faixas em alta (Deezer).
- **Busca:** artista, álbum ou faixa no catálogo Deezer. A busca antiga da YouTube Data API (`/api/search`) continua no backend para canal e mixes.
- **Recentes:** histórico de reprodução da conta.
- **Player:** fila, capa, notificação e tela bloqueada no Android.
- **Limites de faixa nova:** mais de 20 minutos não baixa (o que já está no disco continua). Com `MAX_TRACK_FILE_SIZE_MB` (padrão 20), arquivo maior entra em `download_blocklist.json` e não tenta de novo.

## Onde roda

| Onde | URL | Como sobe |
|------|-----|-----------|
| Produção | [https://ruts.dev/rutsfy/](https://ruts.dev/rutsfy/) | `python scripts/deploy_oracle.py` |
| Máquina local | `http://127.0.0.1:8090` | uvicorn, abaixo |
| LAN `192.168.0.5` | legado, congelado | só `docker compose` antigo; não usar no dia a dia |

Produção é a API no Docker (`docker-compose.prod.yml`), escutando em `127.0.0.1:8090`, com nginx na frente em `/rutsfy`. `BASE_PATH=/rutsfy` e cookie de sessão seguro entram no deploy.

## Desenvolvimento local

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8090
```

Preencha `YOUTUBE_API_KEY` no `.env` se for usar mixes ou a busca da Data API. O catálogo Deezer não precisa dessa chave. `DOWNLOAD_MODE=local` baixa com yt-dlp nesta máquina.

## Áudio em produção

A Oracle baixa pouco do YouTube (IP de datacenter costuma cair no anti-bot). O modo usado lá é `DOWNLOAD_MODE=lan_relay`: a API enfileira o job e um worker na máquina de casa baixa com yt-dlp, envia o `.opus` e apaga a cópia local.

1. No `.env` de produção: `DOWNLOAD_MODE=lan_relay` e `LAN_DOWNLOAD_WORKER_TOKEN` (segredo longo, o mesmo valor em `WORKER_TOKEN` no worker).
2. `python scripts/deploy_oracle.py` (atalho: `python scripts/deploy.py`). Host e chave SSH ficam no script, fora deste arquivo.
3. Cookies na máquina de casa, se o yt-dlp pedir login: `python scripts/sync_cookies_to_lan.py` (`LAN_SSH_HOST`, padrão `192.168.0.4`).
4. Instalar o worker (senha SSH em `LAN_SSH_PASSWORD` ou em `senha.txt` na raiz, que não vai para o git):

```powershell
$env:LAN_SSH_PASSWORD="..."
$env:WORKER_TOKEN="<mesmo LAN_DOWNLOAD_WORKER_TOKEN>"
python scripts/install_lan_worker.py
```

5. IP fixo e serviço no boot: `python scripts/setup_lan_vps_boot.py` (com `LAN_SSH_PASSWORD`). Unit `systemd` system-wide: `rutsfy-worker`.
6. Log: `journalctl -u rutsfy-worker -f`.

Teste no PC, sem instalar na VM: `python scripts/lan_download_worker.py` (com `WORKER_TOKEN` e, se precisar, `RUTSFY_API_BASE`).

Fila presa (job `claimed` órfão): `python scripts/requeue_stale_relay.py`. O worker também se recupera sozinho: heartbeat a cada 30s, lease de 3 minutos sem sinal, e ao subir devolve os próprios `claimed` para `pending`.

Só o script do worker, depois de mudar `scripts/lan_download_worker.py`: `python scripts/push_lan_worker.py`.

Copiar de novo músicas e dados da LAN para a Oracle: `python scripts/migrate_lan_to_oracle_direct.py`.

## Cookies do YouTube

Quando o download roda na própria VPS (`DOWNLOAD_MODE=local`), o YouTube pede sessão. Isso não é cota da API: a busca no Deezer pode funcionar e o download falhar.

1. No PC, logado no YouTube, abra um vídeo por alguns segundos.
2. Extensão **Get cookies.txt LOCALLY** → exportar **neste site** (o arquivo precisa ter `LOGIN_INFO` e `__Secure-1PSID`).
3. Validar e enviar:

```bash
python scripts/upload_youtube_cookies.py youtube_cookies.txt
```

Se faltar cookie de login, o script avisa e não envia. Reinício na Oracle, se precisar: `docker compose -f docker-compose.prod.yml restart sound-api`.

Renovação no Windows (a cada 3 dias): `scripts/install_cookies_upload_scheduled_task.ps1`. Teste manual: `python scripts/renew_and_upload_youtube_cookies.py`. Com o navegador fechado o yt-dlp lê o perfil; se falhar, o próximo ciclo usa o export da extensão.

No modo `lan_relay` o download pesado fica na máquina de casa; os cookies vão para lá (`sync_cookies_to_lan.py`), não para o IP da Oracle.

## App Android

Cliente da API de produção (`https://ruts.dev/rutsfy`). Mesma conta, biblioteca, catálogo Deezer e áudio em `/api/download`, com notificação e tela bloqueada. APK de debug, assinado com a chave de debug — uso próprio, não Play Store.

Build e OTA sem Android Studio (na primeira vez o script instala JDK 17 e o SDK em `.android-sdk/`):

```powershell
python scripts/build_android_apk.py --deploy
```

Só o SDK: `powershell -ExecutionPolicy Bypass -File scripts/setup_android_build.ps1`.

O Gradle grava `backend/static/app/rutsfy.apk` e `version.json`. O deploy manda os dois para o servidor. O app compara `versionCode` e pede para instalar quando sobe.

Manual: Android Studio → **Build APK(s)**, ou `adb install` no `rutsfy.apk`.

## Chave da YouTube Data API

Serve para mixes, vídeos de canal e `/api/search`. O Explorar e a busca do app usam o Deezer e não gastam essa cota. Resolver uma faixa do catálogo também não usa `search.list`.

1. [Google Cloud Console](https://console.cloud.google.com/) → ative **YouTube Data API v3**.
2. Crie uma API key e coloque em `YOUTUBE_API_KEY` no `backend/.env`. O deploy de produção lê esse arquivo.
3. Reserva: `YOUTUBE_API_KEYS=segunda,terceira`. Ao esgotar a principal, usa a próxima. `/api/quota` mostra `apiKeyCount` e uso por `keyId`.

## O que não entra no git

- `backend/.env` e qualquer `.env` com chave ou token
- `senha.txt`
- `caddy/certs/*.key` (a chave privada TLS da LAN)
- `backend/downloads/` (áudios, `rutsfy.db`, cookies, cache)
- APK gerado e `backend/static/app/version.json`
