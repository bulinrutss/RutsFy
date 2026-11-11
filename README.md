# RutsFy

Player web — biblioteca, busca e streaming de áudio. O site e o atalho do Chrome continuam iguais. O app Android em `android/` é um cliente nativo (Kotlin + Media3) da mesma API.

## App Android (APK)

O projeto não substitui o player do navegador. Ele entra com a mesma conta, lê a biblioteca e o catálogo, pede o áudio em `/api/download` e toca com notificação e tela bloqueada.

**Build + OTA (sem Android Studio):** na 1ª vez instala JDK 17 e SDK em `.android-sdk/`; depois só:

```powershell
python scripts/build_android_apk.py --deploy
```

Só setup: `powershell -ExecutionPolicy Bypass -File scripts/setup_android_build.ps1`

O Gradle grava `backend/static/app/rutsfy.apk` e `version.json`. O deploy envia ao servidor; o app no celular baixa e pede instalar quando o `versionCode` sobe.

Alternativa manual: Android Studio → **Build APK(s)**, ou `adb install …/rutsfy.apk`.

A API apontada no app é `https://ruts.dev/rutsfy`. APK de debug — suficiente para uso próprio; Play Store exige keystore release.

## Ambientes

| Onde | URL | Deploy |
|------|-----|--------|
| **Produção** | [https://ruts.dev/rutsfy/](https://ruts.dev/rutsfy/) | `python scripts/deploy_oracle.py` |
| **Local** | `http://127.0.0.1:8090` | dev abaixo |
| LAN `192.168.0.5` | legado, congelado | não atualizar (só `--lan-legacy` se emergência) |

## Desenvolvimento local

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # ou cp no Linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

Ou Docker na máquina (sem bind na LAN):

```bash
docker compose up -d --build
```

## Deploy produção (Oracle)

Chave SSH: `Downloads/hosdt key/ssh-key-2026-09-01.key` (ubuntu@147.15.80.246).

```bash
python scripts/deploy_oracle.py
# equivalente:
python scripts/deploy.py
```

Sincronizar **músicas/dados** da LAN para Oracle (cópia direta, rápida):

```bash
python scripts/migrate_lan_to_oracle_direct.py
```

## Downloads via LAN (recomendado)

A Oracle baixa pouco do YouTube; o worker na **VPS de casa** faz o yt-dlp, envia o `.opus` para a Oracle e apaga o arquivo local.

1. Em `backend/.env` (produção): `DOWNLOAD_MODE=lan_relay`, `LAN_DOWNLOAD_WORKER_TOKEN=<segredo longo>`, e opcional `MAX_TRACK_FILE_SIZE_MB=20` (faixas maiores não baixam e entram em `download_blocklist.json`).
2. Deploy: `python scripts/deploy_oracle.py`
3. Cookies na LAN: `python scripts/sync_cookies_to_lan.py` (padrão `LAN_SSH_HOST=192.168.0.4`).
4. Instalar worker (senha **não** vai pro git — use env):
   ```powershell
   $env:LAN_SSH_PASSWORD="..."
   $env:WORKER_TOKEN="<mesmo LAN_DOWNLOAD_WORKER_TOKEN>"
   python scripts/install_lan_worker.py
   ```
5. IP fixo **192.168.0.4** + worker no boot (após queda de energia):
   ```powershell
   $env:LAN_SSH_PASSWORD="..."
   python scripts/setup_lan_vps_boot.py
   ```
   (Netplan estático na VM + serviço `systemd` system-wide `rutsfy-worker`.)
6. Logs na LAN: `journalctl -u rutsfy-worker -f` (ou `--user` se ainda usar unit antiga)

Teste manual no PC: `python scripts/lan_download_worker.py` (com `WORKER_TOKEN` e `RUTSFY_API_BASE`).

**Se a fila travar** (spinner longo, job `claimed` órfão após restart): `python scripts/requeue_stale_relay.py` — libera jobs e reinicia o worker. O sistema também se recupera sozinho: heartbeat a cada 30s, lease de 3 min sem sinal, e ao subir o worker devolve os próprios `claimed` para `pending`.

Atualizar só o script do worker na LAN após mudanças: `python scripts/push_lan_worker.py`

## Downloads na VPS (YouTube anti-bot)

Na Oracle o YouTube costuma bloquear IP de datacenter (`Sign in to confirm you're not a bot`).
**Não é cota da API** — busca pode funcionar e o download falhar. Com `DOWNLOAD_MODE=lan_relay`, o download pesado fica na LAN.

1. No PC, **logado** no YouTube: abra [youtube.com](https://www.youtube.com), assista qualquer vídeo alguns segundos.
2. Extensão **Get cookies.txt LOCALLY** → exportar **neste site** (precisa ter `LOGIN_INFO` e `__Secure-1PSID` no arquivo).
3. Valide antes de enviar:
   ```bash
   python scripts/upload_youtube_cookies.py youtube_cookies.txt
   ```
   (Se faltar cookie de login, o script avisa e não envia.)
   O script valida e envia; se faltar login no arquivo, ele para com aviso.
5. Reinicie a API se precisar: `docker compose -f docker-compose.prod.yml restart sound-api` (no host Oracle).

### Renovação automática (Windows, a cada 3 dias)

Instale a tarefa agendada (exporta do Chrome/Edge, valida, envia e reinicia a API):

```powershell
& "E:\GitHub\sound\scripts\install_cookies_upload_scheduled_task.ps1"
```

Teste manual: `backend\.venv\Scripts\python.exe scripts\renew_and_upload_youtube_cookies.py`  
Log: `C:\Users\svbul\Downloads\cokies\rutsfy-cookies-upload.log`

Às 03:00 funciona melhor com o navegador **fechado** (yt-dlp lê o perfil). Se falhar, exporte com a extensão e o próximo ciclo usa o arquivo em `cokies\`.

Faixas que **já estão** em `/data/downloads` tocam sem baixar de novo (~219 arquivos migrados da LAN).

## Chave da API de busca

1. [Google Cloud Console](https://console.cloud.google.com/) → ative **YouTube Data API v3**.
2. Crie **API key** → `YOUTUBE_API_KEY` no `backend/.env` (local e no servidor via deploy).
3. **Reserva de cota:** chaves extras em `YOUTUBE_API_KEYS=segunda,terceira,quarta` (mesmo `.env`). Ao esgotar a principal, usa a próxima. `/api/quota` mostra `apiKeyCount` e uso por `keyId` (hash).

## Segurança

- Não commite `senha.txt` nem `.env`.
- Produção usa `BASE_PATH=/rutsfy` e cookies seguros (configurado no deploy Oracle).
