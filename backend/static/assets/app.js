function rutUrl(path) {
  if (path == null || path === "") return path;
  const s = String(path);
  if (!s.startsWith("/")) return s;
  const base = (window.RUTSFY_BASE || "").replace(/\/$/, "");
  if (!base) return s;
  if (s === base || s.startsWith(`${base}/`)) return s;
  return `${base}${s}`;
}

const BRAND_AVATAR_DEFAULT = "/assets/icons/avatar-default.png?v=3";

const form = document.getElementById("search-form");
const input = document.getElementById("q");
const statusEl = document.getElementById("status");
const statusTextEl = document.getElementById("status-text");
const statusSpinnerEl = document.getElementById("status-spinner");
const globalLoadOverlay = document.getElementById("global-load-overlay");
let globalLoadDepth = 0;

function setGlobalLoading(active) {
  if (active) globalLoadDepth += 1;
  else globalLoadDepth = Math.max(0, globalLoadDepth - 1);
  if (!globalLoadOverlay) return;
  globalLoadOverlay.classList.toggle("hidden", globalLoadDepth === 0);
  globalLoadOverlay.setAttribute("aria-hidden", globalLoadDepth === 0 ? "true" : "false");
}
const userMenuQuotaEl = document.getElementById("user-menu-quota");
const userMenuQuotaDividerEl = document.getElementById("user-menu-quota-divider");
const resultsEl = document.getElementById("results");
const searchCatalogEl = document.getElementById("search-catalog");
const searchTracksLabelEl = document.getElementById("search-tracks-label");
const searchColAlbumEl = document.getElementById("search-col-album");
const historyEl = document.getElementById("history");
const historyCountEl = document.getElementById("history-count");
const libraryEl = document.getElementById("library");
const libraryCountEl = document.getElementById("library-count");
const searchHeading = document.getElementById("search-heading");
const searchSaveShortcut = document.getElementById("search-save-shortcut");
const searchShowMore = document.getElementById("search-show-more");
const npShowMore = document.getElementById("np-show-more");
const homeGreeting = document.getElementById("home-greeting");
const audio = document.getElementById("audio");

const playerSourceBtn = document.getElementById("player-source-btn");
const playerCover = document.getElementById("player-cover");
const shellEl = document.querySelector(".shell");
const playerBar = document.querySelector(".player-bar");
const playerCenter = document.querySelector(".player-center");
const playerExtra = document.querySelector(".player-extra");
const playerNowEl = document.querySelector(".player-now");
const npHeroControls = document.getElementById("np-hero-controls");
const npHeroActions = document.getElementById("np-hero-actions");
const npMinimizeBtn = document.getElementById("np-minimize-btn");
const npHeroCover = document.getElementById("np-hero-cover");
const npHeroCoverEmpty = document.getElementById("np-hero-cover-empty");
const npHeroTitle = document.getElementById("np-hero-title");
const npHeroArtist = document.getElementById("np-hero-artist");
const playerTitle = document.getElementById("player-title");
const playerArtistBtn = document.getElementById("player-artist-btn");
const playerStatus = document.getElementById("player-status");
const btnPlay = document.getElementById("btn-play");
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const btnShuffle = document.getElementById("btn-shuffle");
const btnRepeat = document.getElementById("btn-repeat");
const btnStopQueue = document.getElementById("btn-stop-queue");
const repeatOneBadge = document.getElementById("repeat-one-badge");
const btnLibrary = document.getElementById("btn-library");
const iconPlay = document.getElementById("icon-play");
const iconPause = document.getElementById("icon-pause");
const iconPlaySpinner = document.getElementById("icon-play-spinner");
const seek = document.getElementById("seek");
const seekFillBar = document.getElementById("seek-fill-bar");
const timeCurrent = document.getElementById("time-current");
const timeTotal = document.getElementById("time-total");
const volume = document.getElementById("volume");
const volumeFillBar = document.getElementById("volume-fill-bar");

const authGate = document.getElementById("auth-gate");
const authForm = document.getElementById("auth-form");
const authNickname = document.getElementById("auth-nickname");
const authPassword = document.getElementById("auth-password");
const authError = document.getElementById("auth-error");
const authSubmit = document.getElementById("auth-submit");
const userMenuEl = document.getElementById("user-menu");
const userMenuBtn = document.getElementById("user-menu-btn");
const userMenuName = document.getElementById("user-menu-name");
const userMenuPanel = document.getElementById("user-menu-panel");
const userAvatarImg = document.getElementById("user-avatar-img");
const userAvatarInitial = document.getElementById("user-avatar-initial");

const accountModal = document.getElementById("account-modal");
const accountForm = document.getElementById("account-form");
const accountDisplayName = document.getElementById("account-display-name");
const accountCurrentPassword = document.getElementById("account-current-password");
const accountNewPassword = document.getElementById("account-new-password");
const accountAvatarFile = document.getElementById("account-avatar-file");
const accountAvatarRemove = document.getElementById("account-avatar-remove");
const accountAvatarImg = document.getElementById("account-avatar-img");
const accountAvatarInitial = document.getElementById("account-avatar-initial");
const accountFormError = document.getElementById("account-form-error");
const accountFormOk = document.getElementById("account-form-ok");
const accountModalCancel = document.getElementById("account-modal-cancel");

const customizeModal = document.getElementById("customize-modal");
const themePicker = document.getElementById("theme-picker");
const themeCustomPanel = document.getElementById("theme-custom-panel");
const themeCustomAccent = document.getElementById("theme-custom-accent");
const customizeModalCancel = document.getElementById("customize-modal-cancel");
const customizeModalSave = document.getElementById("customize-modal-save");

const exploreSections = document.getElementById("explore-sections");
const deezerShelvesEl = document.getElementById("deezer-shelves");
const deezerTracksEl = document.getElementById("deezer-tracks");
const deezerStatusEl = document.getElementById("deezer-status");
const deezerBarEl = document.getElementById("deezer-bar");
const deezerTitleEl = document.getElementById("deezer-title");
const deezerCoverEl = document.getElementById("deezer-cover");
const deezerSubtitleEl = document.getElementById("deezer-subtitle");
const searchEntityCover = document.getElementById("search-entity-cover");
const searchEntitySub = document.getElementById("search-entity-sub");
const deezerTracksLabelEl = document.getElementById("deezer-tracks-label");
const deezerTrackHeadEl = document.getElementById("deezer-track-head");
const deezerResolvePromises = new Map();
let deezerLoadSeq = 0;
const exploreCatFooter = document.getElementById("explore-cat-footer");
const freeListWrap = document.getElementById("free-list-wrap");
const freeListEl = document.getElementById("free-list");
const freeStatusEl = document.getElementById("free-status");
const freeSearchForm = document.getElementById("free-search-form");
const freeSearchInput = document.getElementById("free-q");
const freeBrowseBar = document.getElementById("free-browse-bar");
const freeBrowseBack = document.getElementById("free-browse-back");
const freeBrowseTitle = document.getElementById("free-browse-title");
const navViewBack = document.getElementById("nav-view-back");
const freeShowMore = document.getElementById("free-show-more");
const homeMainBlock = document.getElementById("home-main-block");
const homeSections = document.getElementById("home-sections");
const homeServerTracks = document.getElementById("home-server-tracks");
const serverLibraryEl = document.getElementById("server-library");
const serverLibraryCountEl = document.getElementById("server-library-count");
const nowPlayingList = document.getElementById("now-playing-list");
const nowPlayingSub = document.getElementById("now-playing-sub");
const npScrollToPlayingBtn = document.getElementById("np-scroll-to-playing");

const RECENT_SEARCHES_KEY = "rutsfy_recent_searches";
const USER_VOLUME_KEY = "rutsfy_volume";
const USER_LAST_LISTEN_KEY = "rutsfy_last_listen";
const LEGACY_SHARED_STORAGE_KEYS = [USER_LAST_LISTEN_KEY, RECENT_SEARCHES_KEY];
const MAX_RECENT_SEARCHES = 12;
const MAX_SAVED_SHORTCUTS = 48;

function userStorageKey(base) {
  const uid = state.user?.id;
  return uid ? `${base}:u:${uid}` : base;
}

function purgeLegacySharedStorage() {
  try {
    for (const key of LEGACY_SHARED_STORAGE_KEYS) {
      localStorage.removeItem(key);
    }
  } catch {
    /* silencioso */
  }
}

function clearRutsfyStorage() {
  try {
    const keys = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (key && key.startsWith("rutsfy_")) keys.push(key);
    }
    keys.forEach((key) => localStorage.removeItem(key));
  } catch {
    /* silencioso */
  }
  try {
    if (window.caches && typeof caches.keys === "function") {
      void caches.keys().then((names) => {
        names.forEach((name) => {
          void caches.delete(name);
        });
      });
    }
  } catch {
    /* silencioso */
  }
}

function resetClientUserData() {
  deezerLoadSeq += 1;
  homeDiscoverSeq += 1;
  expandQueueSeq += 1;
  state.savedShortcuts = [];
  state.historyItems = [];
  state.libraryItems = [];
  state.serverLibraryItems = [];
  state.history.clear();
  state.library.clear();
  state.current = null;
  state.playingId = null;
  state.pendingPlayVideoId = null;
  state.rowLoadingVideoId = null;
  state.rowLoadingKey = null;
  state.isPlaying = false;
  state.queue = [];
  state.queueIndex = -1;
  state.playOrder = [];
  state.queueSource = null;
  state.pendingResumeTime = 0;
  state.pendingResumeVideoId = null;
  state.playbackContext = null;
  state.catalogOrigin = null;
  state.playedAlbumIds = null;
  state.continuedArtistIds = null;
  state.continuationInFlight = false;
  state.deezerStack = [];
  state.deezerTracks = [];
  state.searchCatalog = [];
  state.searchQuery = "";
  state.searchMixId = null;
  state.searchVisibleCount = 0;
  state.searchNextPageToken = null;
  resetNavigationReturnStack();
  if (audio) {
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
  }
  if (input) input.value = "";
  document.getElementById("home-discover")?.replaceChildren();
  if (deezerShelvesEl) deezerShelvesEl.innerHTML = "";
  if (deezerTracksEl) deezerTracksEl.innerHTML = "";
  if (deezerTitleEl) deezerTitleEl.textContent = "";
  clearDeezerEntityCover();
  if (deezerStatusEl) deezerStatusEl.textContent = "";
  if (searchCatalogEl) searchCatalogEl.innerHTML = "";
  if (resultsEl) resultsEl.innerHTML = "";
  if (playerTitle) playerTitle.textContent = "Selecione uma música";
  if (playerArtistBtn) {
    playerArtistBtn.textContent = "";
    playerArtistBtn.classList.add("hidden");
  }
  if (playerCover) {
    playerCover.removeAttribute("src");
    playerCover.classList.add("hidden");
  }
  applyTheme("rutsfy");
  applyColorScheme("dark");
  syncDeezerChrome();
  renderBiblioteca([]);
  renderHistory([]);
  renderHomeSections();
  renderNowPlaying();
  updatePlayerSourceLink();
  updateTransportControls();
  setPlayUi(false);
}

const views = {
  home: document.getElementById("view-home"),
  explore: document.getElementById("view-explore"),
  search: document.getElementById("view-search"),
  nowplaying: document.getElementById("view-nowplaying"),
  history: document.getElementById("view-history"),
  admin: document.getElementById("view-admin"),
};

const ON_SERVER_BADGE_TITLE = "Já no servidor — baixar usa o arquivo local";
const MIX_LOADED_BADGE_TITLE =
  "Lista já carregada — catálogo salvo; use Mostrar mais para ver mais faixas";

const FREE_LIST_PAGE = 50;
let freeSearchTimer = null;

let viewBeforeNowPlaying = "home";
let viewBeforeSearch = "home";
let npClosing = false;
let npPull = null;
let viewAnimTimer = 0;

const state = {
  view: "home",
  npFooterPlayer: false,
  queue: [],
  queueIndex: -1,
  playOrder: [],
  queueSource: null,
  shuffle: false,
  repeat: "off",
  historyItems: [],
  libraryItems: [],
  current: null,
  playingId: null,
  pendingPlayVideoId: null,
  /** Faixa em download para tocar — spinner na linha (mesmo com outra tocando). */
  rowLoadingVideoId: null,
  /** dz:{deezerId} ou videoId — marca a linha no clique, antes do resolve. */
  rowLoadingKey: null,
  isPlaying: false,
  isLoading: false,
  history: new Map(),
  library: new Map(),
  seeking: false,
  prefetchGeneration: 0,
  playSession: 0,
  autoAdvanceEnabled: true,
  quotaSnapshot: null,
  searchCatalog: [],
  searchQuery: "",
  searchVisibleCount: 0,
  searchNextPageToken: null,
  searchHydrated: new Set(),
  searchHydrateGen: 0,
  searchLoadingMore: false,
  searchExpandInFlight: false,
  searchMixId: null,
  searchMixCatalogTotal: 0,
  searchChannelId: null,
  searchChannelTitle: null,
  searchPublishedAfter: null,
  searchPublishedBefore: null,
  searchOrder: null,
  exploreCategories: [],
  deezerStack: [],
  deezerTracks: [],
  catalogOrigin: null,
  lastSearchCatalog: null,
  playedAlbumIds: null,
  continuedArtistIds: null,
  continuationInFlight: false,
  freeSections: [],
  freeCatalogTotal: 0,
  freeListItems: [],
  freeListTotal: 0,
  freeListOffset: 0,
  freeBrowseCategoryId: null,
  freeBrowseLabel: "",
  freeFilterQuery: "",
  freeLoading: false,
  loadedMixIds: new Set(),
  serverVideoIds: new Set(),
  downloadBlocklistIds: new Set(),
  /** Ocultos nesta busca (ex.: longos rejeitados antes de hidratar duração). */
  catalogHiddenVideoIds: new Set(),
  maxDownloadFileMb: 12,
  serverLibraryItems: [],
  mixCoverPreviews: {},
  playbackContext: null,
  pendingResumeTime: 0,
  pendingResumeVideoId: null,
  user: null,
  authMode: "login",
  themeId: "rutsfy",
  themeCustom: {},
  colorScheme: "dark",
  customizeSchemeDraft: "dark",
  userMenuOpen: false,
  pendingAvatarFile: null,
  customizeThemeDraft: "rutsfy",
  savedShortcuts: [],
};

const PREFETCH_AHEAD = 2;
const AUTO_PREFETCH_MAX_DURATION_SEC = 20 * 60;
const SEARCH_INITIAL_VISIBLE = 10;
const SEARCH_SHOW_MORE_STEP = 20;
const SEARCH_API_BATCH = 25;
const LAZY_HYDRATE_BATCH = 12;
const LAZY_HYDRATE_DEBOUNCE_MS = 60;
const LAZY_HYDRATE_ROOT_MARGIN_PX = 280;
const DOWNLOAD_MAX_ATTEMPTS = 2;
const MAX_CONSECUTIVE_PLAY_FAILURES = 20;
const DOWNLOAD_PRIORITY_PLAY_BASE = 1_000_000;
const DOWNLOAD_PRIORITY_PREFETCH = 100;

let consecutivePlayFailures = 0;
let holdMediaSessionPlaying = false;
let userPauseRequested = false;
let ignoreAutoPauseUntil = 0;
let audioHeardSeconds = 0;
let trackEndConsumedToken = -1;
let trackEndTimer = 0;
let primeToken = 0;
let primeAbort = null;
let primedNext = null;
let activeBlobUrl = null;

/** Uma fila no cliente: prioriza a faixa que você acabou de escolher para tocar. */
const _downloadWaiters = new Map();
let _downloadPumpRunning = false;
/** @type {{ videoId: string, priority: number, abortController: AbortController } | null} */
let _inFlightDownload = null;

function rejectDownloadWaiters(waiters, err) {
  for (const w of waiters) {
    try {
      w.reject(err);
    } catch {
      /* já resolvido */
    }
  }
}

function cancelDownloadWaitersBelowPriority(minPriority) {
  for (const [vid, waiters] of [..._downloadWaiters.entries()]) {
    const removed = waiters.filter((w) => (w.priority ?? 0) < minPriority);
    const kept = waiters.filter((w) => (w.priority ?? 0) >= minPriority);
    if (removed.length) rejectDownloadWaiters(removed, new DOMException("Download cancelado", "AbortError"));
    if (kept.length) _downloadWaiters.set(vid, kept);
    else _downloadWaiters.delete(vid);
  }
}

function hasBackgroundDownloadActivity() {
  for (const waiters of _downloadWaiters.values()) {
    if (waiters.some((w) => (w.priority ?? 0) < DOWNLOAD_PRIORITY_PLAY_BASE)) return true;
  }
  if (
    _inFlightDownload &&
    _inFlightDownload.priority < DOWNLOAD_PRIORITY_PLAY_BASE &&
    _downloadPumpRunning
  ) {
    return true;
  }
  return false;
}

function queueCanAutoAdvance() {
  if (!state.queue.length || state.queueIndex < 0) return false;
  if (state.repeat === "one" || state.repeat === "all") return true;
  const order = state.playOrder.length ? state.playOrder : state.queue.map((_, i) => i);
  const pos = order.indexOf(state.queueIndex);
  return pos >= 0 && pos < order.length - 1;
}

function updateStopQueueButton() {
  if (!btnStopQueue) return;
  const show =
    state.autoAdvanceEnabled &&
    (state.isLoading || hasBackgroundDownloadActivity() || queueCanAutoAdvance());
  btnStopQueue.classList.toggle("hidden", !show);
  btnStopQueue.disabled = !show;
}

function stopQueueActivity() {
  state.autoAdvanceEnabled = false;
  state.prefetchGeneration += 1;
  holdMediaSessionPlaying = false;
  clearPrimedNext();
  cancelDownloadWaitersBelowPriority(DOWNLOAD_PRIORITY_PLAY_BASE);

  if (_inFlightDownload && _inFlightDownload.priority < DOWNLOAD_PRIORITY_PLAY_BASE) {
    _inFlightDownload.abortController.abort();
  }

  if (state.isLoading && _inFlightDownload?.priority >= DOWNLOAD_PRIORITY_PLAY_BASE) {
    state.playSession += 1;
    _inFlightDownload.abortController.abort();
    state.pendingPlayVideoId = null;
    state.rowLoadingVideoId = null;
    state.rowLoadingKey = null;
    syncPlayingIdFromAudio();
    setPlayLoading(false);
    updateTrackRowLoadingStates();
    setPlayerStatus("Download cancelado");
  } else if (state.isPlaying && !audio.paused) {
    setPlayerStatus("Sem avanço automático");
    setTimeout(() => {
      if (!state.isLoading && playerStatus?.textContent === "Sem avanço automático") {
        setPlayerStatus("");
      }
    }, 2500);
  } else {
    setPlayerStatus("Downloads e fila automática parados");
    setTimeout(() => setPlayerStatus(""), 2500);
  }

  updateStopQueueButton();
}

function videoIdFromAudioSrc() {
  const src = audio.currentSrc || audio.src;
  if (!src) return null;
  try {
    let pathname = new URL(src, window.location.href).pathname;
    const base = (window.RUTSFY_BASE || "").replace(/\/$/, "");
    if (base && pathname.startsWith(base)) {
      pathname = pathname.slice(base.length) || "/";
    }
    const m = pathname.match(/\/api\/downloads\/([^/?#.]+)/i);
    return m ? decodeURIComponent(m[1]) : null;
  } catch {
    return null;
  }
}

/** Faixa audível na UI — prioriza o videoId do elemento audio. */
function getUiCurrentVideoId() {
  const audible = videoIdFromAudioSrc();
  if (audible) return audible;
  return state.pendingPlayVideoId || state.playingId;
}

function syncPlayingIdFromAudio() {
  const audible = videoIdFromAudioSrc();
  if (!audible) return;
  if (state.pendingPlayVideoId && state.pendingPlayVideoId !== audible) {
    return;
  }
  state.playingId = audible;
  if (!state.pendingPlayVideoId || state.pendingPlayVideoId === audible) {
    state.pendingPlayVideoId = null;
  }
  alignQueueIndexToVideoId(audible);
  const idx = state.queueIndex;
  if (idx >= 0) {
    const qItem = state.queue[idx];
    if (qItem) {
      state.current = { ...state.current, ...qItem };
      updatePlayerBar(state.current);
    }
  }
  highlightPlayingRows();
  updateTransportControls();
}

function isActivePlaybackSession(session) {
  return session === state.playSession;
}

function shouldDrivePlaybackUi(videoId, session) {
  return isActivePlaybackSession(session) && state.playingId === videoId;
}

function _flushDownloadWaiters(videoId, err, data) {
  const list = _downloadWaiters.get(videoId) || [];
  _downloadWaiters.delete(videoId);
  for (const w of list) {
    if (err) w.reject(err);
    else w.resolve(data);
  }
}

function scheduleDownload(videoId, item, priority) {
  const hist = state.history.get(videoId);
  const knownUrl = isServerAudioUrl(hist?.url)
    ? hist.url
    : isServerAudioUrl(item?.url)
      ? item.url
      : "";
  if (knownUrl) {
    return Promise.resolve({ ...item, ...hist, url: knownUrl, alreadyExisted: true });
  }

  if (
    priority >= DOWNLOAD_PRIORITY_PLAY_BASE &&
    _inFlightDownload &&
    _inFlightDownload.videoId !== videoId &&
    _inFlightDownload.priority < DOWNLOAD_PRIORITY_PLAY_BASE
  ) {
    _inFlightDownload.abortController.abort();
  }

  return new Promise((resolve, reject) => {
    const list = _downloadWaiters.get(videoId) || [];
    list.push({ resolve, reject, priority: priority || 0, item });
    list.sort((a, b) => b.priority - a.priority);
    _downloadWaiters.set(videoId, list);
    void _pumpDownloadQueue();
  });
}

async function _pumpDownloadQueue() {
  if (_downloadPumpRunning) return;
  _downloadPumpRunning = true;
  try {
    while (_downloadWaiters.size > 0) {
      let pickId = null;
      let pickPriority = -Infinity;
      for (const [vid, waiters] of _downloadWaiters) {
        const top = waiters[0]?.priority ?? 0;
        if (top > pickPriority) {
          pickPriority = top;
          pickId = vid;
        }
      }
      if (!pickId) break;

      const waiters = (_downloadWaiters.get(pickId) || []).slice();
      waiters.sort((a, b) => b.priority - a.priority);
      const item = waiters.find((w) => w.item)?.item;
      let lastError = null;
      let data = null;
      for (let attempt = 1; attempt <= DOWNLOAD_MAX_ATTEMPTS; attempt += 1) {
        const ac = new AbortController();
        _inFlightDownload = { videoId: pickId, priority: pickPriority, abortController: ac };
        try {
          data = await postDownload(pickId, item, ac.signal, pickPriority);
          mergeHistoryEntry(data);
          break;
        } catch (err) {
          if (err?.name === "AbortError") {
            lastError = err;
            break;
          }
          lastError = err;
          if (attempt < DOWNLOAD_MAX_ATTEMPTS) await delay(800);
        } finally {
          if (_inFlightDownload?.abortController === ac) _inFlightDownload = null;
        }
      }
      if (data) {
        _flushDownloadWaiters(pickId, null, data);
        refreshQuota();
      } else {
        _flushDownloadWaiters(
          pickId,
          lastError || new Error("Não foi possível carregar a faixa"),
          null
        );
      }
    }
  } finally {
    _downloadPumpRunning = false;
    if (_downloadWaiters.size > 0) void _pumpDownloadQueue();
  }
}
let lastListenSaveTimer = null;
let prefsSyncTimer = null;

const THEME_PRESETS = {
  rutsfy: {
    id: "rutsfy",
    label: "RutsFy",
    accent: "#3b82f6",
    accentHover: "#60a5fa",
    accentPress: "#2563eb",
  },
  spotify: {
    id: "spotify",
    label: "Spotify",
    accent: "#1ed760",
    accentHover: "#1fdf64",
    accentPress: "#169c46",
  },
  violet: {
    id: "violet",
    label: "Violeta",
    accent: "#8b5cf6",
    accentHover: "#a78bfa",
    accentPress: "#7c3aed",
  },
  ocean: {
    id: "ocean",
    label: "Oceano",
    accent: "#0891b2",
    accentHover: "#22d3ee",
    accentPress: "#0e7490",
  },
  coral: {
    id: "coral",
    label: "Coral",
    accent: "#d2343e",
    accentHover: "#e04852",
    accentPress: "#b82932",
  },
  custom: {
    id: "custom",
    label: "Personalizado",
    accent: "#3b82f6",
    accentHover: "#60a5fa",
    accentPress: "#2563eb",
  },
};

function userDisplayInitial(user) {
  const name = (user?.displayName || user?.nickname || "?").trim();
  const ch = name.charAt(0);
  return ch ? ch.toUpperCase() : "?";
}

function shadeHex(hex, percent) {
  const raw = String(hex || "").replace("#", "");
  if (raw.length !== 6) return hex;
  const num = parseInt(raw, 16);
  let r = (num >> 16) & 0xff;
  let g = (num >> 8) & 0xff;
  let b = num & 0xff;
  const t = percent < 0 ? 0 : 255;
  const p = Math.abs(percent) / 100;
  r = Math.round((t - r) * p + r);
  g = Math.round((t - g) * p + g);
  b = Math.round((t - b) * p + b);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

function applyTheme(themeId, themeCustom = {}) {
  const preset = THEME_PRESETS[themeId] || THEME_PRESETS.rutsfy;
  let accent = preset.accent;
  let hover = preset.accentHover;
  let press = preset.accentPress;
  if (themeId === "custom" && themeCustom.accent) {
    accent = themeCustom.accent;
    hover = shadeHex(accent, 12);
    press = shadeHex(accent, -18);
  }
  document.documentElement.style.setProperty("--green", accent);
  document.documentElement.style.setProperty("--green-hover", hover);
  document.documentElement.style.setProperty("--green-press", press);
  state.themeId = themeId;
  state.themeCustom = themeId === "custom" ? { ...themeCustom } : {};
}

function applyColorScheme(scheme) {
  const mode = scheme === "light" ? "light" : "dark";
  state.colorScheme = mode;
  document.documentElement.dataset.colorScheme = mode;
  const themeMeta = document.getElementById("meta-theme-color");
  if (themeMeta) {
    themeMeta.setAttribute("content", mode === "light" ? "#f5f5f5" : "#121212");
  }
}

function applyThemeFromPrefs(prefs) {
  const themeId = prefs?.themeId && THEME_PRESETS[prefs.themeId] ? prefs.themeId : "rutsfy";
  const themeCustom =
    prefs?.themeCustom && typeof prefs.themeCustom === "object" ? prefs.themeCustom : {};
  applyTheme(themeId, themeCustom);
  applyColorScheme(prefs?.colorScheme === "light" ? "light" : "dark");
}

function selectCustomizeScheme(scheme) {
  state.customizeSchemeDraft = scheme === "light" ? "light" : "dark";
  document.querySelectorAll(".appearance-option").forEach((btn) => {
    const active = btn.dataset.scheme === state.customizeSchemeDraft;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function renderUserAvatar(imgEl, initialEl, user) {
  if (!imgEl || !initialEl) return;
  const fallback = () => {
    imgEl.onerror = null;
    imgEl.src = rutUrl(BRAND_AVATAR_DEFAULT);
    imgEl.classList.remove("hidden");
    initialEl.textContent = "";
    initialEl.classList.add("hidden");
  };
  const url = user?.avatarUrl;
  if (url) {
    imgEl.onerror = fallback;
    imgEl.src = url.includes("?") ? url : `${url}?t=${Date.now()}`;
    imgEl.classList.remove("hidden");
    initialEl.textContent = "";
    initialEl.classList.add("hidden");
  } else {
    imgEl.onerror = null;
    fallback();
  }
}

function closeUserMenu() {
  if (!userMenuPanel || !userMenuBtn) return;
  state.userMenuOpen = false;
  userMenuPanel.classList.add("hidden");
  userMenuBtn.setAttribute("aria-expanded", "false");
}

function toggleUserMenu() {
  if (!userMenuPanel || !userMenuBtn) return;
  state.userMenuOpen = !state.userMenuOpen;
  userMenuPanel.classList.toggle("hidden", !state.userMenuOpen);
  userMenuBtn.setAttribute("aria-expanded", state.userMenuOpen ? "true" : "false");
  if (state.userMenuOpen) {
    void refreshQuota();
  }
}

function openModal(el) {
  if (!el) return;
  el.classList.remove("hidden");
}

function closeModal(el) {
  if (!el) return;
  el.classList.add("hidden");
}

function fetchInputUrl(input) {
  if (typeof input === "string") return input;
  if (input instanceof URL) return input.href;
  if (input && typeof input === "object" && typeof input.url === "string") return input.url;
  return "";
}

/** Aplica RUTSFY_BASE a paths relativos e a URLs absolutas same-origin (ex.: new URL("/api/…")). */
function resolveFetchUrl(url) {
  if (!url) return url;
  const s = String(url);
  if (s.startsWith("/")) return rutUrl(s);
  const base = (window.RUTSFY_BASE || "").replace(/\/$/, "");
  if (!base) return s;
  try {
    const parsed = new URL(s, window.location.origin);
    if (parsed.origin !== window.location.origin) return s;
    const pathQ = parsed.pathname + parsed.search;
    if (pathQ === base || pathQ.startsWith(`${base}/`)) return parsed.href;
    if (parsed.pathname.startsWith("/api/")) {
      return new URL(rutUrl(pathQ), window.location.origin).href;
    }
  } catch {
    /* ignore */
  }
  return s;
}

function installApiFetch() {
  const native = window.fetch.bind(window);
  window.fetch = async (input, init = {}) => {
    let req = input;
    const url = fetchInputUrl(input);
    const rewritten = resolveFetchUrl(url);
    if (rewritten && rewritten !== url) {
      req = rewritten;
    }
    const resolved = fetchInputUrl(req);
    const isApi = resolved.includes("/api/");
    const isAuthRoute = resolved.includes("/api/auth/");
    const init2 = isApi ? { credentials: "same-origin", ...init } : init;
    const res = await native(req, init2);
    if (isApi && !isAuthRoute && res.status === 401 && state.user) {
      state.user = null;
      updateAuthUserNav();
      showAuthGate(true);
    }
    return res;
  };
}

function apiErrorDetail(data) {
  const d = data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((x) => (x && typeof x === "object" ? x.msg || x.message : x))
      .filter(Boolean)
      .join(". ");
  }
  return "Não foi possível concluir a operação.";
}

function showAuthGate(focusEmail = false) {
  if (authGate) {
    authGate.classList.remove("is-booting");
    authGate.classList.remove("hidden");
    authGate.setAttribute("aria-hidden", "false");
  }
  document.body.classList.add("auth-locked");
  if (focusEmail && authNickname) authNickname.focus();
}

function showAuthBoot() {
  if (authGate) {
    authGate.classList.remove("hidden");
    authGate.classList.add("is-booting");
    authGate.setAttribute("aria-hidden", "false");
  }
  document.body.classList.add("auth-locked");
}

function hideAuthGate() {
  if (authGate) {
    authGate.classList.remove("is-booting");
    authGate.classList.add("hidden");
    authGate.setAttribute("aria-hidden", "true");
  }
  document.body.classList.remove("auth-locked");
}

function updateAuthUserNav() {
  if (!userMenuEl || !userMenuName) return;
  closeUserMenu();
  if (state.user) {
    userMenuEl.classList.remove("hidden");
    userMenuName.textContent = state.user.displayName || state.user.nickname || "Conta";
    renderUserAvatar(userAvatarImg, userAvatarInitial, state.user);
    const showAdmin = Boolean(state.user.isAdmin);
    document.getElementById("user-menu-admin")?.classList.toggle("hidden", !showAdmin);
    document.getElementById("user-menu-admin-divider")?.classList.toggle("hidden", !showAdmin);
  } else {
    userMenuEl.classList.add("hidden");
    userMenuName.textContent = "";
    renderUserAvatar(userAvatarImg, userAvatarInitial, null);
    document.getElementById("user-menu-admin")?.classList.add("hidden");
    document.getElementById("user-menu-admin-divider")?.classList.add("hidden");
  }
}

function fillAccountModalForm() {
  if (!state.user) return;
  if (accountDisplayName) {
    accountDisplayName.value = state.user.displayName || state.user.nickname || "";
  }
  if (accountCurrentPassword) accountCurrentPassword.value = "";
  if (accountNewPassword) accountNewPassword.value = "";
  if (accountFormError) accountFormError.classList.add("hidden");
  if (accountFormOk) accountFormOk.classList.add("hidden");
  state.pendingAvatarFile = null;
  if (accountAvatarFile) accountAvatarFile.value = "";
  renderUserAvatar(accountAvatarImg, accountAvatarInitial, state.user);
  if (accountAvatarRemove) {
    accountAvatarRemove.classList.toggle("hidden", !state.user.avatarUrl);
  }
}

function openAccountModal() {
  closeUserMenu();
  fillAccountModalForm();
  openModal(accountModal);
}

function buildThemePicker() {
  if (!themePicker || themePicker.dataset.built === "1") return;
  themePicker.dataset.built = "1";
  themePicker.innerHTML = "";
  Object.values(THEME_PRESETS).forEach((preset) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-option";
    btn.dataset.themeId = preset.id;
    btn.setAttribute("role", "option");
    btn.innerHTML = `<span class="theme-swatch" style="background:${preset.accent}"></span><span class="theme-option-label">${preset.label}</span>`;
    btn.addEventListener("click", () => selectCustomizeTheme(preset.id));
    themePicker.appendChild(btn);
  });
}

function selectCustomizeTheme(themeId) {
  state.customizeThemeDraft = THEME_PRESETS[themeId] ? themeId : "rutsfy";
  themePicker?.querySelectorAll(".theme-option").forEach((el) => {
    el.classList.toggle("active", el.dataset.themeId === state.customizeThemeDraft);
  });
  if (themeCustomPanel) {
    themeCustomPanel.classList.toggle("hidden", state.customizeThemeDraft !== "custom");
  }
  if (state.customizeThemeDraft === "custom" && themeCustomAccent) {
    const accent = state.themeCustom.accent || THEME_PRESETS.rutsfy.accent;
    themeCustomAccent.value = accent;
  }
}

function openCustomizeModal() {
  closeUserMenu();
  buildThemePicker();
  state.customizeThemeDraft = state.themeId || "rutsfy";
  selectCustomizeTheme(state.customizeThemeDraft);
  selectCustomizeScheme(state.colorScheme || "dark");
  if (themeCustomAccent && state.themeId === "custom" && state.themeCustom.accent) {
    themeCustomAccent.value = state.themeCustom.accent;
  }
  openModal(customizeModal);
}

async function saveCustomizeTheme() {
  const themeId = state.customizeThemeDraft || "rutsfy";
  const colorScheme = state.customizeSchemeDraft === "light" ? "light" : "dark";
  const themeCustom =
    themeId === "custom" && themeCustomAccent
      ? { accent: themeCustomAccent.value }
      : {};
  applyTheme(themeId, themeCustom);
  applyColorScheme(colorScheme);
  try {
    await fetch("/api/me/preferences", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ themeId, themeCustom, colorScheme }),
    });
  } catch {
    /* silencioso */
  }
  closeModal(customizeModal);
}

async function submitAccountForm(e) {
  e.preventDefault();
  if (!state.user) return;
  if (accountFormError) accountFormError.classList.add("hidden");
  if (accountFormOk) accountFormOk.classList.add("hidden");

  const displayName = accountDisplayName?.value.trim() || "";
  const newPassword = accountNewPassword?.value || "";
  const currentPassword = accountCurrentPassword?.value || "";

  try {
    if (state.pendingAvatarFile) {
      const fd = new FormData();
      fd.append("file", state.pendingAvatarFile);
      const up = await fetch("/api/me/avatar", { method: "POST", body: fd });
      const upData = await up.json().catch(() => ({}));
      if (!up.ok) throw new Error(apiErrorDetail(upData));
      if (upData.user) state.user = upData.user;
      state.pendingAvatarFile = null;
    }

    const body = {};
    if (displayName && displayName !== state.user.displayName) body.displayName = displayName;
    if (newPassword) {
      body.currentPassword = currentPassword;
      body.newPassword = newPassword;
    }
    if (Object.keys(body).length) {
      const res = await fetch("/api/me/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(apiErrorDetail(data));
      if (data.user) state.user = data.user;
    }

    updateAuthUserNav();
    if (accountCurrentPassword) accountCurrentPassword.value = "";
    if (accountNewPassword) accountNewPassword.value = "";
    closeModal(accountModal);
  } catch (err) {
    if (accountFormError) {
      accountFormError.textContent = err.message || "Erro ao salvar";
      accountFormError.classList.remove("hidden");
    }
  }
}

async function removeAccountAvatar() {
  if (!state.user?.avatarUrl) return;
  try {
    const res = await fetch("/api/me/avatar", { method: "DELETE" });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorDetail(data));
    if (data.user) state.user = data.user;
    state.pendingAvatarFile = null;
    updateAuthUserNav();
    fillAccountModalForm();
  } catch (err) {
    if (accountFormError) {
      accountFormError.textContent = err.message || "Erro ao remover foto";
      accountFormError.classList.remove("hidden");
    }
  }
}

function setAuthMode(mode) {
  state.authMode = mode === "register" ? "register" : "login";
  document.querySelectorAll(".auth-tab").forEach((btn) => {
    const active = btn.dataset.authMode === state.authMode;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", active ? "true" : "false");
  });
  if (authSubmit) {
    authSubmit.textContent = state.authMode === "register" ? "Criar conta" : "Entrar";
  }
  if (authPassword) {
    authPassword.autocomplete = state.authMode === "register" ? "new-password" : "current-password";
  }
  if (authError) authError.classList.add("hidden");
}

async function loadServerPreferences() {
  const res = await fetch("/api/me/preferences");
  if (!res.ok) return;
  const prefs = await res.json();
  purgeLegacySharedStorage();
  const listenKey = userStorageKey(USER_LAST_LISTEN_KEY);
  const recentKey = userStorageKey(RECENT_SEARCHES_KEY);
  if (prefs.volume != null && volume) {
    const n = Number(prefs.volume);
    if (Number.isFinite(n)) {
      const clamped = Math.max(0, Math.min(100, Math.round(n)));
      volume.value = String(clamped);
      audio.volume = clamped / 100;
      syncVolumeVisual();
      try {
        localStorage.setItem(userStorageKey(USER_VOLUME_KEY), volume.value);
      } catch {
        /* silencioso */
      }
    }
  }
  if (prefs.lastListen && typeof prefs.lastListen === "object" && prefs.lastListen.videoId) {
    try {
      localStorage.setItem(listenKey, JSON.stringify(prefs.lastListen));
    } catch {
      /* silencioso */
    }
  } else {
    try {
      localStorage.removeItem(listenKey);
    } catch {
      /* silencioso */
    }
  }
  if (Array.isArray(prefs.recentSearches)) {
    try {
      localStorage.setItem(recentKey, JSON.stringify(prefs.recentSearches.slice(0, MAX_RECENT_SEARCHES)));
    } catch {
      /* silencioso */
    }
  } else {
    try {
      localStorage.removeItem(recentKey);
    } catch {
      /* silencioso */
    }
  }
  applyThemeFromPrefs(prefs);
  state.savedShortcuts = Array.isArray(prefs.savedShortcuts)
    ? normalizeSavedShortcuts(prefs.savedShortcuts)
    : [];
}

function schedulePrefsSync() {
  if (!state.user) return;
  if (prefsSyncTimer) clearTimeout(prefsSyncTimer);
  prefsSyncTimer = setTimeout(() => {
    prefsSyncTimer = null;
    void syncPreferencesToServer();
  }, 2000);
}

async function syncPreferencesToServer() {
  if (!state.user) return;
  const body = {};
  if (volume) {
    const n = Number(volume.value);
    if (Number.isFinite(n)) body.volume = Math.max(0, Math.min(100, Math.round(n)));
  }
  const lastListen = readLastListenRaw();
  if (lastListen?.videoId) body.lastListen = lastListen;
  if (state.themeId) {
    body.themeId = state.themeId;
    body.themeCustom = state.themeCustom || {};
  }
  if (state.colorScheme) {
    body.colorScheme = state.colorScheme;
  }
  if (Array.isArray(state.savedShortcuts)) {
    body.savedShortcuts = state.savedShortcuts;
  }
  body.recentSearches = loadRecentSearches().slice(0, MAX_RECENT_SEARCHES);
  if (!Object.keys(body).length) return;
  try {
    await fetch("/api/me/preferences", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    /* silencioso */
  }
}

async function bootstrapAuth() {
  try {
    const res = await fetch("/api/auth/me");
    if (res.ok) {
      const data = await res.json();
      state.user = data.user;
      showAuthBoot();
      updateAuthUserNav();
      return true;
    }
  } catch {
    /* offline */
  }
  showAuthGate(false);
  return false;
}

async function onAuthenticated() {
  showAuthBoot();
  try {
    purgeLegacySharedStorage();
    resetClientUserData();
    updateAuthUserNav();
    await loadServerPreferences();
    await Promise.all([refreshLibrary(), refreshHistory(), loadServerVideoIds(), loadDownloadBlocklist()]);
    await refreshHome();
    restoreLastListenToPlayer();
    updatePlayerSourceLink();
    refreshQuota();
    void refreshExplore();
  } finally {
    hideAuthGate();
  }
  window.__showPwaInstallBanner?.();
}

async function submitAuthForm(e) {
  e.preventDefault();
  if (!authNickname || !authPassword) return;
  const nickname = authNickname.value.trim();
  const password = authPassword.value;
  if (authError) authError.classList.add("hidden");
  if (authSubmit) authSubmit.disabled = true;
  const url = state.authMode === "register" ? "/api/auth/register" : "/api/auth/login";
  const payload = { nickname, password };
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorDetail(data));
    if (state.user?.id && state.user.id !== data.user?.id) {
      resetClientUserData();
    }
    state.user = data.user;
    purgeLegacySharedStorage();
    await onAuthenticated();
  } catch (err) {
    if (authError) {
      authError.textContent = err.message || "Erro ao entrar";
      authError.classList.remove("hidden");
    }
  } finally {
    if (authSubmit) authSubmit.disabled = false;
  }
}

async function logoutSession() {
  saveLastListen();
  await syncPreferencesToServer();
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch {
    /* silencioso */
  }
  state.user = null;
  resetClientUserData();
  clearRutsfyStorage();
  purgeLegacySharedStorage();
  updateAuthUserNav();
  showAuthGate(true);
}

function bindAuthUi() {
  document.querySelectorAll(".auth-tab").forEach((btn) => {
    btn.addEventListener("click", () => setAuthMode(btn.dataset.authMode || "login"));
  });
  if (authForm) authForm.addEventListener("submit", (e) => void submitAuthForm(e));
  setAuthMode("login");
}

function bindUserMenuUi() {
  if (userMenuBtn) {
    userMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleUserMenu();
    });
  }
  userMenuPanel?.querySelectorAll("[data-user-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.userAction;
      if (action === "account") openAccountModal();
      else if (action === "customize") openCustomizeModal();
      else if (action === "admin") openAdminPanel();
      else if (action === "logout") void logoutSession();
      else closeUserMenu();
    });
  });
  document.addEventListener("click", (e) => {
    if (!state.userMenuOpen) return;
    if (userMenuEl?.contains(e.target)) return;
    closeUserMenu();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeUserMenu();
      closeModal(accountModal);
      closeModal(customizeModal);
    }
  });

  if (accountForm) accountForm.addEventListener("submit", (e) => void submitAccountForm(e));
  accountModalCancel?.addEventListener("click", () => closeModal(accountModal));
  accountModal?.addEventListener("click", (e) => {
    if (e.target === accountModal) closeModal(accountModal);
  });

  accountAvatarFile?.addEventListener("change", () => {
    const file = accountAvatarFile.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      if (accountFormError) {
        accountFormError.textContent = "Imagem muito grande (máx. 2 MB).";
        accountFormError.classList.remove("hidden");
      }
      accountAvatarFile.value = "";
      return;
    }
    state.pendingAvatarFile = file;
    const url = URL.createObjectURL(file);
    if (accountAvatarImg) {
      accountAvatarImg.src = url;
      accountAvatarImg.classList.remove("hidden");
    }
    if (accountAvatarInitial) accountAvatarInitial.classList.add("hidden");
    if (accountAvatarRemove) accountAvatarRemove.classList.remove("hidden");
  });
  accountAvatarRemove?.addEventListener("click", () => void removeAccountAvatar());

  customizeModalCancel?.addEventListener("click", () => closeModal(customizeModal));
  customizeModalSave?.addEventListener("click", () => void saveCustomizeTheme());
  customizeModal?.addEventListener("click", (e) => {
    if (e.target === customizeModal) closeModal(customizeModal);
  });

  searchSaveShortcut?.addEventListener("click", () => toggleSaveCurrentSearch());

  document.querySelectorAll(".appearance-option").forEach((btn) => {
    btn.addEventListener("click", () => selectCustomizeScheme(btn.dataset.scheme || "dark"));
  });
}

const PLAY_SVG =
  '<svg class="col-play-icon col-play-icon-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
const PAUSE_SVG =
  '<svg class="col-play-icon col-play-icon-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6V5zm8 0h4v14h-4V5z"/></svg>';

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** i).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function durationIsoToSeconds(iso) {
  const m = /^P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$/.exec(iso || "");
  if (!m) return null;
  const d = m[1] ? parseInt(m[1], 10) : 0;
  const h = m[2] ? parseInt(m[2], 10) : 0;
  const min = m[3] ? parseInt(m[3], 10) : 0;
  const s = m[4] ? parseFloat(m[4]) : 0;
  return d * 86400 + h * 3600 + min * 60 + s;
}

function isTrackDownloadBlocked(item) {
  const id = item?.videoId;
  return Boolean(id && state.downloadBlocklistIds.has(id));
}

function isCatalogHiddenVideo(item) {
  const id = item?.videoId;
  return Boolean(id && state.catalogHiddenVideoIds?.has(id));
}

function estimatedOpusBytesFromItem(item) {
  const sec = durationIsoToSeconds(item?.duration);
  if (sec == null || sec <= 0) return null;
  const kbps = 64;
  return (sec * kbps * 1000) / 8 * 1.1;
}

function isOverMaxFileSizeEstimate(item) {
  if (isTrackOnServer(item)) return false;
  const mb = state.maxDownloadFileMb;
  if (!mb || mb <= 0) return false;
  const est = estimatedOpusBytesFromItem(item);
  if (est == null) return false;
  return est > mb * 1024 * 1024;
}

/** Oculta da busca/fila como faixas longas ou bloqueadas por tamanho. */
function shouldHideTrackFromLists(item) {
  if (!item?.videoId) return true;
  if (isTrackOnServer(item)) return false;
  if (isCatalogHiddenVideo(item)) return true;
  if (isTrackDownloadBlocked(item)) return true;
  const sec = durationIsoToSeconds(item?.duration);
  if (sec != null && sec > AUTO_PREFETCH_MAX_DURATION_SEC) return true;
  if (isOverMaxFileSizeEstimate(item)) return true;
  return false;
}

const _PART_WORD_MAP = {
  one: "1",
  two: "2",
  three: "3",
  four: "4",
  five: "5",
  i: "1",
  ii: "2",
  iii: "3",
  iv: "4",
  v: "5",
};

const _TITLE_DEDUPE_NOISE =
  /\b(official(?:\s+music)?\s+video|official\s+audio|lyrics?(?:\s+video)?|remastered?(?:\s+\d{4})?|restored|re-?edited|extended|visuali[sz]er|full\s+hd|\bhd\b|\b4k\b|\b8k\b|\bmv\b|audio\s+only|vevo|pulse|mono\s+mix|stereo|anniversary|deluxe|explicit|clean\s+version|radio\s+edit|single\s+version|album\s+version|original\s+mix|video\s+analysis|\banalysis\b|react(?:ion)?|review|explained|breakdown|meaning|espanol|español|ingles|ingl[eê]s|english|spanish|subtitles?|legendado?|traducido|translation|with\s+lyrics)\b/gi;

const _JUNK_SEGMENT_WORDS = new Set([
  "analysis",
  "espanol",
  "español",
  "ingles",
  "ingles",
  "english",
  "spanish",
  "subtitles",
  "subtitle",
  "legendado",
  "traducido",
  "translation",
  "hd",
  "4k",
  "8k",
  "video",
  "react",
  "reaction",
  "review",
  "explained",
  "breakdown",
  "meaning",
]);

const _ARTIST_CHANNEL_NOISE = /\s*[-–]\s*topic\s*$|\s+vevo\s*$|\s+official\s*$|\s+records\s*$|\s+music\s*$/i;

function foldAsciiForDedupe(text) {
  return String(text || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function inferArtistFromTitle(title) {
  const m = /^(.+?)\s+[-–|·]\s+(.+)$/.exec(String(title || "").trim());
  if (!m) return null;
  const artist = m[1].trim();
  return artist && artist.length <= 80 ? artist : null;
}

function isJunkTitleSegment(segment) {
  let s = foldAsciiForDedupe(segment).replace(/[^\w\s]/g, " ");
  s = s.replace(/\s+/g, " ").trim();
  if (!s) return true;
  if (/^(video\s+analysis|analysis|react(?:ion)?|review|hd|4k|8k)/i.test(s)) return true;
  const tokens = s.split(/\s+/).filter(Boolean);
  return tokens.length > 0 && tokens.every((t) => _JUNK_SEGMENT_WORDS.has(t));
}

function partNumberFromText(text) {
  const m = /\b(?:part|pt\.?)[\s,:-]*(one|two|three|four|five|i{1,3}|iv|\d+)\b/i.exec(
    text || ""
  );
  if (!m) return null;
  const raw = m[1].toLowerCase();
  return _PART_WORD_MAP[raw] || (raw.match(/^\d+$/) ? raw : null);
}

function normalizeArtistKey(artist, channel) {
  for (const raw of [artist, channel]) {
    if (!raw) continue;
    let a = foldAsciiForDedupe(String(raw).trim());
    a = a.replace(_ARTIST_CHANNEL_NOISE, "");
    a = a.replace(/[^\w\s]/g, " ");
    a = a.replace(/\s+/g, " ").trim();
    if (a) return a;
  }
  return "";
}

function stripSongTitleForDedupe(title, artist, channel) {
  let t = String(title || "").trim();
  const art = (inferArtistFromTitle(t) || artist || channel || "").trim();
  if (art) {
    const esc = art.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    t = t.replace(new RegExp(`^${esc}\\s*[-–|·:]\\s*`, "i"), "").trim();
  } else {
    const m = /^(.+?)\s+[-–|·]\s+(.+)$/.exec(t);
    if (m) t = m[2].trim();
  }
  const dashParts = t.split(/\s[-–—]\s+/);
  if (dashParts.length > 1) {
    const kept = [dashParts[0].trim()];
    for (let i = 1; i < dashParts.length; i += 1) {
      const seg = dashParts[i].trim();
      if (seg && !isJunkTitleSegment(seg)) kept.push(seg);
    }
    t = kept.length > 1 ? kept.join(" - ") : kept[0];
  }
  return t;
}

function normalizeSongCoreForDedupe(songTitle) {
  let t = foldAsciiForDedupe(String(songTitle || "").trim());
  if (!t) return "";
  const part = partNumberFromText(t);
  t = t.replace(/["']/g, " ");
  t = t.replace(/[\[\(\{][^\]\)\}]*[\]\)\}]/g, " ");
  t = t.replace(_TITLE_DEDUPE_NOISE, " ");
  t = t.replace(/\b(?:part|pt\.?)[\s,:-]*(one|two|three|four|five|i{1,3}|iv|\d+)\b/gi, " ");
  t = t.replace(/\b\d{4}\b/g, " ");
  t = t.replace(/[^\w\s]/g, " ");
  t = t.replace(/\s+/g, " ").trim();
  if (part) t = `${t} part ${part}`.trim();
  return t;
}

function similarTrackDedupeKey(item) {
  if (!item?.videoId || !item.title) return null;
  const fromTitle = inferArtistFromTitle(item.title);
  const artist = normalizeArtistKey(fromTitle || item.artist, item.channelTitle);
  const song = stripSongTitleForDedupe(item.title, fromTitle || item.artist, item.channelTitle);
  const core = normalizeSongCoreForDedupe(song);
  if (!core) return null;
  return `${artist}|${core}`;
}

function searchCatalogSongKeys() {
  return [...new Set(state.searchCatalog.map((i) => similarTrackDedupeKey(i)).filter(Boolean))];
}

function compactSearchCatalog() {
  if (!state.searchCatalog.length) return false;
  const before = state.searchCatalog.length;
  state.searchCatalog = filterDiscoverableItems(state.searchCatalog);
  if (state.searchCatalog.length === before) return false;
  state.searchVisibleCount = Math.min(state.searchVisibleCount, state.searchCatalog.length);
  if (shouldBindSearchResultsToQueue()) syncSearchQueue();
  refreshDiscoverableListsAfterPurge();
  updateSearchStatusLine();
  return true;
}

function dedupeTrackQuality(item) {
  const title = String(item?.title || "").toLowerCase();
  const junk =
    title.includes("analysis") ||
    title.includes("español") ||
    title.includes("espanol") ||
    title.includes("inglés") ||
    title.includes("ingles") ||
    title.includes("react") ||
    title.includes("review") ||
    title.includes("explained") ||
    title.includes("legendado");
  const official = title.includes("official");
  const onServer = Boolean(item?.onServer);
  return [onServer ? 1 : 0, official ? 1 : 0, junk ? 0 : 1];
}

function dedupeQualityGreater(a, b) {
  const qa = dedupeTrackQuality(a);
  const qb = dedupeTrackQuality(b);
  for (let i = 0; i < qa.length; i += 1) {
    if (qa[i] !== qb[i]) return qa[i] > qb[i];
  }
  return false;
}

function dedupeSimilarTracks(items) {
  const indexByKey = new Map();
  const out = [];
  for (const item of items || []) {
    const key = similarTrackDedupeKey(item);
    if (!key) {
      out.push(item);
      continue;
    }
    if (!indexByKey.has(key)) {
      indexByKey.set(key, out.length);
      out.push(item);
      continue;
    }
    const idx = indexByKey.get(key);
    if (dedupeQualityGreater(item, out[idx])) out[idx] = item;
  }
  return out;
}

function filterDiscoverableItems(items) {
  return dedupeSimilarTracks((items || []).filter((it) => !shouldHideTrackFromLists(it)));
}

function purgeTrackFromDiscoverableLists(videoId) {
  if (!videoId) return false;
  const drop = (arr) => (Array.isArray(arr) ? arr.filter((it) => it?.videoId !== videoId) : arr);
  let changed = false;

  const sc = state.searchCatalog.length;
  state.searchCatalog = drop(state.searchCatalog);
  if (state.searchCatalog.length !== sc) changed = true;

  const fl = state.freeListItems.length;
  state.freeListItems = drop(state.freeListItems);
  if (state.freeListItems.length !== fl) changed = true;

  if (state.queue.length) {
    const playingId =
      state.queueIndex >= 0 && state.queue[state.queueIndex]
        ? state.queue[state.queueIndex].videoId
        : null;
    const qBefore = state.queue.length;
    state.queue = drop(state.queue);
    if (state.queue.length !== qBefore) {
      changed = true;
      if (playingId === videoId) {
        state.queueIndex = -1;
      } else if (state.queueIndex >= 0) {
        const newIdx = state.queue.findIndex((it) => it.videoId === playingId);
        state.queueIndex = newIdx >= 0 ? newIdx : Math.min(state.queueIndex, state.queue.length - 1);
      }
      rebuildPlayOrder();
    }
  }

  if (!changed) return false;

  state.searchVisibleCount = Math.min(state.searchVisibleCount, state.searchCatalog.length);
  if (shouldBindSearchResultsToQueue()) syncSearchQueue();
  refreshDiscoverableListsAfterPurge();
  return true;
}

function purgeBlockedTrackFromUi(videoId) {
  purgeTrackFromDiscoverableLists(videoId);
}

function evictHiddenTracksFromCatalog() {
  const ids = new Set();
  for (const item of state.searchCatalog) {
    if (item?.videoId && shouldHideTrackFromLists(item)) ids.add(item.videoId);
  }
  for (const item of state.freeListItems) {
    if (item?.videoId && shouldHideTrackFromLists(item)) ids.add(item.videoId);
  }
  for (const id of ids) purgeTrackFromDiscoverableLists(id);
}

function refreshDiscoverableListsAfterPurge() {
  if (state.view === "search") renderSearchVisible();
  if (state.view === "free" && freeListEl) {
    renderFreeList(state.freeListItems, { append: false });
    updateFreeShowMoreUi();
  }
  if (state.view === "nowplaying") renderNowPlaying();
  updateCatalogShowMoreUi();
  updateSearchStatusLine();
}

function isDownloadBlocklistMessage(message) {
  const m = String(message || "").toLowerCase();
  return (
    m.includes("pesad") ||
    m.includes("bloqueio") ||
    m.includes("bloqueada") ||
    m.includes("limite") ||
    m.includes("mb)")
  );
}

function isRejectedDownloadMessage(message) {
  const m = String(message || "").toLowerCase();
  if (isDownloadBlocklistMessage(message)) return true;
  if (m.includes("20 min")) return true;
  if (m.includes("minutos não podem")) return true;
  if (m.includes("não podem ser baixadas")) return true;
  return false;
}

function noteDownloadRejected(videoId, message) {
  if (!videoId || !isRejectedDownloadMessage(message)) return;
  if (isDownloadBlocklistMessage(message)) {
    state.downloadBlocklistIds.add(videoId);
  } else {
    state.catalogHiddenVideoIds.add(videoId);
  }
  purgeTrackFromDiscoverableLists(videoId);
  void loadDownloadBlocklist();
}

function noteDownloadBlocklisted(videoId, message) {
  noteDownloadRejected(videoId, message);
}

function purgeAllBlocklistedFromUi() {
  for (const id of state.downloadBlocklistIds) {
    purgeBlockedTrackFromUi(id);
  }
}

function isAutoPrefetchAllowed(item) {
  return !shouldHideTrackFromLists(item);
}

function pickPrefetchItems(catalog, max = PREFETCH_AHEAD) {
  const out = [];
  for (const item of catalog || []) {
    if (out.length >= max) break;
    if (!item?.videoId || !isAutoPrefetchAllowed(item)) continue;
    out.push(item);
  }
  return out;
}

function formatDurationIso(iso) {
  const m = /^P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(iso || "");
  if (!m) return "—";
  const [d, h, min, s] = m.slice(1).map((x) => (x ? parseInt(x, 10) : 0));
  const hh = d * 24 + h;
  const mm = String(min).padStart(hh ? 2 : 1, "0");
  const ss = String(s).padStart(2, "0");
  return hh ? `${hh}:${mm}:${ss}` : `${mm}:${ss}`;
}

function formatSeconds(sec) {
  if (!Number.isFinite(sec) || sec < 0) return "0:00";
  const s = Math.floor(sec % 60);
  const m = Math.floor(sec / 60) % 60;
  const h = Math.floor(sec / 3600);
  const ss = String(s).padStart(2, "0");
  if (h) return `${h}:${String(m).padStart(2, "0")}:${ss}`;
  return `${m}:${ss}`;
}

function descSnippet(text, max = 80) {
  const t = (text || "").replace(/\s+/g, " ").trim();
  if (!t) return "—";
  return t.length > max ? `${t.slice(0, max).trim()}…` : t;
}

function higherResThumb(url) {
  return url ? url.replace("/mqdefault", "/hqdefault") : "";
}

function absoluteMediaUrl(pathOrUrl) {
  if (!pathOrUrl) return "";
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  try {
    return new URL(rutUrl(pathOrUrl), window.location.origin).href;
  } catch {
    return pathOrUrl;
  }
}

let mediaSessionCoverBlobUrl = null;
let mediaSessionCoverVideoId = null;

/** Capas same-origin — Android/iOS usam para fundo desfocado da notificação. */
function buildMediaSessionArtwork(track) {
  const artwork = [];
  const push = (src, sizes, type = "image/jpeg") => {
    const abs = absoluteMediaUrl(src);
    if (abs) artwork.push({ src: abs, sizes, type });
  };
  const videoId = track?.videoId;
  if (videoId) {
    const base = `/api/tracks/${encodeURIComponent(videoId)}/cover.jpg`;
    push(`${base}?size=1280`, "1280x1280");
    push(`${base}?size=480`, "480x480");
    push(`${base}?size=320`, "320x320");
    return artwork;
  }
  const thumbnailUrl = track?.thumbnailUrl || "";
  if (thumbnailUrl) {
    const max = thumbnailUrl.replace(/\/(mqdefault|hqdefault|sddefault)(\.[a-z]+)?$/i, "/maxresdefault$2");
    push(max, "1280x720");
    push(higherResThumb(thumbnailUrl), "480x360");
  }
  push(rutUrl("/assets/icons/icon-512.png?v=3"), "512x512", "image/png");
  return artwork;
}

async function upgradeMediaSessionCoverBlob(track) {
  if (!track?.videoId || !("mediaSession" in navigator)) return;
  const url = absoluteMediaUrl(`/api/tracks/${encodeURIComponent(track.videoId)}/cover.jpg?size=1280`);
  try {
    const res = await fetch(url);
    if (!res.ok) return;
    const blob = await res.blob();
    if ((state.current?.videoId || track.videoId) !== track.videoId) return;
    if (mediaSessionCoverBlobUrl) URL.revokeObjectURL(mediaSessionCoverBlobUrl);
    mediaSessionCoverBlobUrl = URL.createObjectURL(blob);
    mediaSessionCoverVideoId = track.videoId;
    const meta = navigator.mediaSession.metadata;
    if (!meta) return;
    const blobArt = {
      src: mediaSessionCoverBlobUrl,
      sizes: "1280x1280",
      type: blob.type || "image/jpeg",
    };
    const rest = buildMediaSessionArtwork(track).filter((a) => a.src !== url);
    navigator.mediaSession.metadata = new MediaMetadata({
      title: meta.title,
      artist: meta.artist,
      album: meta.album,
      artwork: [blobArt, ...rest],
    });
  } catch {
    /* mantém URLs HTTP */
  }
}

let mediaSessionHandlersBound = false;
let mediaSessionPositionSyncAt = 0;

function mediaSessionAlbumLabel() {
  const bits = [];
  if (state.shuffle) bits.push("Aleatório");
  if (state.repeat === "one") bits.push("Repetir uma");
  else if (state.repeat === "all") bits.push("Repetir tudo");
  return bits.length ? `RutsFy · ${bits.join(" · ")}` : "RutsFy";
}

function refreshMediaSessionModeMetadata() {
  const track = state.current;
  if (!track?.videoId || !("mediaSession" in navigator)) return;
  const prev = navigator.mediaSession.metadata;
  const credit = trackCreditLine(track);
  const artist = credit.label ? creditDisplayLabel(credit.label) : "RutsFy";
  let artwork = buildMediaSessionArtwork(track);
  if (prev?.artwork?.length) {
    artwork = [...prev.artwork];
  } else if (mediaSessionCoverBlobUrl && track.videoId === mediaSessionCoverVideoId) {
    artwork = [
      { src: mediaSessionCoverBlobUrl, sizes: "1280x1280", type: "image/jpeg" },
      ...artwork,
    ];
  }
  try {
    navigator.mediaSession.metadata = new MediaMetadata({
      title: track.title || prev?.title || "Sem título",
      artist,
      album: mediaSessionAlbumLabel(),
      artwork,
    });
  } catch {
    /* MediaMetadata indisponível */
  }
}

function toggleShuffleMode() {
  state.shuffle = !state.shuffle;
  rebuildPlayOrder();
  updateTransportControls();
  refreshMediaSessionModeMetadata();
  if (state.isPlaying || holdMediaSessionPlaying) void primeUpcomingPlayback();
}

function cycleRepeatMode() {
  const cycle = { off: "all", all: "one", one: "off" };
  state.repeat = cycle[state.repeat] || "off";
  updateTransportControls();
  refreshMediaSessionModeMetadata();
  if (state.isPlaying || holdMediaSessionPlaying) void primeUpcomingPlayback();
}

function isMobileMediaSessionLayout() {
  try {
    return window.matchMedia(MOBILE_UI_MEDIA).matches;
  } catch {
    return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent || "");
  }
}

function syncMediaSessionSeekHandlers() {
  if (!("mediaSession" in navigator) || !mediaSessionHandlersBound) return;
  const ms = navigator.mediaSession;
  const bind = (action, fn) => {
    try {
      ms.setActionHandler(action, fn);
    } catch {
      /* ação não suportada */
    }
  };
  if (isMobileMediaSessionLayout()) {
    bind("seekbackward", () => toggleShuffleMode());
    bind("seekforward", () => cycleRepeatMode());
  } else {
    const skipBy = (delta, details) => {
      if (!audio.src || !Number.isFinite(audio.duration)) return;
      const step = details?.seekOffset ?? 10;
      const off = delta < 0 ? -Math.abs(step) : Math.abs(step);
      audio.currentTime = Math.max(0, Math.min(audio.currentTime + off, audio.duration));
      syncMediaSessionPosition(true);
    };
    bind("seekbackward", (details) => skipBy(-1, details));
    bind("seekforward", (details) => skipBy(1, details));
  }
}

function initMediaSessionHandlers() {
  if (mediaSessionHandlersBound || !("mediaSession" in navigator)) return;
  mediaSessionHandlersBound = true;
  const ms = navigator.mediaSession;
  const safeHandler = (action, fn) => {
    try {
      ms.setActionHandler(action, fn);
    } catch {
      /* ação não suportada neste navegador */
    }
  };
  safeHandler("play", () => {
    if (!audio.src && state.current?.videoId) {
      void playItem(state.current, { setQueue: false });
      return;
    }
    audio.play().catch(() => {});
  });
  safeHandler("pause", () => {
    userPauseRequested = true;
    ignoreAutoPauseUntil = 0;
    audio.pause();
  });
  safeHandler("previoustrack", () => {
    advancePlayback(-1);
  });
  safeHandler("nexttrack", () => {
    advancePlayback(1);
  });
  safeHandler("stop", () => {
    userPauseRequested = true;
    ignoreAutoPauseUntil = 0;
    clearTimeout(trackEndTimer);
    audio.pause();
    audio.currentTime = 0;
    syncMediaSessionPlaybackState();
  });
  safeHandler("seekto", (details) => {
    if (details.seekTime == null || !Number.isFinite(audio.duration)) return;
    audio.currentTime = Math.max(0, Math.min(details.seekTime, audio.duration));
    syncMediaSessionPosition(true);
  });
  safeHandler("shuffle", () => toggleShuffleMode());
  safeHandler("repeat", () => cycleRepeatMode());
  syncMediaSessionSeekHandlers();
  window.addEventListener("resize", () => syncMediaSessionSeekHandlers(), { passive: true });
}

function syncMediaSessionPlaybackState() {
  if (!("mediaSession" in navigator)) return;
  initMediaSessionHandlers();
  const hasTrack = Boolean(state.current?.videoId || audio.src);
  if (!hasTrack) {
    navigator.mediaSession.playbackState = "none";
    return;
  }
  // Enquanto o áudio segue tocando, a sessão fica "playing" mesmo se a
  // próxima faixa ainda está carregando. Marcar "paused" aqui faz o
  // navegador disparar a ação de pausa e parar a música no primeiro próximo.
  if (holdMediaSessionPlaying || (audio.src && !audio.paused)) {
    navigator.mediaSession.playbackState = "playing";
    return;
  }
  navigator.mediaSession.playbackState = "paused";
}

function syncMediaSessionPosition(force = false) {
  if (!("mediaSession" in navigator)) return;
  if (!audio.src || !Number.isFinite(audio.duration) || audio.duration <= 0) return;
  const now = Date.now();
  if (!force && now - mediaSessionPositionSyncAt < 900) return;
  mediaSessionPositionSyncAt = now;
  try {
    navigator.mediaSession.setPositionState({
      duration: audio.duration,
      playbackRate: audio.playbackRate || 1,
      position: Math.max(0, Math.min(audio.currentTime, audio.duration)),
    });
  } catch {
    /* setPositionState indisponível */
  }
}

function syncMediaSessionMetadata(item) {
  if (!("mediaSession" in navigator)) return;
  initMediaSessionHandlers();
  const track = item || state.current;
  if (!track?.videoId) {
    navigator.mediaSession.metadata = null;
    syncMediaSessionPlaybackState();
    return;
  }
  const credit = trackCreditLine(track);
  const artist = credit.label ? creditDisplayLabel(credit.label) : "RutsFy";
  try {
    navigator.mediaSession.metadata = new MediaMetadata({
      title: track.title || "Sem título",
      artist,
      album: mediaSessionAlbumLabel(),
      artwork: buildMediaSessionArtwork(track),
    });
  } catch {
    /* MediaMetadata indisponível */
  }
  if (track.videoId !== mediaSessionCoverVideoId) {
    if (mediaSessionCoverBlobUrl) {
      URL.revokeObjectURL(mediaSessionCoverBlobUrl);
      mediaSessionCoverBlobUrl = null;
      mediaSessionCoverVideoId = null;
    }
  }
  void upgradeMediaSessionCoverBlob(track);
  syncMediaSessionPlaybackState();
  syncMediaSessionPosition(true);
}

function itemPayload(item) {
  return {
    title: item.title,
    artist: item.artist,
    artistId: item.artistId,
    album: item.album,
    albumId: item.albumId,
    deezerId: item.deezerId,
    genre: item.genre,
    catalogSource: item.catalogSource,
    channelId: item.channelId,
    channelTitle: item.channelTitle,
    description: item.description,
    duration: item.duration,
    thumbnailUrl: item.thumbnailUrl,
    url: item.url,
  };
}

function extractArtistFromTitle(title) {
  const t = (title || "").trim();
  if (!t) return "";
  const m = t.match(/^(.+?)\s+[-–|·]\s+(.+)$/);
  if (!m) return "";
  const artist = m[1].trim();
  return artist.length > 0 && artist.length <= 80 ? artist : "";
}

/** Linha secundária: artista se existir, senão canal. */
function trackCreditLine(item) {
  const artist = (item?.artist || extractArtistFromTitle(item?.title) || "").trim();
  if (artist) {
    return { label: artist, query: artist, kind: "artist", channelId: "" };
  }
  const channel = (item?.channelTitle || "").trim();
  const channelId = (item?.channelId || "").trim();
  if (channel) {
    return { label: channel, query: channel, kind: "channel", channelId };
  }
  return { label: "", query: "", kind: "", channelId: "" };
}

function creditActionTitle(credit) {
  if (!credit?.label) return "";
  if (credit.kind === "channel" && credit.channelId) {
    return `Vídeos do canal: ${credit.label}`;
  }
  return `Buscar: ${credit.query || credit.label}`;
}

const MOBILE_UI_MEDIA =
  "(max-width: 900px), ((max-width: 1200px) and (hover: none) and (pointer: coarse))";

const backExitToast = document.getElementById("back-exit-toast");
let mobileBackExitArmed = false;
let mobileBackExitArmTimer = null;
let mobileBackBound = false;

function isMobileUi() {
  return window.matchMedia(MOBILE_UI_MEDIA).matches;
}

function isIosDevice() {
  const ua = navigator.userAgent || "";
  if (/iPhone|iPod/i.test(ua)) return true;
  if (/iPad/i.test(ua)) return true;
  return navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1;
}

function needsMobileBackButton() {
  return isMobileUi() && (isIosDevice() || isAndroidDevice());
}

const viewReturnStack = [];
let navigationRestoring = false;
let navigationIgnoreNextPop = false;

function contentScrollRoot() {
  return document.querySelector(".content");
}

function captureFreeBrowseState() {
  if (!freeBrowseBar || freeBrowseBar.classList.contains("hidden")) return null;
  return {
    categoryId: state.freeBrowseCategoryId,
    label: state.freeBrowseLabel,
    filterQuery: state.freeFilterQuery,
    listItems: state.freeListItems.map((i) => ({ ...i })),
    listOffset: state.freeListOffset,
    listTotal: state.freeListTotal,
    freeSearchInput: freeSearchInput?.value || "",
  };
}

function captureSearchSessionState() {
  if (state.view !== "search") return null;
  if (!state.searchQuery && !state.searchMixId && !state.searchChannelId) return null;
  const scrollRoot = contentScrollRoot();
  return {
    searchQuery: state.searchQuery,
    searchMixId: state.searchMixId,
    searchChannelId: state.searchChannelId,
    searchChannelTitle: state.searchChannelTitle,
    searchPublishedAfter: state.searchPublishedAfter,
    searchPublishedBefore: state.searchPublishedBefore,
    searchOrder: state.searchOrder,
    searchHeading: searchHeading?.textContent || "",
    searchCatalog: state.searchCatalog.map((i) => ({ ...i })),
    searchVisibleCount: state.searchVisibleCount,
    searchNextPageToken: state.searchNextPageToken,
    searchMixCatalogTotal: state.searchMixCatalogTotal,
    searchHydrated: [...state.searchHydrated],
    searchLoadingMore: state.searchLoadingMore,
    inputValue: input.value,
    statusMessage: statusTextEl?.textContent || "",
    scrollTop: scrollRoot?.scrollTop ?? 0,
  };
}

function captureScrollAnchor(originEl) {
  if (!(originEl instanceof Element)) return null;
  const card = originEl.closest(".mix-card");
  if (!card) return null;
  return {
    mixId: card.dataset.mixId || null,
    freeShelfId: card.dataset.freeShelfId || null,
    exploreCategory: card.closest("[data-category]")?.dataset.category || null,
  };
}

function captureNavigationEntry(opts = {}) {
  const scrollRoot = contentScrollRoot();
  return {
    view: state.view,
    scrollTop: scrollRoot?.scrollTop ?? 0,
    scrollAnchor: captureScrollAnchor(opts.originEl),
    search: captureSearchSessionState(),
    freeBrowse: captureFreeBrowseState(),
  };
}

function resetNavigationReturnStack() {
  viewReturnStack.length = 0;
  updateNavigationBackUi();
}

function pushNavigationReturn(opts = {}) {
  if (navigationRestoring || opts.skipPush) return;
  viewReturnStack.push(captureNavigationEntry(opts));
  updateNavigationBackUi();
  if (isMobileUi()) pushMobileBackState();
}

function navigationBackAvailable() {
  return viewReturnStack.length > 0;
}

function shouldShowNavigationBackButton() {
  if (!navigationBackAvailable()) return false;
  if (isMobileUi() && !needsMobileBackButton()) return false;
  if (state.view === "search") return true;
  if (state.view === "home" && freeBrowseBar && !freeBrowseBar.classList.contains("hidden")) {
    return true;
  }
  return false;
}

function updateNavigationBackUi() {
  const show = shouldShowNavigationBackButton();
  navViewBack?.classList.toggle("hidden", !show);
  if (freeBrowseBack) {
    freeBrowseBack.classList.toggle("hidden", !show || state.view !== "home");
  }
}

function restoreContentScroll(entry, scrollTopOverride) {
  const scrollRoot = contentScrollRoot();
  if (!scrollRoot || !entry) return;
  const topFallback = scrollTopOverride ?? entry.scrollTop ?? 0;
  const apply = () => {
    const anchor = entry.scrollAnchor;
    if (anchor?.mixId) {
      const el = document.querySelector(
        `.mix-card[data-mix-id="${CSS.escape(anchor.mixId)}"]`
      );
      if (el) {
        const top =
          el.getBoundingClientRect().top -
          scrollRoot.getBoundingClientRect().top +
          scrollRoot.scrollTop -
          72;
        scrollRoot.scrollTop = Math.max(0, top);
        return;
      }
    }
    if (anchor?.freeShelfId) {
      const el = document.querySelector(
        `.mix-card[data-free-shelf-id="${CSS.escape(anchor.freeShelfId)}"]`
      );
      if (el) {
        const top =
          el.getBoundingClientRect().top -
          scrollRoot.getBoundingClientRect().top +
          scrollRoot.scrollTop -
          72;
        scrollRoot.scrollTop = Math.max(0, top);
        return;
      }
    }
    scrollRoot.scrollTop = topFallback;
  };
  window.requestAnimationFrame(() => window.requestAnimationFrame(apply));
}

function applySearchSessionState(s) {
  if (!s) return;
  clearSearchFilters();
  state.searchQuery = s.searchQuery ?? "";
  state.searchMixId = s.searchMixId ?? null;
  state.searchChannelId = s.searchChannelId ?? null;
  state.searchChannelTitle = s.searchChannelTitle ?? null;
  state.searchPublishedAfter = s.searchPublishedAfter ?? null;
  state.searchPublishedBefore = s.searchPublishedBefore ?? null;
  state.searchOrder = s.searchOrder ?? null;
  state.searchCatalog = (s.searchCatalog || []).map((i) => ({ ...i }));
  state.searchVisibleCount = s.searchVisibleCount ?? 0;
  state.searchNextPageToken = s.searchNextPageToken ?? null;
  state.searchMixCatalogTotal = s.searchMixCatalogTotal ?? 0;
  state.searchHydrated = new Set(s.searchHydrated || []);
  state.searchLoadingMore = s.searchLoadingMore ?? false;
  setView("search", { skipSearchFocus: true });
  searchHeading.textContent = s.searchHeading || state.searchQuery || "Buscar";
  clearSearchEntityCover();
  input.value = s.inputValue ?? "";
  compactSearchCatalog();
  restoreSearchViewUi();
  searchHeading.textContent = s.searchHeading || searchHeading.textContent;
  setStatus(s.statusMessage || "");
  updateSearchSaveButton();
}

function restoreFreeBrowseState(fb) {
  if (!fb) return;
  state.freeBrowseCategoryId = fb.categoryId;
  state.freeBrowseLabel = fb.label;
  state.freeFilterQuery = fb.filterQuery;
  state.freeListItems = (fb.listItems || []).map((i) => ({ ...i }));
  state.freeListOffset = fb.listOffset ?? state.freeListItems.length;
  state.freeListTotal = fb.listTotal ?? state.freeListItems.length;
  if (freeSearchInput) freeSearchInput.value = fb.freeSearchInput || "";
  setFreeBrowseUi(true, fb.label || "");
  renderFreeList(state.freeListItems, { append: false });
  updateFreeShowMoreUi();
}

async function restoreNavigationEntry(entry) {
  if (entry.view === "search" && entry.search) {
    applySearchSessionState(entry.search);
    restoreContentScroll(entry, entry.search.scrollTop);
    return;
  }
  if (entry.view === "home") {
    if (entry.freeBrowse) {
      setView("home", { skipHomeRefresh: true });
      restoreFreeBrowseState(entry.freeBrowse);
      restoreContentScroll(entry);
      return;
    }
    exitFreeBrowse();
    setView("home", { skipHomeRefresh: true });
    restoreContentScroll(entry);
    return;
  }
  if (entry.view === "explore") {
    setView("explore", { skipExploreRefresh: true });
    restoreContentScroll(entry);
    return;
  }
  if (entry.view === "history") {
    setView("history", { skipHistoryRefresh: true });
    restoreContentScroll(entry);
    return;
  }
  setView(entry.view, {
    skipHomeRefresh: true,
    skipExploreRefresh: true,
    skipHistoryRefresh: true,
  });
  restoreContentScroll(entry);
}

function popNavigationReturn() {
  const entry = viewReturnStack.pop();
  updateNavigationBackUi();
  if (!entry) return;
  navigationRestoring = true;
  try {
    void restoreNavigationEntry(entry);
  } finally {
    navigationRestoring = false;
    updateNavigationBackUi();
  }
}

function navigateBackUi() {
  if (!navigationBackAvailable()) return;
  popNavigationReturn();
  if (isMobileUi()) {
    navigationIgnoreNextPop = true;
    try {
      history.back();
    } catch {
      navigationIgnoreNextPop = false;
    }
  }
}

function pushMobileBackState() {
  if (!isMobileUi()) return;
  try {
    history.pushState({ rutsfyBack: 1 }, "", window.location.href);
  } catch {
    /* ignore */
  }
}

function showBackExitToast() {
  if (!backExitToast) return;
  backExitToast.classList.remove("hidden");
  window.clearTimeout(showBackExitToast._hideTimer);
  showBackExitToast._hideTimer = window.setTimeout(() => {
    backExitToast.classList.add("hidden");
  }, 2600);
}

function disarmMobileBackExit() {
  mobileBackExitArmed = false;
  if (mobileBackExitArmTimer) {
    window.clearTimeout(mobileBackExitArmTimer);
    mobileBackExitArmTimer = null;
  }
}

function armMobileBackExit() {
  mobileBackExitArmed = true;
  if (mobileBackExitArmTimer) window.clearTimeout(mobileBackExitArmTimer);
  mobileBackExitArmTimer = window.setTimeout(disarmMobileBackExit, 2500);
}

function dismissMobileBackOverlay() {
  if (state.userMenuOpen) {
    closeUserMenu();
    return true;
  }
  for (const el of [accountModal, customizeModal]) {
    if (el && !el.classList.contains("hidden")) {
      closeModal(el);
      return true;
    }
  }
  const pwaBanner = document.getElementById("pwa-install-banner");
  if (pwaBanner && !pwaBanner.classList.contains("hidden")) {
    pwaBanner.classList.add("hidden");
    return true;
  }
  return false;
}

function handleMobileBackNavigation() {
  if (!isMobileUi()) return;

  if (dismissMobileBackOverlay()) {
    pushMobileBackState();
    return;
  }

  if (state.view === "explore" && state.deezerStack.length) {
    disarmMobileBackExit();
    state.deezerStack.pop();
    void restoreDeezerBrowse().catch(() => {});
    pushMobileBackState();
    return;
  }

  if (navigationBackAvailable()) {
    disarmMobileBackExit();
    popNavigationReturn();
    return;
  }

  if (document.body.classList.contains("auth-locked")) {
    if (mobileBackExitArmed) {
      disarmMobileBackExit();
      history.back();
      return;
    }
    showBackExitToast();
    armMobileBackExit();
    pushMobileBackState();
    return;
  }

  if (state.view === "nowplaying") {
    disarmMobileBackExit();
    closeNowPlaying();
    pushMobileBackState();
    return;
  }

  if (state.view !== "home") {
    disarmMobileBackExit();
    setView("home");
    pushMobileBackState();
    return;
  }

  if (mobileBackExitArmed) {
    disarmMobileBackExit();
    history.back();
    return;
  }
  showBackExitToast();
  armMobileBackExit();
  pushMobileBackState();
}

function bindMobileBackNavigation() {
  if (mobileBackBound || !isMobileUi()) return;
  mobileBackBound = true;
  pushMobileBackState();
  window.addEventListener("popstate", () => {
    if (navigationIgnoreNextPop) {
      navigationIgnoreNextPop = false;
      return;
    }
    handleMobileBackNavigation();
  });
}

/** No celular artista/canal só informa — toque na faixa toca (sem abrir busca). */
function artistCreditSearchEnabled() {
  return !isMobileUi();
}

const CREDIT_LABEL_DISPLAY_MAX = 28;

function creditDisplayLabel(label) {
  const t = (label || "").trim();
  if (t.length <= CREDIT_LABEL_DISPLAY_MAX) return t;
  return `${t.slice(0, CREDIT_LABEL_DISPLAY_MAX - 1).trim()}…`;
}

function creditFullTitle(credit) {
  if (!credit?.label) return "";
  return creditActionTitle(credit) || credit.label;
}

function artistCreditInnerHtml(credit) {
  if (!credit.label) {
    return `<span class="track-artist">—</span>`;
  }
  const shown = escapeHtml(creditDisplayLabel(credit.label));
  const tip = escapeHtml(creditFullTitle(credit));
  if (!artistCreditSearchEnabled()) {
    return `<span class="track-artist track-artist-static" title="${tip}">${shown}</span>`;
  }
  return `<button type="button" class="track-artist-btn" data-search-query="${escapeHtml(credit.query)}" data-credit-kind="${escapeHtml(credit.kind || "")}" data-channel-id="${escapeHtml(credit.channelId || "")}" title="${tip}">${shown}</button>`;
}

function bindTrackArtistCreditButton(row) {
  const btn = row.querySelector(".track-artist-btn");
  if (!btn || !artistCreditSearchEnabled()) return;
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    void runCreditSearch({
      label: btn.textContent,
      query: btn.dataset.searchQuery || btn.textContent,
      kind: btn.dataset.creditKind || "",
      channelId: btn.dataset.channelId || "",
    });
  });
}

async function runCreditSearch(credit) {
  if (!credit?.label) return;
  await runTextSearch(credit.query || credit.label);
}

function buildSearchFetchUrl() {
  if (state.searchChannelId) {
    const url = new URL(
      rutUrl(`/api/channel/${encodeURIComponent(state.searchChannelId)}/videos`),
      window.location.origin
    );
    url.searchParams.set("light", "1");
    url.searchParams.set("max_results", String(SEARCH_API_BATCH));
    return url;
  }
  const url = new URL(rutUrl("/api/search"), window.location.origin);
  applySearchApiParams(url);
  return url;
}

function setCatalogEntityCover(img, subtitleEl, picture, subtitle) {
  if (img) {
    const url = String(picture || "").trim();
    if (url) {
      img.src = url;
      img.classList.remove("hidden");
    } else {
      img.removeAttribute("src");
      img.classList.add("hidden");
    }
  }
  if (subtitleEl) {
    const text = String(subtitle || "").trim();
    subtitleEl.textContent = text;
    subtitleEl.classList.toggle("hidden", !text);
  }
}

function clearSearchEntityCover() {
  setCatalogEntityCover(searchEntityCover, searchEntitySub, "", "");
}

function clearDeezerEntityCover() {
  setCatalogEntityCover(deezerCoverEl, deezerSubtitleEl, "", "");
}

function clearSearchCatalogChrome(catalog) {
  if (searchCatalogEl) searchCatalogEl.innerHTML = "";
  if (searchTracksLabelEl) {
    searchTracksLabelEl.textContent = "";
    searchTracksLabelEl.closest(".catalog-list-heading")?.classList.add("hidden");
  }
  if (searchColAlbumEl) searchColAlbumEl.textContent = catalog ? "Álbum" : "Descrição";
  if (!catalog) state.deezerTracks = state.deezerTracks || [];
}

function renderSearchCatalogTracks(tracks, label) {
  const list = Array.isArray(tracks) ? tracks : [];
  state.deezerTracks = list;
  searchListTracks = list;
  if (searchTracksLabelEl) {
    searchTracksLabelEl.textContent = label || "";
    searchTracksLabelEl.closest(".catalog-list-heading")?.classList.toggle("hidden", !label || !list.length);
  }
  if (searchColAlbumEl) searchColAlbumEl.textContent = "Álbum";
  resultsEl.innerHTML = "";
  list.forEach((item, index) => {
    resultsEl.appendChild(buildTrackRow(item, index, { mode: "deezer" }));
  });
  searchShowMore?.classList.add("hidden");
  setSearchTrackHeadVisible(list.length > 0);
  scheduleKnownDeezerAudio(list);
  syncCatalogListPlayButtons();
}

function paintSearchCatalog(data, heading) {
  clearSearchEntityCover();
  if (searchCatalogEl) searchCatalogEl.innerHTML = "";
  const artists = data.artists || [];
  const albums = data.albums || [];
  if (searchCatalogEl && artists.length) {
    appendShelfSection(searchCatalogEl, "Artistas", "search-artists", () =>
      artists.map((a) => deezerCard("artist", a.id, a.name, a.picture, ""))
    );
  }
  if (searchCatalogEl && albums.length) {
    appendShelfSection(searchCatalogEl, "Álbuns", "search-albums", () =>
      albums.map((a) => deezerCard("album", a.id, a.title, a.picture, a.subtitle || a.releaseDate || ""))
    );
  }
  const label = data.artist?.name ? "Mais tocadas" : "Faixas";
  renderSearchCatalogTracks(data.tracks || [], label);
  if (heading) searchHeading.textContent = heading;
  if (!artists.length && !albums.length && !(data.tracks || []).length) {
    setStatus("Nenhum resultado.", { loading: false });
    return;
  }
  setStatus("", { loading: false });
}

async function showSearchCatalog(term) {
  setStatus("Procurando…", { loading: true });
  const data = await deezerGet(`/api/catalog/deezer/search?q=${encodeURIComponent(term)}`);
  state.lastSearchCatalog = data;
  state.catalogOrigin = data.artist?.id
    ? { kind: "artist", id: String(data.artist.id), title: data.artist.name || term }
    : null;
  const heading = data.artist?.name || term;
  paintSearchCatalog(data, heading);
}

async function openSearchCatalogLevel(kind, id, title) {
  if (id == null || id === "") return;
  state.catalogOrigin = { kind, id: String(id), title: title || "" };
  setView("search", { skipSearchFocus: true });
  searchHeading.textContent = title || "Catálogo";
  clearSearchEntityCover();
  setStatus("Carregando…", { loading: true });
  if (searchCatalogEl) searchCatalogEl.innerHTML = "";
  resultsEl.innerHTML = "";
  const encoded = encodeURIComponent(id);
  let data;
  if (
    kind === "artist" &&
    state.lastSearchCatalog?.artist?.id != null &&
    String(state.lastSearchCatalog.artist.id) === String(id) &&
    (state.lastSearchCatalog.tracks || []).length
  ) {
    paintSearchCatalog(state.lastSearchCatalog, state.lastSearchCatalog.artist?.name || title);
    setStatus("", { loading: false });
    return;
  }
  if (kind === "artist") data = await deezerGet(`/api/catalog/deezer/artists/${encoded}`);
  else if (kind === "album") data = await deezerGet(`/api/catalog/deezer/albums/${encoded}`);
  else if (kind === "playlist") data = await deezerGet(`/api/catalog/deezer/playlists/${encoded}`);
  else return;
  if (kind === "artist") {
    paintSearchCatalog(
      {
        artist: data.artist,
        artists: data.artist ? [data.artist] : [],
        albums: data.albums || [],
        tracks: data.tracks || [],
      },
      data.artist?.name || title
    );
    setStatus("", { loading: false });
    return;
  }
  if (searchCatalogEl) searchCatalogEl.innerHTML = "";
  const name = kind === "album" ? data.album?.title : data.playlist?.title;
  const picture = kind === "album" ? data.album?.picture : data.playlist?.picture;
  const subtitle = kind === "album" ? data.album?.artist : "";
  renderSearchCatalogTracks(data.tracks || [], kind === "album" ? data.album?.genre || "Faixas" : "Faixas");
  searchHeading.textContent = name || title || "Catálogo";
  setCatalogEntityCover(searchEntityCover, searchEntitySub, picture, subtitle);
  setStatus("", { loading: false });
}

async function runTextSearch(q) {
  const term = (q || "").trim();
  if (!term) return;
  const fromRecents =
    state.view === "search" && !state.searchQuery && !state.searchMixId && !state.searchChannelId;
  if (!fromRecents) pushNavigationReturn();
  input.value = term;
  setView("search", { skipSearchFocus: isMobileUi() });
  searchHeading.textContent = term;
  clearSearchEntityCover();
  setStatus("Procurando…", { loading: true });
  resultsEl.innerHTML = "";
  searchShowMore.classList.add("hidden");
  state.searchLoadingMore = false;
  clearSearchFilters();
  state.searchQuery = term;
  recordRecentSearch({ q: term, label: term });
  try {
    await showSearchCatalog(term);
  } catch (err) {
    setStatus(err.message || "Erro na busca", { error: true, loading: false });
  }
}

async function runChannelVideos(_channelId, title) {
  await runTextSearch(title || "");
}

function isInLibrary(videoId) {
  return state.library.has(videoId);
}

function updateLibraryButtons() {
  document.querySelectorAll(".btn-add-lib[data-video-id]").forEach((btn) => {
    const id = btn.dataset.videoId;
    const saved = isInLibrary(id);
    btn.classList.toggle("saved", saved);
    btn.textContent = saved ? "✓" : "+";
    btn.title = saved ? "Remover da biblioteca" : "Adicionar à biblioteca";
  });
  if (state.current?.videoId && btnLibrary) {
    const saved = isInLibrary(state.current.videoId);
    btnLibrary.classList.toggle("saved", saved);
    btnLibrary.textContent = saved ? "✓" : "+";
    btnLibrary.title = saved ? "Remover da biblioteca" : "Adicionar à biblioteca";
  }
}

function restorePlayerChromeToBar() {
  if (!playerBar || !playerCenter) return;
  playerBar.classList.remove("hidden");
  const audioEl = document.getElementById("audio");
  if (audioEl) {
    if (!playerBar.contains(playerCenter)) playerBar.insertBefore(playerCenter, audioEl);
    if (playerExtra && !playerBar.contains(playerExtra)) playerBar.insertBefore(playerExtra, audioEl);
  }
  if (btnLibrary && playerNowEl && !playerNowEl.contains(btnLibrary)) {
    playerNowEl.appendChild(btnLibrary);
  }
}

function nowPlayingScrollThreshold() {
  const hero = document.querySelector(".np-hero");
  if (!hero) return 96;
  return Math.min(Math.max(hero.offsetHeight * 0.28, 72), 220);
}

function updateNowPlayingLayoutFromScroll() {
  if (state.view !== "nowplaying") return;
  const scroller = document.querySelector(".np-scroll");
  if (!scroller) return;
  const showFooter = scroller.scrollTop > nowPlayingScrollThreshold();
  if (showFooter === state.npFooterPlayer) return;
  state.npFooterPlayer = showFooter;
  applyNowPlayingChromeLayout();
}

function bindNowPlayingScroll() {
  const scroller = document.querySelector(".np-scroll");
  if (!scroller || scroller.dataset.npScrollBound === "1") return;
  scroller.dataset.npScrollBound = "1";
  scroller.addEventListener(
    "scroll",
    () => {
      window.requestAnimationFrame(updateNowPlayingLayoutFromScroll);
    },
    { passive: true }
  );
  bindNowPlayingPullToClose(scroller);
}

function bindNowPlayingPullToClose(scroller) {
  const sheet = views.nowplaying;
  if (!sheet || scroller.dataset.npPullBound === "1") return;
  scroller.dataset.npPullBound = "1";

  const blocked = (target) =>
    target instanceof Element &&
    target.closest("button, a, input, textarea, select, .seek-wrap, .volume-wrap");

  const begin = (clientY, clientX, target) => {
    if (npClosing || state.view !== "nowplaying") return false;
    if (scroller.scrollTop > 4) return false;
    if (blocked(target)) return false;
    npPull = {
      y: clientY,
      x: clientX,
      lastY: clientY,
      lastT: performance.now(),
      active: false,
      dy: 0,
      vy: 0,
    };
    return true;
  };

  const move = (clientY, clientX, event) => {
    if (!npPull || npClosing) return;
    const dy = clientY - npPull.y;
    const dx = clientX - npPull.x;
    if (!npPull.active) {
      if (scroller.scrollTop > 4 || dy < 8) return;
      if (Math.abs(dx) > dy) {
        npPull = null;
        return;
      }
      npPull.active = true;
      sheet.classList.add("is-dragging");
    }
    if (event.cancelable) event.preventDefault();
    const now = performance.now();
    npPull.vy = (clientY - npPull.lastY) / Math.max(16, now - npPull.lastT);
    npPull.lastY = clientY;
    npPull.lastT = now;
    npPull.dy = Math.max(0, dy);
    sheet.style.transition = "none";
    sheet.style.transform = `translateY(${npPull.dy}px)`;
  };

  const end = () => {
    if (!npPull) return;
    const gesture = npPull;
    npPull = null;
    sheet.classList.remove("is-dragging");
    if (!gesture.active) return;
    if (gesture.dy > 70 || gesture.vy > 0.4) {
      closeNowPlaying();
      return;
    }
    sheet.style.transition = "transform 0.34s cubic-bezier(0.22, 1, 0.36, 1)";
    sheet.style.transform = "translateY(0)";
  };

  scroller.addEventListener(
    "touchstart",
    (e) => {
      if (e.touches.length !== 1) return;
      const t = e.touches[0];
      begin(t.clientY, t.clientX, e.target);
    },
    { passive: true }
  );
  scroller.addEventListener(
    "touchmove",
    (e) => {
      const t = e.touches[0];
      if (!t) return;
      move(t.clientY, t.clientX, e);
    },
    { passive: false }
  );
  scroller.addEventListener("touchend", end);
  scroller.addEventListener("touchcancel", end);

  scroller.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse" || e.button !== 0) return;
    if (!begin(e.clientY, e.clientX, e.target)) return;
    npPull.pointerId = e.pointerId;
  });
  scroller.addEventListener(
    "pointermove",
    (e) => {
      if (!npPull || e.pointerType !== "mouse" || e.pointerId !== npPull.pointerId) return;
      move(e.clientY, e.clientX, e);
    },
    { passive: false }
  );
  scroller.addEventListener("pointerup", (e) => {
    if (!npPull || e.pointerType !== "mouse" || e.pointerId !== npPull.pointerId) return;
    end();
  });
  scroller.addEventListener("pointercancel", (e) => {
    if (!npPull || e.pointerType !== "mouse") return;
    end();
  });
}

function applyNowPlayingChromeLayout() {
  if (!shellEl || !playerCenter || !npHeroControls) return;
  const onNowPlaying = state.view === "nowplaying";
  shellEl.classList.toggle("shell--np-expanded", onNowPlaying);
  shellEl.classList.toggle("shell--np-footer-player", onNowPlaying && state.npFooterPlayer);
  if (!onNowPlaying) {
    restorePlayerChromeToBar();
    return;
  }
  if (state.npFooterPlayer) {
    restorePlayerChromeToBar();
    window.requestAnimationFrame(pinNowPlayingSheet);
    return;
  }
  npHeroControls.appendChild(playerCenter);
  if (playerExtra) npHeroControls.appendChild(playerExtra);
  if (btnLibrary && npHeroActions) npHeroActions.appendChild(btnLibrary);
  playerBar?.classList.add("hidden");
  syncNpHeroFromPlayer();
  window.requestAnimationFrame(pinNowPlayingSheet);
}

function mountNowPlayingPlayerChrome(expanded) {
  if (!expanded) {
    state.npFooterPlayer = false;
  }
  applyNowPlayingChromeLayout();
}

function shouldStayOnNowPlayingQueue() {
  return state.view === "nowplaying" && state.npFooterPlayer;
}

function syncNpHeroFromPlayer() {
  if (!npHeroTitle) return;
  const item = state.current;
  const thumb = item ? higherResThumb(item.thumbnailUrl || "") : "";
  if (npHeroCover && npHeroCoverEmpty) {
    if (thumb) {
      npHeroCover.src = thumb;
      npHeroCover.classList.remove("hidden");
      npHeroCoverEmpty.classList.add("hidden");
    } else {
      npHeroCover.removeAttribute("src");
      npHeroCover.classList.add("hidden");
      npHeroCoverEmpty.classList.remove("hidden");
    }
  }
  npHeroTitle.textContent = item?.title || playerTitle?.textContent || "Selecione uma música";
  if (npHeroArtist && playerArtistBtn) {
    if (!playerArtistBtn.classList.contains("hidden") && playerArtistBtn.textContent) {
      npHeroArtist.textContent = playerArtistBtn.textContent;
      npHeroArtist.title = playerArtistBtn.title || "";
      npHeroArtist.dataset.searchQuery = playerArtistBtn.dataset.searchQuery || "";
      npHeroArtist.dataset.creditKind = playerArtistBtn.dataset.creditKind || "";
      npHeroArtist.dataset.channelId = playerArtistBtn.dataset.channelId || "";
      npHeroArtist.classList.remove("hidden");
    } else {
      npHeroArtist.textContent = "";
      npHeroArtist.classList.add("hidden");
    }
  }
}

function pinNowPlayingSheet() {
  if (npClosing || npPull?.active) return;
  const sheet = views.nowplaying;
  const content = contentScrollRoot();
  if (!sheet?.classList.contains("is-sheet") || !content || state.view !== "nowplaying") return;
  const rect = content.getBoundingClientRect();
  if (rect.width < 1 || rect.height < 1) return;
  sheet.style.position = "fixed";
  sheet.style.top = `${rect.top}px`;
  sheet.style.left = `${rect.left}px`;
  sheet.style.width = `${rect.width}px`;
  sheet.style.height = `${rect.height}px`;
  sheet.style.right = "auto";
  sheet.style.bottom = "auto";
}

function unpinNowPlayingSheet() {
  const sheet = views.nowplaying;
  if (!sheet) return;
  sheet.style.position = "";
  sheet.style.top = "";
  sheet.style.left = "";
  sheet.style.width = "";
  sheet.style.height = "";
  sheet.style.right = "";
  sheet.style.bottom = "";
}

window.addEventListener("resize", () => pinNowPlayingSheet(), { passive: true });
window.visualViewport?.addEventListener("resize", () => pinNowPlayingSheet(), { passive: true });
window.visualViewport?.addEventListener("scroll", () => pinNowPlayingSheet(), { passive: true });

let adminPane = "users";
let adminHistoryUser = null;
let lastNotedPlayId = "";

function notePlaybackStarted(item) {
  const id = item?.videoId;
  if (!id || id === lastNotedPlayId) return;
  lastNotedPlayId = id;
  fetch("/api/me/plays", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      videoId: id,
      title: item.title || "",
      artist: item.artist || "",
    }),
  }).catch(() => {});
}

function openAdminPanel() {
  closeUserMenu();
  adminPane = "users";
  adminHistoryUser = null;
  setView("admin");
}

function formatAdminWhen(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatAdminDay(isoDate) {
  const parts = String(isoDate || "").split("-");
  if (parts.length !== 3) return isoDate || "—";
  return `${parts[2]}/${parts[1]}`;
}

function syncAdminTabs() {
  document.querySelectorAll(".admin-tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.adminTab === adminPane);
  });
  document.getElementById("admin-users")?.classList.toggle("hidden", adminPane !== "users");
  document.getElementById("admin-stats")?.classList.toggle("hidden", adminPane !== "stats");
}

async function renderAdminPanel() {
  if (!state.user?.isAdmin) return;
  syncAdminTabs();
  if (adminPane === "stats") {
    await renderAdminStats();
    return;
  }
  if (adminHistoryUser) {
    await renderAdminUserHistory(adminHistoryUser);
    return;
  }
  await renderAdminUsers();
}

async function renderAdminUsers() {
  const root = document.getElementById("admin-users");
  if (!root) return;
  root.innerHTML = `<p class="status-line">Carregando usuários…</p>`;
  try {
    const res = await fetch("/api/admin/users");
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorDetail(data));
    const users = data.users || [];
    if (!users.length) {
      root.innerHTML = `<p class="status-line">Nenhum usuário.</p>`;
      return;
    }
    root.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Apelido</th>
            <th>Reproduções</th>
            <th>Último acesso</th>
            <th>Última faixa</th>
          </tr>
        </thead>
        <tbody>
          ${users
            .map(
              (user) => `
            <tr>
              <td><button type="button" class="admin-user-btn" data-admin-user="${escapeHtml(user.id)}">${escapeHtml(user.nickname || "Conta")}</button></td>
              <td>${Number(user.playCount) || 0}</td>
              <td>${escapeHtml(formatAdminWhen(user.lastAccessAt))}</td>
              <td>${escapeHtml(formatAdminWhen(user.lastPlayedAt))}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
    root.querySelectorAll("[data-admin-user]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.adminUser;
        adminHistoryUser = users.find((row) => row.id === id) || { id, nickname: btn.textContent };
        void renderAdminUserHistory(adminHistoryUser);
      });
    });
  } catch (err) {
    root.innerHTML = `<p class="status-line">${escapeHtml(err.message || "Não foi possível carregar")}</p>`;
  }
}

async function renderAdminUserHistory(user) {
  const root = document.getElementById("admin-users");
  if (!root) return;
  root.innerHTML = `<p class="status-line">Carregando histórico…</p>`;
  try {
    const res = await fetch(`/api/admin/users/${encodeURIComponent(user.id)}/history`);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorDetail(data));
    const items = data.items || [];
    const rows = items.length
      ? items
          .map(
            (item) => `
          <tr>
            <td>${escapeHtml(item.title || "Sem título")}</td>
            <td>${escapeHtml(item.artist || "—")}</td>
            <td>${escapeHtml(formatAdminWhen(item.lastPlayedAt))}</td>
          </tr>`
          )
          .join("")
      : `<tr><td colspan="3">Nenhuma reprodução ainda.</td></tr>`;
    root.innerHTML = `
      <button type="button" class="page-btn admin-back" id="admin-history-back">← Usuários</button>
      <h2 class="admin-block-title">Histórico de ${escapeHtml(data.user?.nickname || user.nickname || "usuário")}</h2>
      <table class="admin-table">
        <thead><tr><th>Faixa</th><th>Artista</th><th>Quando</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
    document.getElementById("admin-history-back")?.addEventListener("click", () => {
      adminHistoryUser = null;
      void renderAdminUsers();
    });
  } catch (err) {
    root.innerHTML = `<p class="status-line">${escapeHtml(err.message || "Não foi possível carregar")}</p>`;
  }
}

async function renderAdminStats() {
  const root = document.getElementById("admin-stats");
  if (!root) return;
  root.innerHTML = `<p class="status-line">Carregando estatísticas…</p>`;
  try {
    const res = await fetch("/api/admin/stats");
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorDetail(data));
    const cards = [
      ["Usuários", data.users],
      ["Acessos hoje", data.visitsToday],
      ["Logins hoje", data.loginsToday],
      ["Reproduções hoje", data.playsToday],
      ["Buscas hoje", data.searchesToday],
      ["Reproduções em 7 dias", data.plays7d],
    ];
    const days = (data.days || [])
      .map(
        (day) => `
      <tr>
        <td>${escapeHtml(formatAdminDay(day.date))}</td>
        <td>${Number(day.visits) || 0}</td>
        <td>${Number(day.logins) || 0}</td>
        <td>${Number(day.plays) || 0}</td>
        <td>${Number(day.searches) || 0}</td>
      </tr>`
      )
      .join("");
    const tracks = (data.topTracks || []).length
      ? data.topTracks
          .map(
            (track) => `
          <tr>
            <td>${escapeHtml(track.title || "Sem título")}</td>
            <td>${escapeHtml(track.artist || "—")}</td>
            <td>${Number(track.plays) || 0}</td>
          </tr>`
          )
          .join("")
      : `<tr><td colspan="3">Ainda sem reproduções.</td></tr>`;
    const people = (data.topUsers || []).length
      ? data.topUsers
          .map(
            (person) => `
          <tr>
            <td>${escapeHtml(person.nickname || "Conta")}</td>
            <td>${Number(person.plays) || 0}</td>
          </tr>`
          )
          .join("")
      : `<tr><td colspan="2">Ainda sem reproduções.</td></tr>`;
    root.innerHTML = `
      <div class="admin-stats-grid">
        ${cards
          .map(
            ([label, value]) => `
          <div class="admin-stat">
            <span class="admin-stat-value">${Number(value) || 0}</span>
            <span class="admin-stat-label">${escapeHtml(label)}</span>
          </div>`
          )
          .join("")}
      </div>
      <h2 class="admin-block-title">Últimos 14 dias</h2>
      <table class="admin-table">
        <thead><tr><th>Dia</th><th>Acessos</th><th>Logins</th><th>Reproduções</th><th>Buscas</th></tr></thead>
        <tbody>${days}</tbody>
      </table>
      <h2 class="admin-block-title">Faixas mais ouvidas</h2>
      <table class="admin-table">
        <thead><tr><th>Faixa</th><th>Artista</th><th>Vezes</th></tr></thead>
        <tbody>${tracks}</tbody>
      </table>
      <h2 class="admin-block-title">Quem mais ouve</h2>
      <table class="admin-table">
        <thead><tr><th>Usuário</th><th>Reproduções</th></tr></thead>
        <tbody>${people}</tbody>
      </table>`;
  } catch (err) {
    root.innerHTML = `<p class="status-line">${escapeHtml(err.message || "Não foi possível carregar")}</p>`;
  }
}

document.querySelectorAll(".admin-tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    adminPane = btn.dataset.adminTab || "users";
    if (adminPane === "users") adminHistoryUser = null;
    if (state.view === "admin") void renderAdminPanel();
    else syncAdminTabs();
  });
});

function setView(name, opts = {}) {
  if (name === "library" || name === "free") name = "home";
  if (name === "admin" && !state.user?.isAdmin) name = "home";
  if (name !== "home") {
    disarmMobileBackExit();
  }
  if (name !== "nowplaying") {
    state.npFooterPlayer = false;
  }
  if (name === "nowplaying" && state.view !== "nowplaying") {
    viewBeforeNowPlaying = state.view === "nowplaying" ? viewBeforeNowPlaying : state.view;
  }
  if (name === "search" && state.view !== "search" && state.view !== "nowplaying") {
    viewBeforeSearch = state.view || "home";
  }
  const prevView = state.view;
  const switching = prevView !== name;
  state.view = name;
  mountNowPlayingPlayerChrome(name === "nowplaying");
  const under = name === "nowplaying" ? viewBeforeNowPlaying || "home" : null;
  const pageSwitch =
    switching &&
    opts.animate !== false &&
    prevView &&
    prevView !== "nowplaying" &&
    name !== "nowplaying" &&
    views[prevView] &&
    views[name] &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (pageSwitch) {
    window.clearTimeout(viewAnimTimer);
    for (const [key, el] of Object.entries(views)) {
      el.classList.remove("view-leave", "view-enter");
      el.classList.toggle("hidden", key !== name && key !== prevView);
    }
    const fromEl = views[prevView];
    const toEl = views[name];
    fromEl.classList.add("view-leave");
    void toEl.offsetWidth;
    toEl.classList.add("view-enter");
    viewAnimTimer = window.setTimeout(() => {
      if (state.view !== name) return;
      fromEl.classList.remove("view-leave");
      fromEl.classList.add("hidden");
      toEl.classList.remove("view-enter");
    }, 460);
  } else {
    for (const [key, el] of Object.entries(views)) {
      el.classList.remove("view-leave", "view-enter");
      el.classList.toggle("hidden", !(key === name || key === under));
    }
  }
  const sheet = views.nowplaying;
  if (sheet) {
    if (name === "nowplaying") {
      sheet.classList.add("is-sheet");
      sheet.classList.remove("is-closing", "is-dragging");
      pinNowPlayingSheet();
      if (switching && !npPull) {
        const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reduce) {
          sheet.style.transition = "";
          sheet.style.transform = "";
        } else {
          sheet.style.transition = "none";
          sheet.style.transform = "translateY(100%)";
          void sheet.offsetWidth;
          window.requestAnimationFrame(() => {
            window.requestAnimationFrame(() => {
              if (state.view !== "nowplaying" || npPull?.active) return;
              sheet.style.transition = "transform 0.46s cubic-bezier(0.22, 1, 0.36, 1)";
              sheet.style.transform = "translateY(0)";
            });
          });
        }
      }
    } else {
      sheet.classList.remove("is-sheet", "is-closing", "is-dragging");
      sheet.style.transition = "";
      sheet.style.transform = "";
      unpinNowPlayingSheet();
    }
  }
  let navView = name === "nowplaying" ? viewBeforeNowPlaying || "home" : name;
  if (navView === "search" || navView === "nowplaying") navView = viewBeforeSearch || "home";
  if (name === "admin") navView = "";
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === navView);
  });
  if (name === "search" && !opts.keepSearchFocus) {
    if (opts.skipSearchFocus) {
      input.blur();
    } else if (isMobileUi()) {
      if (opts.focusSearch) input.focus();
      else input.blur();
    } else if (!opts.skipSearchFocus) {
      input.focus();
    }
  }
  if (name === "search" && state.searchCatalog.length) {
    requestAnimationFrame(() => bindLazyHydrateRows());
  }
  if (name === "home" && !opts.skipHomeRefresh) void refreshHome();
  if (name === "explore" && !opts.skipExploreRefresh) refreshExplore();
  if (name === "nowplaying") {
    renderNowPlaying();
    bindNowPlayingScroll();
    window.requestAnimationFrame(updateNowPlayingLayoutFromScroll);
  }
  if (name === "history" && !opts.skipHistoryRefresh) void refreshHistory();
  if (name === "admin") void renderAdminPanel();
  if (name === "search") updateSearchSaveButton();
  if (exploreCatFooter) exploreCatFooter.hidden = true;
  updateNavigationBackUi();
}

function nowPlayingOriginLabel() {
  const ctx = state.playbackContext;
  if (!ctx) {
    if (state.queueSource === "history") return "Recentes";
    if (state.queueSource === "library") return "Biblioteca";
    if (state.queueSource === "free") return state.freeBrowseLabel || "Grátis no servidor";
    if (state.queueSource === "search") {
      if (state.searchMixId) {
        const mix = findMixById(state.searchMixId);
        if (mix?.label) return mix.label;
      }
      return state.searchQuery || "Busca";
    }
    return "";
  }
  if (ctx.source === "deezer" && (ctx.catalogOrigin?.title || state.catalogOrigin?.title)) {
    return ctx.catalogOrigin?.title || state.catalogOrigin.title;
  }
  if (ctx.source === "history") return "Recentes";
  if (ctx.source === "library") return "Biblioteca";
  if (ctx.searchMixId) {
    const mix = findMixById(ctx.searchMixId);
    if (mix?.label) return mix.label;
  }
  return ctx.searchHeading || ctx.searchQuery || "Busca";
}

function renderNowPlaying() {
  if (!nowPlayingList) return;
  const origin = nowPlayingOriginLabel();
  const n = state.queue.length;
  if (nowPlayingSub) {
    if (!n) {
      nowPlayingSub.textContent = "Toque algo para montar a fila.";
    } else if (origin) {
      nowPlayingSub.textContent = `${n} faixa${n > 1 ? "s" : ""} · de ${origin}`;
    } else {
      nowPlayingSub.textContent = `${n} faixa${n > 1 ? "s" : ""} na fila`;
    }
  }
  nowPlayingList.innerHTML = "";
  if (npScrollToPlayingBtn) {
    npScrollToPlayingBtn.disabled = !state.playingId || !n;
  }
  if (!n) {
    nowPlayingList.innerHTML = "<li class=\"status-line\">Nada tocando ainda.</li>";
    updateCatalogShowMoreUi();
    return;
  }
  state.queue.forEach((item, i) => {
    nowPlayingList.appendChild(buildTrackRow(item, i, { mode: "queue" }));
  });
  highlightPlayingRows();
  updateLibraryButtons();
  updateTrackRowLoadingStates();
  updateCatalogShowMoreUi();
  scheduleKnownDeezerAudio(state.queue);
}

function findMixById(mixId) {
  if (!mixId) return null;
  for (const cat of state.exploreCategories) {
    for (const mix of cat.mixes || []) {
      if (mix.id === mixId) return mix;
    }
  }
  return null;
}

function isSameSearchSession(ctx) {
  if (!ctx || ctx.source !== "search") return false;
  return (
    (ctx.searchMixId || null) === (state.searchMixId || null) &&
    (ctx.searchQuery || "") === (state.searchQuery || "") &&
    (ctx.searchPublishedAfter || null) === (state.searchPublishedAfter || null) &&
    (ctx.searchPublishedBefore || null) === (state.searchPublishedBefore || null) &&
    (ctx.searchOrder || null) === (state.searchOrder || null)
  );
}

function shouldBindSearchResultsToQueue() {
  const videoId = state.playingId || state.current?.videoId;
  if (!videoId || !state.queue.length || state.queueIndex < 0) return true;
  if (state.queueSource !== "search") return false;
  const ctx = state.playbackContext;
  if (!ctx || ctx.source !== "search") return false;
  return isSameSearchSession(ctx);
}

function snapshotPlaybackContext(source) {
  const origin = state.catalogOrigin || state.playbackContext?.catalogOrigin || null;
  if (source !== "search" && source !== "history" && source !== "library") {
    state.playbackContext = {
      source: source || "deezer",
      catalogOrigin: origin,
      searchHeading: origin?.title || "",
      queueIndex: state.queueIndex,
    };
    return;
  }
  const ctx = {
    source,
    searchQuery: state.searchQuery,
    searchMixId: state.searchMixId,
    searchPublishedAfter: state.searchPublishedAfter,
    searchPublishedBefore: state.searchPublishedBefore,
    searchOrder: state.searchOrder,
    searchHeading: searchHeading.textContent,
    searchCatalog: state.searchCatalog.map((i) => ({ ...i })),
    searchVisibleCount: state.searchVisibleCount,
    searchNextPageToken: state.searchNextPageToken,
    searchMixCatalogTotal: state.searchMixCatalogTotal,
    searchHydrated: [...state.searchHydrated],
    catalogOrigin: origin,
    queue: state.queue.map((i) => ({ ...i })),
    queueIndex: state.queueIndex,
  };
  state.playbackContext = ctx;
}

function applyPlaybackContext(ctx) {
  if (!ctx) return;
  state.queueSource = ctx.source;
  if (ctx.source === "search") {
    state.searchQuery = ctx.searchQuery ?? "";
    state.searchMixId = ctx.searchMixId ?? null;
    state.searchPublishedAfter = ctx.searchPublishedAfter ?? null;
    state.searchPublishedBefore = ctx.searchPublishedBefore ?? null;
    state.searchOrder = ctx.searchOrder ?? null;
    state.searchCatalog = (ctx.searchCatalog || []).map((i) => ({ ...i }));
    state.searchVisibleCount = ctx.searchVisibleCount ?? 0;
    state.searchNextPageToken = ctx.searchNextPageToken ?? null;
    state.searchMixCatalogTotal = ctx.searchMixCatalogTotal ?? 0;
    state.searchHydrated = new Set(ctx.searchHydrated || []);
    searchHeading.textContent = ctx.searchHeading || state.searchQuery || "Buscar";
    clearSearchEntityCover();
    syncSearchInputFromState();
    compactSearchCatalog();
  }
  const liveId = state.playingId || state.current?.videoId;
  const liveQueueOk =
    state.queue.length > 0 && liveId && state.queue.some((i) => i.videoId === liveId);
  if (liveQueueOk) {
    const idx = state.queue.findIndex((i) => i.videoId === liveId);
    if (idx >= 0) state.queueIndex = idx;
  } else if (ctx.queue?.length) {
    state.queue = ctx.queue.map((i) => ({ ...i }));
    const idx = liveId ? state.queue.findIndex((i) => i.videoId === liveId) : ctx.queueIndex;
    state.queueIndex = idx >= 0 ? idx : ctx.queueIndex >= 0 ? ctx.queueIndex : 0;
  }
  rebuildPlayOrder();
  updateTransportControls();
}

function resolvePlaybackListView() {
  const videoId = state.playingId || state.current?.videoId;
  if (!videoId) return null;

  if (state.playbackContext?.source) return state.playbackContext.source;

  const source = state.queueSource;
  if (source === "search" || source === "history" || source === "library") {
    return source;
  }
  if (state.searchCatalog.some((i) => i.videoId === videoId)) return "search";
  if (state.historyItems.some((i) => i.videoId === videoId)) return "history";
  if (state.libraryItems.some((i) => i.videoId === videoId)) return "library";
  return null;
}

function syncSearchInputFromState() {
  if (state.searchMixId) {
    input.value = "";
    return;
  }
  input.value = state.searchQuery || "";
}

function restoreSearchViewUi() {
  const mix = state.searchMixId ? findMixById(state.searchMixId) : null;
  if (mix) {
    searchHeading.textContent = mix.label || state.searchQuery || "Buscar";
  } else {
    searchHeading.textContent = state.searchQuery || "Buscar";
  }
  clearSearchEntityCover();
  syncSearchInputFromState();
  searchShowMore.classList.toggle("hidden", !state.searchCatalog.length);
  if (state.searchCatalog.length) {
    renderSearchVisible();
  } else if (!state.searchQuery && !state.searchMixId && !state.searchChannelId) {
    renderSearchRecents();
  } else {
    resultsEl.innerHTML = "";
    setStatus("");
  }
}

function scrollPlayingRowIntoView() {
  if (!state.playingId) return;
  requestAnimationFrame(() => {
    const row =
      document.querySelector("#now-playing-list .track-row.playing") ||
      document.querySelector(".track-row.playing");
    row?.scrollIntoView({ block: "center", behavior: "smooth" });
  });
}

function scrollNowPlayingToHero(behavior = "smooth") {
  requestAnimationFrame(() => {
    const scroller = document.querySelector(".np-scroll");
    if (scroller) scroller.scrollTo({ top: 0, behavior });
    state.npFooterPlayer = false;
    if (state.view === "nowplaying") applyNowPlayingChromeLayout();
  });
}

function finishCloseNowPlaying() {
  const back =
    viewBeforeNowPlaying && viewBeforeNowPlaying !== "nowplaying" ? viewBeforeNowPlaying : "home";
  setView(back, {
    animate: false,
    skipHomeRefresh: true,
    skipExploreRefresh: true,
    skipHistoryRefresh: true,
    skipSearchFocus: true,
  });
}

function closeNowPlaying() {
  const sheet = views.nowplaying;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!sheet || state.view !== "nowplaying" || sheet.classList.contains("hidden") || reduceMotion) {
    npClosing = false;
    finishCloseNowPlaying();
    return;
  }
  if (npClosing) return;
  npClosing = true;
  npPull = null;
  sheet.classList.add("is-closing");
  sheet.classList.remove("is-dragging");
  const from = sheet.style.transform || "translateY(0px)";
  sheet.style.transition = "none";
  sheet.style.transform = from;
  sheet.getBoundingClientRect();
  sheet.style.transition = "transform 0.36s cubic-bezier(0.22, 1, 0.36, 1)";
  sheet.style.transform = "translateY(100%)";
  let settled = false;
  const done = (event) => {
    if (settled) return;
    if (event && event.propertyName && event.propertyName !== "transform") return;
    settled = true;
    sheet.removeEventListener("transitionend", done);
    npClosing = false;
    finishCloseNowPlaying();
  };
  sheet.addEventListener("transitionend", done);
  window.setTimeout(done, 460);
}

/** Tela cheia Reproduzindo (capa + controles), não só a lista da fila. */
function openNowPlaying(opts = {}) {
  const { scrollToQueueTrack = false, scrollBehavior = "smooth", applySearchContext = true } = opts;
  const videoId = state.playingId || state.current?.videoId;
  if (applySearchContext && videoId && state.playbackContext?.source === "search") {
    applyPlaybackContext(state.playbackContext);
  }
  setView("nowplaying", { skipExploreRefresh: true });
  if (scrollToQueueTrack && state.playingId) {
    scrollPlayingRowIntoView();
  } else {
    scrollNowPlayingToHero(scrollBehavior);
  }
}

function goToPlaybackSource() {
  const videoId = state.playingId || state.current?.videoId;
  if (!videoId) return;
  openNowPlaying();
}

function updatePlayerSourceLink() {
  if (!playerSourceBtn) return;
  const hasTrack = Boolean(state.current?.videoId);
  const canOpenPlayer = Boolean(state.playingId || hasTrack);
  const canPlayLast = hasTrack && !audio.src;
  playerSourceBtn.disabled = !canOpenPlayer && !canPlayLast;
  if (canOpenPlayer) {
    playerSourceBtn.title = "Abrir Reproduzindo";
  } else if (canPlayLast) {
    playerSourceBtn.title = "Tocar última faixa";
  } else {
    playerSourceBtn.title = "Selecione uma música";
  }
}

function readLastListenRaw() {
  if (!state.user?.id) return null;
  try {
    const raw = localStorage.getItem(userStorageKey(USER_LAST_LISTEN_KEY));
    if (!raw) return null;
    const data = JSON.parse(raw);
    return data && typeof data === "object" ? data : null;
  } catch {
    return null;
  }
}

function slimQueueItemForStorage(item) {
  if (!item?.videoId && !item?.deezerId) return null;
  return {
    videoId: item.videoId || "",
    deezerId: item.deezerId || null,
    title: item.title,
    artist: item.artist,
    artistId: item.artistId || null,
    album: item.album || "",
    albumId: item.albumId || null,
    genre: item.genre || "",
    catalogSource: item.catalogSource || "",
    channelId: item.channelId,
    channelTitle: item.channelTitle,
    thumbnailUrl: item.thumbnailUrl,
    duration: item.duration,
    url: item.url,
  };
}

function saveLastListen() {
  if (!state.user?.id) return;
  const item = state.current;
  if (!item?.videoId) return;
  let currentTime = 0;
  if (audio.src && Number.isFinite(audio.currentTime)) {
    currentTime = audio.currentTime;
  } else if (state.pendingResumeTime > 0) {
    currentTime = state.pendingResumeTime;
  }

  const queue = (state.queue.length ? state.queue : [item])
    .map(slimQueueItemForStorage)
    .filter(Boolean)
    .slice(0, 200);

  let queueIndex = state.queueIndex;
  if (queueIndex < 0 || queueIndex >= queue.length) {
    queueIndex = queue.findIndex((i) => i.videoId === item.videoId);
  }
  if (queueIndex < 0) queueIndex = 0;

  const ctx = state.playbackContext;
  const catalogOrigin = state.catalogOrigin || ctx?.catalogOrigin || null;
  const playbackContext = ctx
    ? {
        source: ctx.source,
        searchHeading: ctx.searchHeading,
        searchQuery: ctx.searchQuery,
        searchMixId: ctx.searchMixId,
        catalogOrigin,
      }
    : catalogOrigin
      ? { source: state.queueSource || "deezer", catalogOrigin }
      : null;

  const payload = {
    videoId: item.videoId,
    deezerId: item.deezerId || null,
    title: item.title,
    artist: item.artist,
    artistId: item.artistId || null,
    album: item.album || "",
    albumId: item.albumId || null,
    genre: item.genre || "",
    catalogSource: item.catalogSource || "",
    channelId: item.channelId,
    channelTitle: item.channelTitle,
    thumbnailUrl: item.thumbnailUrl,
    duration: item.duration,
    url: item.url,
    catalogOrigin,
    currentTime,
    queue,
    queueIndex,
    queueSource: state.queueSource,
    shuffle: state.shuffle,
    repeat: state.repeat,
    playbackContext,
    savedAt: Date.now(),
  };
  try {
    localStorage.setItem(userStorageKey(USER_LAST_LISTEN_KEY), JSON.stringify(payload));
  } catch {
    /* quota / privado */
  }
  schedulePrefsSync();
}

function scheduleSaveLastListen() {
  if (lastListenSaveTimer) return;
  lastListenSaveTimer = setTimeout(() => {
    lastListenSaveTimer = null;
    saveLastListen();
  }, 4000);
}

function loadUserVolume() {
  try {
    const raw = localStorage.getItem(userStorageKey(USER_VOLUME_KEY));
    if (raw == null || !volume) return;
    const n = Number(raw);
    if (!Number.isFinite(n)) return;
    const clamped = Math.max(0, Math.min(100, Math.round(n)));
    volume.value = String(clamped);
    audio.volume = clamped / 100;
    syncVolumeVisual();
  } catch {
    /* silencioso */
  }
}

function persistUserVolume() {
  if (!volume || !state.user?.id) return;
  try {
    localStorage.setItem(userStorageKey(USER_VOLUME_KEY), String(volume.value));
  } catch {
    /* silencioso */
  }
  schedulePrefsSync();
}

function mergeQueueItemWithHistory(qItem) {
  if (!qItem?.videoId) return qItem;
  const hist = state.history.get(qItem.videoId);
  return hist ? { ...qItem, ...hist } : qItem;
}

function restoreLastListenToPlayer() {
  const saved = readLastListenRaw();
  if (!saved?.videoId) return;

  let item = mergeQueueItemWithHistory({ ...saved });
  state.current = item;
  const t = Number(saved.currentTime);
  state.pendingResumeTime = Number.isFinite(t) && t > 3 ? t : 0;
  state.pendingResumeVideoId = state.pendingResumeTime > 0 ? item.videoId : null;
  state.playingId = item.videoId;

  state.catalogOrigin = saved.catalogOrigin || saved.playbackContext?.catalogOrigin || null;
  const storedQueue = Array.isArray(saved.queue)
    ? saved.queue.filter((i) => i?.videoId || i?.deezerId)
    : [];
  if (storedQueue.length) {
    state.queue = storedQueue.map((q) => mergeQueueItemWithHistory({ ...q }));
    let idx = Number(saved.queueIndex);
    if (!Number.isFinite(idx) || idx < 0 || idx >= state.queue.length) {
      idx = state.queue.findIndex((i) => i.videoId === item.videoId);
    }
    state.queueIndex = idx >= 0 ? idx : 0;
    state.queueSource = saved.queueSource || state.queueSource || "single";
    if (saved.playbackContext && typeof saved.playbackContext === "object") {
      state.playbackContext = { ...saved.playbackContext };
    }
    if (typeof saved.shuffle === "boolean") state.shuffle = saved.shuffle;
    if (saved.repeat === "off" || saved.repeat === "all" || saved.repeat === "one") {
      state.repeat = saved.repeat;
    }
    rebuildPlayOrder();
    updateTransportControls();
  } else {
    setPlaybackQueue([item], item.videoId, "single");
    state.playingId = item.videoId;
  }

  updatePlayerBar(item);
  updatePlayerSourceLink();
  renderNowPlaying();
  highlightPlayingRows();

  if (state.pendingResumeTime > 0) {
    timeCurrent.textContent = formatSeconds(state.pendingResumeTime);
    setPlayerStatus("Toque play para continuar");
  } else {
    setPlayerStatus("Toque play para ouvir de novo");
  }
  if (state.queue.length < 2) void expandPlaybackQueue();
}

function sameCatalogTrack(a, b) {
  if (!a || !b) return false;
  if (a.deezerId != null && b.deezerId != null && String(a.deezerId) === String(b.deezerId)) return true;
  if (a.videoId && b.videoId && a.videoId === b.videoId) return true;
  const titleA = (a.title || "").trim().toLowerCase();
  const titleB = (b.title || "").trim().toLowerCase();
  const artistA = (a.artist || "").trim().toLowerCase();
  const artistB = (b.artist || "").trim().toLowerCase();
  return Boolean(titleA && titleA === titleB && artistA && artistA === artistB);
}

async function tracksForOrigin(origin) {
  if (!origin?.kind || origin.id == null || origin.id === "") return [];
  const id = encodeURIComponent(origin.id);
  if (origin.kind === "artist") {
    const data = await deezerGet(`/api/catalog/deezer/artists/${id}`);
    return data.tracks || [];
  }
  if (origin.kind === "album") {
    const data = await deezerGet(`/api/catalog/deezer/albums/${id}`);
    return data.tracks || [];
  }
  if (origin.kind === "playlist") {
    const data = await deezerGet(`/api/catalog/deezer/playlists/${id}`);
    return data.tracks || [];
  }
  if (origin.kind === "genre" || origin.kind === "chart") {
    const data = await deezerGet(`/api/catalog/deezer/genres/${id}`);
    return data.tracks || [];
  }
  return [];
}

function queueAroundTrack(tracks, item) {
  const list = (tracks || []).filter((row) => row && (row.deezerId || row.videoId));
  if (!list.length) return [];
  let found = false;
  const merged = list.map((row) => {
    if (!sameCatalogTrack(row, item)) return row;
    found = true;
    return { ...row, ...item, deezerId: row.deezerId || item.deezerId };
  });
  if (!found) merged.unshift(item);
  return merged;
}

let expandQueueSeq = 0;

async function expandPlaybackQueue() {
  const item = state.current;
  if (!item || state.queue.length > 1) return;
  const seq = ++expandQueueSeq;
  let tracks = [];
  try {
    const origin = state.catalogOrigin;
    if (origin?.kind === "artist" || origin?.kind === "album" || origin?.kind === "playlist" || origin?.kind === "genre" || origin?.kind === "chart") {
      tracks = await tracksForOrigin(origin);
    }
    if (tracks.length < 2 && item.artistId && origin?.kind !== "artist") {
      tracks = await tracksForOrigin({ kind: "artist", id: item.artistId });
    }
    if (tracks.length < 2 && item.albumId && origin?.kind !== "album") {
      tracks = await tracksForOrigin({ kind: "album", id: item.albumId });
    }
    if (tracks.length < 2 && item.artist) {
      const data = await deezerGet(`/api/catalog/deezer/search?q=${encodeURIComponent(item.artist)}`);
      tracks = data.tracks || [];
    }
  } catch {
    return;
  }
  if (seq !== expandQueueSeq || !state.current || state.current.videoId !== item.videoId) return;
  const merged = queueAroundTrack(tracks, item);
  if (merged.length < 2) return;
  const key = item.videoId || (item.deezerId ? `dz:${item.deezerId}` : "");
  setPlaybackQueue(merged, key, "deezer");
  state.playingId = item.videoId;
  state.current = item;
  renderNowPlaying();
  highlightPlayingRows();
}

async function playCatalogOrigin(kind, id, title) {
  const origin = { kind, id: String(id), title: title || "" };
  state.catalogOrigin = origin;
  notePlayedOrigin(origin);
  setPlayerStatus("Montando a lista…");
  setGlobalLoading(true);
  let tracks = [];
  try {
    tracks = await tracksForOrigin(origin);
  } catch (err) {
    setPlayerStatus(err.message || "Não achei as faixas");
    return;
  } finally {
    setGlobalLoading(false);
  }
  if (!tracks.length) {
    setPlayerStatus("Nenhuma faixa nesta lista");
    return;
  }
  const current = state.current;
  const preferred = current && (
    (kind === "album" && current.albumId != null && String(current.albumId) === String(id)) ||
    (kind === "artist" && current.artistId != null && String(current.artistId) === String(id))
  )
    ? current
    : null;
  const merged = preferred ? queueAroundTrack(tracks, preferred) : tracks;
  const start = preferred
    ? merged.find((row) => sameCatalogTrack(row, preferred)) || merged[0]
    : merged[0];
  const key = start.videoId || (start.deezerId ? `dz:${start.deezerId}` : "");
  setPlaybackQueue(merged, key, "deezer");
  openNowPlaying();
  void playItem(start, { setQueue: false });
}

function applySearchApiParams(url) {
  url.searchParams.set("light", "1");
  url.searchParams.set("max_results", String(SEARCH_API_BATCH));
  if (state.searchMixId) {
    url.searchParams.set("mix_id", state.searchMixId);
  } else if (state.searchQuery) {
    url.searchParams.set("q", state.searchQuery);
  }
  if (state.searchPublishedAfter) {
    url.searchParams.set("published_after", state.searchPublishedAfter);
  }
  if (state.searchPublishedBefore) {
    url.searchParams.set("published_before", state.searchPublishedBefore);
  }
  if (state.searchOrder) {
    url.searchParams.set("order", state.searchOrder);
  }
}

function clearSearchFilters() {
  state.searchMixId = null;
  state.searchChannelId = null;
  state.searchChannelTitle = null;
  state.searchPublishedAfter = null;
  state.searchPublishedBefore = null;
  state.searchOrder = null;
}

async function ensureMixCatalogLoaded() {
  if (state.exploreCategories.length) return true;
  try {
    const res = await fetch("/api/mixes");
    const data = await res.json();
    if (!res.ok) return false;
    state.exploreCategories = data.categories || [];
    state.loadedMixIds = new Set(data.loadedMixIds || []);
    for (const cat of state.exploreCategories) {
      for (const mix of cat.mixes || []) {
        if (mix.id && Array.isArray(mix.coverPreview) && mix.coverPreview.length) {
          state.mixCoverPreviews[mix.id] = mix.coverPreview;
        }
      }
    }
    return true;
  } catch {
    return false;
  }
}

async function refreshExplore() {
  if (exploreSections) exploreSections.innerHTML = "";
  if (exploreCatFooter) exploreCatFooter.hidden = true;
  try {
    await restoreDeezerBrowse();
  } catch (err) {
    if (deezerStatusEl) deezerStatusEl.textContent = err.message || "Catálogo indisponível";
  }
}

function deezerCoverHtml(url) {
  if (!url) {
    return `<div class="deezer-card-art" aria-hidden="true"></div>`;
  }
  return `<div class="deezer-card-art"><img src="${escapeHtml(url)}" alt="" loading="lazy" decoding="async" /></div>`;
}

function deezerCard(kind, id, title, image, subtitle, opts = {}) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mix-card deezer-card";
  btn.title = title || "";
  btn.innerHTML = `${deezerCoverHtml(image)}<div class="mix-card-body"><span class="mix-card-title">${escapeHtml(title || "")}</span>${subtitle ? `<span class="mix-card-sub">${escapeHtml(subtitle)}</span>` : ""}</div>`;
  if (kind === "artist") btn.classList.add("is-round");
  btn.addEventListener("click", () => {
    if (opts.searchOnClick && title) {
      void runTextSearch(title);
      return;
    }
    if (opts.playOnClick && (kind === "artist" || kind === "album" || kind === "playlist")) {
      void playCatalogOrigin(kind, id, title);
      return;
    }
    if (state.view === "search") {
      void openSearchCatalogLevel(kind, id, title);
      return;
    }
    if (state.view !== "explore") setView("explore", { skipExploreRefresh: true });
    void openDeezerLevel(kind, id, title);
  });
  return btn;
}

async function deezerGet(path) {
  const res = await fetch(rutUrl(path));
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === "string" ? detail : "Catálogo indisponível");
  }
  return data;
}

function syncDeezerChrome() {
  const drilled = state.deezerStack.length > 0;
  if (exploreSections) exploreSections.classList.toggle("hidden", drilled);
  if (exploreCatFooter) exploreCatFooter.hidden = true;
  if (deezerBarEl) deezerBarEl.classList.toggle("hidden", !drilled);
}

function renderDeezerTracks(tracks, label) {
  state.deezerTracks = Array.isArray(tracks) ? tracks : [];
  exploreListTracks = state.deezerTracks;
  if (deezerTracksLabelEl) {
    deezerTracksLabelEl.textContent = label || "";
    deezerTracksLabelEl.closest(".catalog-list-heading")?.classList.toggle("hidden", !label || !state.deezerTracks.length);
  }
  if (deezerTrackHeadEl) deezerTrackHeadEl.classList.toggle("hidden", !state.deezerTracks.length);
  if (!deezerTracksEl) return;
  deezerTracksEl.innerHTML = "";
  state.deezerTracks.forEach((item, index) => {
    deezerTracksEl.appendChild(buildTrackRow(item, index, { mode: "deezer" }));
  });
  scheduleKnownDeezerAudio(state.deezerTracks);
  syncCatalogListPlayButtons();
}

function appendCardShelf(container, title, cards, sectionId, opts = {}) {
  const list = (cards || []).filter((card) => card && card.id != null);
  if (!container || !list.length) return null;
  const section = appendShelfSection(container, title, sectionId || title, () =>
    list.map((card) =>
      deezerCard(
        card.kind || "playlist",
        card.id,
        card.title || card.name || "",
        card.picture,
        card.subtitle || "",
        { playOnClick: Boolean(opts.playOnClick), searchOnClick: Boolean(opts.searchOnClick) }
      )
    )
  );
  if (section && sectionId) section.id = sectionId;
  return section;
}

const GENRE_COVERS = [
  { test: /rock|metal|punk/i, g1: "#E63946", g2: "#1D1D1D" },
  { test: /electro|dance|edm|house|techno/i, g1: "#00FFF0", g2: "#8B5DFF" },
  { test: /hip.?hop|rap|funk/i, g1: "#6A4C93", g2: "#FFD93D" },
  { test: /jazz|blues/i, g1: "#6B4423", g2: "#C4A484" },
  { test: /clássic|classic|orquestra/i, g1: "#D4A574", g2: "#2C3E50" },
  { test: /sertanejo|country/i, g1: "#D4A574", g2: "#8B4513" },
  { test: /forró|forro|axé|axe/i, g1: "#FF6B35", g2: "#E63946" },
  { test: /mpb|bossa/i, g1: "#4ECDC4", g2: "#2C3E50" },
  { test: /samba|pagode/i, g1: "#F4A261", g2: "#9D174D" },
  { test: /reggae|reggaeton/i, g1: "#90BE6D", g2: "#14532D" },
  { test: /pop/i, g1: "#FF6B9D", g2: "#BE185D" },
  { test: /alternat|indie/i, g1: "#B2DFDB", g2: "#5B4B8A" },
  { test: /ambient|chill|relax|lo-?fi/i, g1: "#4ECDC4", g2: "#556FB5" },
  { test: /r&b|soul/i, g1: "#8B5DFF", g2: "#1D1D1D" },
  { test: /gospel|religios/i, g1: "#F5F5DC", g2: "#1E3A5F" },
  { test: /latin|latino|k-?pop/i, g1: "#FF6B35", g2: "#FFD93D" },
];

function genreCoverColors(name) {
  const hit = GENRE_COVERS.find((row) => row.test.test(name || ""));
  return hit || { g1: "#3B82F6", g2: "#1E1B4B" };
}

function appendGenrePills(container, genres, sectionId) {
  const list = (genres || []).filter((genre) => genre && genre.id != null && genre.name);
  if (!container || !list.length) return;
  const section = document.createElement("section");
  section.className = "explore-class";
  if (sectionId) section.id = sectionId;
  const title = document.createElement("h2");
  title.className = "explore-class-title";
  title.textContent = "Momentos e gêneros";
  section.appendChild(title);
  const wrap = document.createElement("div");
  wrap.className = "genre-covers";
  list.forEach((genre) => {
    const colors = genreCoverColors(genre.name);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "genre-cover";
    btn.style.setProperty("--g1", colors.g1);
    btn.style.setProperty("--g2", colors.g2);
    btn.innerHTML = `<span class="genre-cover-name">${escapeHtml(genre.name)}</span>`;
    btn.addEventListener("click", () => {
      if (state.view === "search") {
        void openSearchCatalogLevel("genre", genre.id, genre.name);
        return;
      }
      if (state.view !== "explore") setView("explore", { skipExploreRefresh: true });
      void openDeezerLevel("genre", genre.id, genre.name);
    });
    wrap.appendChild(btn);
  });
  section.appendChild(wrap);
  container.appendChild(section);
}

function appendTrackBlock(container, title, tracks, sectionId) {
  const list = (tracks || []).filter((item) => item && (item.deezerId || item.videoId));
  if (!container || !list.length) return;
  const section = document.createElement("section");
  section.className = "explore-class";
  if (sectionId) section.id = sectionId;
  const heading = document.createElement("h2");
  heading.className = "explore-class-title";
  heading.textContent = title;
  section.appendChild(heading);
  state.deezerTracks = list;
  state.catalogOrigin = sectionId === "trending" ? { kind: "chart", id: "0", title: title || "Em alta" } : state.catalogOrigin;
  const ol = document.createElement("ol");
  ol.className = "track-list";
  list.forEach((item, index) => ol.appendChild(buildTrackRow(item, index, { mode: "deezer" })));
  section.appendChild(ol);
  scheduleKnownDeezerAudio(list);
  container.appendChild(section);
}

function appendExploreChips(container, chips) {
  const list = (chips || []).filter((chip) => chip && chip.id && chip.label);
  if (!container || !list.length) return;
  const bar = document.createElement("div");
  bar.className = "explore-chips";
  list.forEach((chip) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "explore-chip";
    btn.textContent = chip.label;
    btn.addEventListener("click", () => {
      document.getElementById(chip.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    bar.appendChild(btn);
  });
  container.appendChild(bar);
}

async function showDeezerHome() {
  const seq = ++deezerLoadSeq;
  state.catalogOrigin = null;
  if (deezerTitleEl) deezerTitleEl.textContent = "";
  clearDeezerEntityCover();
  if (deezerStatusEl) deezerStatusEl.textContent = "Carregando catálogo…";
  syncDeezerChrome();
  renderDeezerTracks([], "");
  if (deezerShelvesEl) deezerShelvesEl.innerHTML = "";
  const data = await deezerGet("/api/catalog/deezer/explore");
  if (seq !== deezerLoadSeq) return;
  if (deezerStatusEl) deezerStatusEl.textContent = "";
  if (!deezerShelvesEl) return;
  appendExploreChips(deezerShelvesEl, data.chips);
  appendCardShelf(deezerShelvesEl, "Novos álbuns e singles", data.releases, "releases");
  appendGenrePills(deezerShelvesEl, data.genres, "genres");
  appendTrackBlock(deezerShelvesEl, "Em alta", data.trending, "trending");
  appendCardShelf(deezerShelvesEl, "Paradas", data.chartPlaylists, "charts");
  if (!deezerShelvesEl.childElementCount && deezerStatusEl) {
    deezerStatusEl.textContent = "Catálogo vazio no momento.";
  }
}

async function showDeezerLevel(level) {
  const seq = ++deezerLoadSeq;
  state.catalogOrigin = {
    kind: level.kind,
    id: String(level.id),
    title: level.title || "",
  };
  notePlayedOrigin(state.catalogOrigin);
  if (deezerStatusEl) deezerStatusEl.textContent = "Carregando…";
  if (deezerTitleEl) deezerTitleEl.textContent = level.title || "";
  clearDeezerEntityCover();
  syncDeezerChrome();
  renderDeezerTracks([], "");
  if (deezerShelvesEl) deezerShelvesEl.innerHTML = "";
  const id = encodeURIComponent(level.id);
  let data;
  if (level.kind === "genre") {
    data = await deezerGet(`/api/catalog/deezer/genres/${id}`);
  } else if (level.kind === "artist") {
    data = await deezerGet(`/api/catalog/deezer/artists/${id}`);
  } else if (level.kind === "album") {
    data = await deezerGet(`/api/catalog/deezer/albums/${id}`);
  } else if (level.kind === "playlist") {
    data = await deezerGet(`/api/catalog/deezer/playlists/${id}`);
  } else {
    data = {};
  }
  if (seq !== deezerLoadSeq) return;
  if (level.kind === "genre") {
    const name = data.genre?.name || level.title || "Gênero";
    if (deezerTitleEl) deezerTitleEl.textContent = name;
    level.title = name;
    if (deezerShelvesEl && (data.artists || []).length) {
      appendShelfSection(deezerShelvesEl, "Artistas", `deezer-artists-${id}`, () =>
        data.artists.map((a) => deezerCard("artist", a.id, a.name, a.picture, ""))
      );
    }
    if (deezerShelvesEl && (data.playlists || []).length) {
      appendShelfSection(deezerShelvesEl, "Playlists", `deezer-pl-${id}`, () =>
        data.playlists.map((p) => deezerCard("playlist", p.id, p.title, p.picture, p.subtitle || "Playlist"))
      );
    }
    renderDeezerTracks(data.tracks || [], "Parada");
  } else if (level.kind === "artist") {
    const name = data.artist?.name || level.title || "Artista";
    if (deezerTitleEl) deezerTitleEl.textContent = name;
    level.title = name;
    if (deezerShelvesEl && (data.albums || []).length) {
      appendShelfSection(deezerShelvesEl, "Álbuns", `deezer-albums-${id}`, () =>
        data.albums.map((a) => deezerCard("album", a.id, a.title, a.picture, a.releaseDate || ""))
      );
    }
    renderDeezerTracks(data.tracks || [], "Mais tocadas");
  } else if (level.kind === "album") {
    const name = data.album?.title || level.title || "Álbum";
    if (deezerTitleEl) deezerTitleEl.textContent = name;
    level.title = name;
    setCatalogEntityCover(deezerCoverEl, deezerSubtitleEl, data.album?.picture, data.album?.artist);
    renderDeezerTracks(data.tracks || [], data.album?.genre || "Faixas");
  } else if (level.kind === "playlist") {
    const name = data.playlist?.title || level.title || "Playlist";
    if (deezerTitleEl) deezerTitleEl.textContent = name;
    level.title = name;
    setCatalogEntityCover(deezerCoverEl, deezerSubtitleEl, data.playlist?.picture, "");
    renderDeezerTracks(data.tracks || [], "Faixas");
  }
  if (deezerStatusEl) deezerStatusEl.textContent = "";
  syncDeezerChrome();
}

async function openDeezerLevel(kind, id, title) {
  if (id == null || id === "") return;
  const level = { kind, id: String(id), title: title || "" };
  state.deezerStack.push(level);
  try {
    await showDeezerLevel(level);
  } catch (err) {
    state.deezerStack.pop();
    syncDeezerChrome();
    if (deezerStatusEl) deezerStatusEl.textContent = err.message || "Catálogo indisponível";
  }
}

async function restoreDeezerBrowse() {
  if (!deezerShelvesEl) return;
  if (state.deezerStack.length) {
    await showDeezerLevel(state.deezerStack[state.deezerStack.length - 1]);
    return;
  }
  await showDeezerHome();
}

document.getElementById("deezer-back")?.addEventListener("click", () => {
  state.deezerStack.pop();
  void restoreDeezerBrowse().catch((err) => {
    if (deezerStatusEl) deezerStatusEl.textContent = err.message || "Catálogo indisponível";
  });
});

function ensureDeezerResolved(item, { quiet = false } = {}) {
  if (item?.videoId || !item?.deezerId) return Promise.resolve(item);
  const key = String(item.deezerId);
  const pending = deezerResolvePromises.get(key);
  if (pending) return pending.then(() => item);
  const job = (async () => {
    if (!quiet) setPlayerStatus("Procurando áudio…");
    const res = await fetch(rutUrl("/api/catalog/deezer/resolve"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deezerId: item.deezerId,
        title: item.title,
        artist: item.artist,
        album: item.album,
        genre: item.genre,
        duration: item.duration,
        thumbnailUrl: item.thumbnailUrl,
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.videoId) {
      const detail = data.detail;
      throw new Error(typeof detail === "string" ? detail : "Não achei um áudio compatível com esta faixa.");
    }
    item.videoId = data.videoId;
    item.catalogSource = "deezer";
    document.querySelectorAll(`[data-deezer-id="${CSS.escape(key)}"]`).forEach((row) => {
      row.dataset.videoId = data.videoId;
      const addBtn = row.querySelector(".btn-add-lib");
      if (addBtn) addBtn.dataset.videoId = data.videoId;
      syncTrackRowServerBadge(row, item);
    });
    return item;
  })();
  deezerResolvePromises.set(key, job);
  job.finally(() => {
    if (deezerResolvePromises.get(key) === job) deezerResolvePromises.delete(key);
  });
  return job;
}

function loadRecentSearches() {
  if (!state.user?.id) return [];
  try {
    const raw = localStorage.getItem(userStorageKey(RECENT_SEARCHES_KEY));
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveRecentSearches(list) {
  if (!state.user?.id) return;
  try {
    localStorage.setItem(
      userStorageKey(RECENT_SEARCHES_KEY),
      JSON.stringify(list.slice(0, MAX_RECENT_SEARCHES))
    );
  } catch {
    /* quota / privado */
  }
  schedulePrefsSync();
}

function recordRecentSearch(entry) {
  const q = (entry.q || "").trim();
  const mixId = entry.mixId || null;
  const channelId = entry.channelId || null;
  const label = (entry.label || q || "").trim();
  if (!q && !mixId && !channelId) return;

  let coverPreview = Array.isArray(entry.coverPreview)
    ? entry.coverPreview.filter(Boolean).slice(0, 4)
    : [];
  if (!coverPreview.length && mixId) {
    const mix = findMixById(mixId);
    coverPreview = (
      (state.mixCoverPreviews[mixId]?.length && state.mixCoverPreviews[mixId]) ||
      mix?.coverPreview ||
      []
    ).slice(0, 4);
  }
  if (!coverPreview.length && state.searchCatalog?.length) {
    coverPreview = shortcutPreviewFromCatalog();
  }

  const dedupeKey = mixId || (channelId ? `channel:${channelId}` : q.toLowerCase());
  let list = loadRecentSearches().filter((i) => {
    const k = i.mixId || (i.channelId ? `channel:${i.channelId}` : (i.q || "").toLowerCase());
    return k !== dedupeKey;
  });
  list.unshift({
    q: q || label,
    mixId,
    channelId,
    label: label || q,
    coverPreview,
    at: Date.now(),
  });
  saveRecentSearches(list);
  if (state.view === "home") renderHomeSections();
}

function homeGreetingText() {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "Bom dia";
  if (h >= 12 && h < 18) return "Boa tarde";
  return "Boa noite";
}

function normalizeSavedShortcuts(list) {
  if (!Array.isArray(list)) return [];
  return list
    .filter((e) => e && e.id && (e.mixId || e.q || e.channelId))
    .slice(0, MAX_SAVED_SHORTCUTS);
}

function shortcutKeyForParts({ mixId, q, channelId }) {
  if (mixId) return `mix:${mixId}`;
  if (channelId) return `channel:${channelId}`;
  return `search:${(q || "").trim().toLowerCase()}`;
}

function getSavedShortcuts() {
  return state.savedShortcuts || [];
}

function isShortcutSaved(entryOrKey) {
  const key = typeof entryOrKey === "string" ? entryOrKey : shortcutKeyForParts(entryOrKey);
  return getSavedShortcuts().some((s) => s.id === key);
}

function shortcutPreviewFromCatalog(limit = 4) {
  const urls = [];
  const seen = new Set();
  for (const item of state.searchCatalog || []) {
    const u = item?.thumbnailUrl;
    if (!u || seen.has(u)) continue;
    seen.add(u);
    urls.push(u);
    if (urls.length >= limit) break;
  }
  return urls;
}

async function persistSavedShortcuts() {
  if (!state.user) return;
  try {
    await fetch("/api/me/preferences", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ savedShortcuts: state.savedShortcuts }),
    });
  } catch {
    /* silencioso */
  }
  renderHomeSections();
  updateSearchSaveButton();
  refreshExploreSaveButtons();
}

function removeSavedShortcut(id) {
  state.savedShortcuts = getSavedShortcuts().filter((s) => s.id !== id);
  void persistSavedShortcuts();
}

async function addSavedShortcut(entry) {
  const id = shortcutKeyForParts(entry);
  const label = (entry.label || entry.q || "").trim() || "Salvo";
  let coverPreview = Array.isArray(entry.coverPreview) ? entry.coverPreview.filter(Boolean).slice(0, 4) : [];
  if (!coverPreview.length && entry.mixId) {
    const mix = findMixById(entry.mixId);
    const preview =
      (state.mixCoverPreviews[entry.mixId]?.length && state.mixCoverPreviews[entry.mixId]) ||
      mix?.coverPreview ||
      [];
    coverPreview = preview.slice(0, 4);
  }
  if (!coverPreview.length && !entry.mixId && !entry.channelId) {
    coverPreview = shortcutPreviewFromCatalog();
  }
  const normalized = {
    id,
    type: entry.mixId ? "mix" : entry.channelId ? "channel" : "search",
    mixId: entry.mixId || null,
    q: entry.q ? String(entry.q).trim() : null,
    channelId: entry.channelId || null,
    label,
    coverPreview,
    savedAt: Date.now(),
  };
  const rest = getSavedShortcuts().filter((s) => s.id !== id);
  state.savedShortcuts = [normalized, ...rest].slice(0, MAX_SAVED_SHORTCUTS);
  await persistSavedShortcuts();
}

function toggleSaveMix(mix) {
  if (!mix?.id) return;
  const id = shortcutKeyForParts({ mixId: mix.id });
  if (isShortcutSaved(id)) {
    removeSavedShortcut(id);
    return;
  }
  const preview =
    (state.mixCoverPreviews[mix.id]?.length && state.mixCoverPreviews[mix.id]) ||
    mix.coverPreview ||
    [];
  void addSavedShortcut({ mixId: mix.id, label: mix.label, coverPreview: preview });
}

function currentSearchShortcutDescriptor() {
  if (state.searchMixId) {
    const mix = findMixById(state.searchMixId);
    return {
      mixId: state.searchMixId,
      q: state.searchQuery || mix?.query || "",
      label: mix?.label || searchHeading?.textContent || "Playlist",
    };
  }
  if (state.searchChannelId) {
    const label =
      state.searchChannelTitle ||
      (searchHeading?.textContent || "").replace(/^Canal ·\s*/, "").trim() ||
      "Canal";
    return {
      channelId: state.searchChannelId,
      label: label.startsWith("Canal ·") ? label : `Canal · ${label}`,
    };
  }
  const q = (state.searchQuery || "").trim();
  if (!q) return null;
  return { q, label: q };
}

function toggleSaveCurrentSearch() {
  const desc = currentSearchShortcutDescriptor();
  if (!desc) return;
  const id = shortcutKeyForParts(desc);
  if (isShortcutSaved(id)) {
    removeSavedShortcut(id);
    return;
  }
  let coverPreview = shortcutPreviewFromCatalog();
  if (desc.mixId) {
    const mix = findMixById(desc.mixId);
    const preview =
      (state.mixCoverPreviews[desc.mixId]?.length && state.mixCoverPreviews[desc.mixId]) ||
      mix?.coverPreview ||
      [];
    if (preview.length) coverPreview = preview.slice(0, 4);
  }
  void addSavedShortcut({ ...desc, coverPreview });
}

function updateSearchSaveButton() {
  if (!searchSaveShortcut) return;
  const desc = currentSearchShortcutDescriptor();
  const show = state.view === "search" && Boolean(desc);
  searchSaveShortcut.classList.toggle("hidden", !show);
  if (!show) return;
  const saved = isShortcutSaved(shortcutKeyForParts(desc));
  searchSaveShortcut.textContent = saved ? "Salvo ✓" : "Salvar na biblioteca";
  searchSaveShortcut.classList.toggle("is-saved", saved);
}

function refreshExploreSaveButtons() {
  exploreSections?.querySelectorAll(".mix-card-save-btn[data-mix-id]").forEach((btn) => {
    const mixId = btn.dataset.mixId;
    const saved = isShortcutSaved(`mix:${mixId}`);
    btn.classList.toggle("is-saved", saved);
    btn.classList.toggle("is-visible", saved);
    btn.textContent = saved ? "✓" : "+";
    btn.title = saved ? "Remover do Início e Biblioteca" : "Salvar no Início e Biblioteca";
  });
}

function resolveShortcutPreview(entry) {
  let preview = Array.isArray(entry.coverPreview) ? entry.coverPreview.filter(Boolean) : [];
  if (preview.length) return preview.slice(0, 4);
  if (entry.mixId) {
    const mix = findMixById(entry.mixId);
    preview =
      (state.mixCoverPreviews[entry.mixId]?.length && state.mixCoverPreviews[entry.mixId]) ||
      mix?.coverPreview ||
      [];
  }
  return preview.slice(0, 4);
}

function savedShortcutSubtitle(entry) {
  if (entry.type === "mix" || entry.mixId) return "Playlist · Explorar";
  if (entry.type === "channel" || entry.channelId) return "Canal";
  return "Busca";
}

async function openSavedShortcut(entry) {
  await openRecentSearch(entry);
}

function createSavedShortcutCard(entry) {
  return createShortcutMixCard(entry, { allowRemove: true });
}

function createShortcutMixCard(entry, opts = {}) {
  const wrap = document.createElement("div");
  wrap.className = "mix-card-wrap";
  wrap.dataset.shortcutId = entry.id || "";

  const preview = resolveShortcutPreview(entry);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mix-card";
  if (entry.mixId) btn.dataset.mixId = entry.mixId;
  btn.setAttribute("role", "listitem");
  btn.innerHTML = `${mixCoverArtHtml(preview)}<div class="mix-card-body"><span class="mix-card-title">${escapeHtml(entry.label || "")}</span><span class="mix-card-sub">${escapeHtml(savedShortcutSubtitle(entry))}</span></div>`;
  btn.addEventListener("click", () => void openSavedShortcut(entry));
  wrap.appendChild(btn);
  attachMixLoadedBadge(wrap, { mixId: entry.mixId || null });

  if (opts.allowRemove) {
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "mix-card-save-btn is-saved is-visible";
    removeBtn.title = "Remover do Início e Biblioteca";
    removeBtn.setAttribute("aria-label", "Remover");
    removeBtn.textContent = "×";
    removeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      removeSavedShortcut(entry.id);
    });
    wrap.appendChild(removeBtn);
  }

  return wrap;
}

function createMixCardButton(mix, opts = {}) {
  const wrap = document.createElement("div");
  wrap.className = "mix-card-wrap";

  const preview =
    (state.mixCoverPreviews[mix.id]?.length && state.mixCoverPreviews[mix.id]) ||
    mix.coverPreview ||
    [];
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mix-card";
  btn.dataset.mixId = mix.id || "";
  btn.setAttribute("role", "listitem");
  btn.innerHTML = `${mixCoverArtHtml(preview)}<div class="mix-card-body"><span class="mix-card-title">${escapeHtml(mix.label)}</span><span class="mix-card-sub">${escapeHtml(mixCardSubtitle(mix))}</span></div>`;
  btn.addEventListener("click", () => void startMix(mix, { originEl: btn }));
  wrap.appendChild(btn);
  attachMixLoadedBadge(wrap, { mixId: mix.id });

  if (opts.allowSave && mix.id) {
    const saved = isShortcutSaved(`mix:${mix.id}`);
    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = `mix-card-save-btn${saved ? " is-saved is-visible" : ""}`;
    saveBtn.dataset.mixId = mix.id;
    saveBtn.title = saved ? "Remover do Início e Biblioteca" : "Salvar no Início e Biblioteca";
    saveBtn.setAttribute("aria-label", saveBtn.title);
    saveBtn.textContent = saved ? "✓" : "+";
    saveBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSaveMix(mix);
      const nowSaved = isShortcutSaved(`mix:${mix.id}`);
      saveBtn.classList.toggle("is-saved", nowSaved);
      saveBtn.classList.toggle("is-visible", nowSaved);
      saveBtn.textContent = nowSaved ? "✓" : "+";
      saveBtn.title = nowSaved
        ? "Remover do Início e Biblioteca"
        : "Salvar no Início e Biblioteca";
    });
    wrap.appendChild(saveBtn);
  }

  return wrap;
}

function appendShelfSection(container, title, sectionKey, buildItems) {
  const section = document.createElement("section");
  section.className = "explore-class";
  section.dataset.category = sectionKey;

  const head = document.createElement("div");
  head.className = "explore-class-head";
  const h2 = document.createElement("h2");
  h2.className = "explore-class-title";
  h2.id = `shelf-${sectionKey}`;
  h2.textContent = title;
  head.appendChild(h2);

  const nav = document.createElement("div");
  nav.className = "explore-class-nav";
  nav.innerHTML = `<button type="button" class="explore-mais-btn" hidden>Mais</button><button type="button" class="explore-scroll-btn" data-dir="prev" aria-label="Anterior">${EXPLORE_SHELF_SCROLL_ICON.prev}</button><button type="button" class="explore-scroll-btn" data-dir="next" aria-label="Próximo">${EXPLORE_SHELF_SCROLL_ICON.next}</button>`;
  head.appendChild(nav);
  section.appendChild(head);

  const shelfWrap = document.createElement("div");
  shelfWrap.className = "explore-shelf-wrap";
  const shelf = document.createElement("div");
  shelf.className = "explore-shelf";
  shelf.setAttribute("role", "list");

  for (const node of buildItems()) shelf.appendChild(node);

  shelfWrap.appendChild(shelf);
  section.appendChild(shelfWrap);
  container.appendChild(section);
  bindExploreShelfNav(section, shelf);
  return section;
}

function recentSearchCoverPreview(entry) {
  if (Array.isArray(entry.coverPreview) && entry.coverPreview.length) {
    return entry.coverPreview.filter(Boolean).slice(0, 4);
  }
  if (entry.mixId) {
    return resolveShortcutPreview({ mixId: entry.mixId, coverPreview: [] });
  }
  return [];
}

function recentSearchSubtitle(entry) {
  if (entry.mixId) return "Playlist recente";
  if (entry.channelId) return "Canal recente";
  return "Busca recente";
}

function createRecentSearchMixCard(entry) {
  const wrap = document.createElement("div");
  wrap.className = "mix-card-wrap";
  const preview = recentSearchCoverPreview(entry);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mix-card";
  btn.setAttribute("role", "listitem");
  btn.title = entry.label || entry.q || "";
  btn.innerHTML = `${mixCoverArtHtml(preview)}<div class="mix-card-body"><span class="mix-card-title">${escapeHtml(entry.label || entry.q || "")}</span><span class="mix-card-sub">${escapeHtml(recentSearchSubtitle(entry))}</span></div>`;
  btn.addEventListener("click", () => void openRecentSearch(entry));
  wrap.appendChild(btn);
  return wrap;
}

async function openRecentSearch(entry) {
  const q = (entry?.label || entry?.q || "").replace(/^Canal ·\s*/, "").trim();
  if (!q) return;
  await runTextSearch(q);
}

function renderHomeSections() {
  if (!homeSections) return;
  if (homeGreeting) {
    homeGreeting.textContent = `${homeGreetingText()} · o que combina com o que você ouve.`;
  }
  homeSections.innerHTML = "";

  let any = false;

  const saved = getSavedShortcuts();
  if (saved.length) {
    any = true;
    appendShelfSection(homeSections, "Suas playlists e buscas", "home-saved", () =>
      saved.map((entry) => createSavedShortcutCard(entry))
    );
  }

  const recent = loadRecentSearches();
  if (recent.length) {
    any = true;
    appendShelfSection(homeSections, "Buscas recentes", "home-recent", () =>
      recent.map((entry) => createRecentSearchMixCard(entry))
    );
  }

  if (!any) {
    homeSections.innerHTML =
      '<p class="status-line">Salve playlists e buscas com +, ou use Explorar.</p>';
  }
}

async function ensureServerCatalogLoaded() {
  if (state.freeSections.length) return;
  await loadServerCatalogForHome();
}

let homeDiscoverSeq = 0;

function renderHomeDiscover(data) {
  const el = document.getElementById("home-discover");
  if (!el) return;
  el.innerHTML = "";
  appendCardShelf(el, "Ouvir de novo", data.listenAgain, "home-again", { searchOnClick: true });
  for (const shelf of data.shelves || []) {
    appendCardShelf(el, shelf.title || "", shelf.cards, "");
  }
  appendCardShelf(el, "Álbuns para você", data.albumsForYou, "home-albums");
  appendCardShelf(el, "Hits de hoje", data.hitsToday, "home-hits");
  appendCardShelf(el, "Playlists em destaque para você", data.featuredPlaylists, "home-playlists");
  appendCardShelf(el, "Novidades", data.newReleases, "home-new");
}

async function loadHomeDiscover() {
  const el = document.getElementById("home-discover");
  if (!el) return;
  const seq = ++homeDiscoverSeq;
  el.innerHTML = "";
  setGlobalLoading(true);
  try {
    const data = await deezerGet("/api/catalog/deezer/library");
    if (seq !== homeDiscoverSeq) return;
    renderHomeDiscover(data);
  } catch (err) {
    if (seq !== homeDiscoverSeq) return;
    el.innerHTML = `<p class="status-line">${escapeHtml(err.message || "Catálogo indisponível")}</p>`;
  } finally {
    if (seq === homeDiscoverSeq) setGlobalLoading(false);
  }
}

async function refreshHome() {
  if (!homeSections) return;
  renderHomeSections();
  await Promise.all([loadHomeDiscover(), refreshLibrary()]);
}

function mixCoverArtHtml(preview) {
  const urls = Array.isArray(preview) ? preview.filter(Boolean) : [];
  let cells = "";
  for (let i = 0; i < 4; i += 1) {
    const url = urls[i];
    if (url) {
      cells += `<div class="mix-cover-cell"><img src="${escapeHtml(url)}" alt="" loading="eager" decoding="async" /></div>`;
    } else {
      cells += `<div class="mix-cover-cell mix-cover-cell--empty" aria-hidden="true"></div>`;
    }
  }
  return `<div class="mix-card-art">${cells}</div>`;
}

function applyMixCoverPreview(mixId, preview) {
  if (!mixId || !Array.isArray(preview) || !preview.length) return;
  state.mixCoverPreviews[mixId] = preview;
  for (const cat of state.exploreCategories) {
    for (const mix of cat.mixes || []) {
      if (mix.id === mixId) mix.coverPreview = preview;
    }
  }
  const savedIdx = getSavedShortcuts().findIndex((s) => s.mixId === mixId);
  if (savedIdx >= 0) {
    const next = [...getSavedShortcuts()];
    next[savedIdx] = { ...next[savedIdx], coverPreview: preview.slice(0, 4) };
    state.savedShortcuts = next;
  }
  document.querySelectorAll(`[data-mix-id="${CSS.escape(mixId)}"] .mix-card-art`).forEach((art) => {
    art.outerHTML = mixCoverArtHtml(preview).trim();
  });
  document.querySelectorAll(`[data-shortcut-id="mix:${CSS.escape(mixId)}"] .mix-card-art`).forEach((art) => {
    art.outerHTML = mixCoverArtHtml(preview).trim();
  });
}

async function submitMixCoversFromItems(mixId, items) {
  if (!mixId || !items?.length) return;
  const urls = [];
  const seen = new Set();
  for (const item of items) {
    const url = higherResThumb(item.thumbnailUrl || "");
    if (!url || seen.has(url)) continue;
    seen.add(url);
    urls.push(url);
    if (urls.length >= 24) break;
  }
  if (!urls.length) return;
  try {
    const res = await fetch(`/api/mixes/${encodeURIComponent(mixId)}/covers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thumbnailUrls: urls }),
    });
    const data = await res.json();
    if (!res.ok) return;
    if (Array.isArray(data.coverPreview) && data.coverPreview.length) {
      applyMixCoverPreview(mixId, data.coverPreview);
    }
  } catch {
    /* silencioso */
  }
}

/** Ícones SVG (path) por categoria do Explorar — barra inferior no celular. */
const EXPLORE_CATEGORY_ICON = {
  destaques:
    '<path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>',
  rock: '<path d="M7 2v11h3v9l7-12h-4l4-8H7z"/>',
  pop: '<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5-3c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>',
  hiphop:
    '<path d="M12 1a9 9 0 00-9 9v7c0 1.66 1.34 3 3 3h1v-8H5v-2a7 7 0 1114 0v2h-2v8h1c1.66 0 3-1.34 3-3v-7a9 9 0 00-9-9z"/>',
  eletronica:
    '<path d="M4 10h4V6H4v4zm0 8h4v-4H4v4zm6-12v16h4V6h-4zm6 4h4V6h-4v4zm0 8h4v-4h-4v4z"/>',
  mpb: '<path d="M12 3C7.03 3 3 7.03 3 12s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9zm-1 14H8v-6h3v6zm2 0V9h3v8h-3z"/>',
  sertanejo:
    '<path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V22h8v-7.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/>',
  "pagode-funk":
    '<path d="M12 3v10.55c-2.21-.47-4-2.24-4-4.55h2V7h4V3h-2zm-1 12.5c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>',
  "forro-regional":
    '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 010-5 2.5 2.5 0 010 5z"/>',
  "gospel-br":
    '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>',
  decadas:
    '<path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM7 12h5v5H7z"/>',
  recentes:
    '<path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 5v5.2l3.5 2.1-.9 1.5L11 13V7h2z"/>',
  artistas:
    '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>',
  outros:
    '<path d="M4 8h4V4H4v4zm0 6h4v-4H4v4zm6-10v16h4V4h-4zm6 4h4V4h-4v4zm0 6h4v-4h-4v4z"/>',
  mundo:
    '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93A8.001 8.001 0 014.07 13H11v6.93zM11 11V4.07A8.001 8.001 0 0119.93 11H11z"/>',
  default:
    '<path d="M12 3v10.55c-2.21-.47-4-2.24-4-4.55h2V7h4V3h-2zm-1 12.5c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>',
};

function exploreCategoryIconMarkup(categoryId) {
  const path = EXPLORE_CATEGORY_ICON[categoryId] || EXPLORE_CATEGORY_ICON.default;
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${path}</svg>`;
}

function scrollContentToExploreCategory(categoryId) {
  const target = document.getElementById(`explore-class-${categoryId}`);
  const scrollRoot = document.querySelector(".content");
  if (!target || !scrollRoot) {
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  const top =
    target.getBoundingClientRect().top -
    scrollRoot.getBoundingClientRect().top +
    scrollRoot.scrollTop -
    6;
  scrollRoot.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
}

function renderExploreCategoryFooter() {
  if (!exploreCatFooter) return;
  exploreCatFooter.innerHTML = "";
  const footerCats = state.exploreCategories.map((cat) => ({
    id: cat.id || "cat",
    label: cat.label || "",
  }));
  const artistSec = state.freeSections.find((s) => s.id === "artistas");
  if (artistSec?.shelves?.length) {
    footerCats.push({ id: "artistas", label: artistSec.label || "Artistas" });
  }
  if (!footerCats.length) return;
  footerCats.forEach((cat, index) => {
    const id = cat.id || "cat";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `explore-cat-btn${index === 0 ? " active" : ""}`;
    btn.dataset.categoryId = id;
    btn.setAttribute("aria-label", cat.label || id);
    btn.innerHTML = exploreCategoryIconMarkup(id);
    const label = document.createElement("span");
    label.textContent = cat.label || id;
    btn.appendChild(label);
    btn.addEventListener("click", () => {
      exploreCatFooter.querySelectorAll(".explore-cat-btn").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      scrollContentToExploreCategory(id);
    });
    exploreCatFooter.appendChild(btn);
  });
}

const EXPLORE_SHELF_SCROLL_ICON = {
  prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 18.5L8 12l6.5-6.5 1.4 1.4L10.8 12l5.1 5.1-1.4 1.4z"/></svg>',
  next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 18.5L16 12l-6.5-6.5-1.4 1.4L13.2 12l-5.1 5.1 1.4 1.4z"/></svg>',
};

function mixCardSubtitle(mix) {
  const sub = (mix.subtitle || "Mix").trim();
  return `RutsFy · ${sub}`;
}

function bindExploreShelfNav(section, shelf) {
  const prevBtn = section.querySelector(".explore-scroll-btn[data-dir='prev']");
  const nextBtn = section.querySelector(".explore-scroll-btn[data-dir='next']");
  const maisBtn = section.querySelector(".explore-mais-btn");

  const syncScrollButtons = () => {
    const max = shelf.scrollWidth - shelf.clientWidth;
    const left = shelf.scrollLeft;
    if (prevBtn) prevBtn.disabled = left <= 4;
    if (nextBtn) nextBtn.disabled = max <= 4 || left >= max - 4;
    if (maisBtn) maisBtn.hidden = max <= 4;
  };

  const scrollByPage = (dir) => {
    const step = Math.max(240, shelf.clientWidth * 0.85);
    shelf.scrollBy({ left: dir * step, behavior: "smooth" });
  };

  prevBtn?.addEventListener("click", () => scrollByPage(-1));
  nextBtn?.addEventListener("click", () => scrollByPage(1));
  maisBtn?.addEventListener("click", () => {
    shelf.scrollTo({ left: shelf.scrollWidth, behavior: "smooth" });
  });
  shelf.addEventListener("scroll", syncScrollButtons, { passive: true });
  window.addEventListener(
    "resize",
    () => {
      syncScrollButtons();
    },
    { passive: true }
  );
  requestAnimationFrame(syncScrollButtons);
}

function renderExploreSections() {
  exploreSections.innerHTML = "";
  for (const cat of state.exploreCategories) {
    const section = document.createElement("section");
    section.className = "explore-class";
    section.dataset.category = cat.id || "";
    section.setAttribute("role", "listitem");
    section.setAttribute("aria-labelledby", `explore-class-${cat.id || "cat"}`);

    const head = document.createElement("div");
    head.className = "explore-class-head";

    const title = document.createElement("h2");
    title.id = `explore-class-${cat.id || "cat"}`;
    title.className = "explore-class-title";
    title.textContent = cat.label || "";
    head.appendChild(title);

    const nav = document.createElement("div");
    nav.className = "explore-class-nav";
    nav.innerHTML = `<button type="button" class="explore-mais-btn" hidden>Mais</button><button type="button" class="explore-scroll-btn" data-dir="prev" aria-label="Anterior">${EXPLORE_SHELF_SCROLL_ICON.prev}</button><button type="button" class="explore-scroll-btn" data-dir="next" aria-label="Próximo">${EXPLORE_SHELF_SCROLL_ICON.next}</button>`;
    head.appendChild(nav);
    section.appendChild(head);

    const shelfWrap = document.createElement("div");
    shelfWrap.className = "explore-shelf-wrap";
    const shelf = document.createElement("div");
    shelf.className = "explore-shelf";
    shelf.setAttribute("role", "list");

    for (const mix of cat.mixes || []) {
      shelf.appendChild(createMixCardButton(mix, { allowSave: true }));
    }

    shelfWrap.appendChild(shelf);
    section.appendChild(shelfWrap);
    exploreSections.appendChild(section);
    bindExploreShelfNav(section, shelf);
  }
}

function mergeFreeItemsIntoHistory(items) {
  for (const item of items || []) {
    if (!item?.videoId) continue;
    const prev = state.history.get(item.videoId) || {};
    state.history.set(item.videoId, { ...prev, ...item, alreadyExisted: true });
  }
}

function findFreeShelf(shelfId) {
  for (const sec of state.freeSections) {
    const sh = (sec.shelves || []).find((s) => s.id === shelfId);
    if (sh) return sh;
  }
  return null;
}

async function ensureFreeQueueForCategory(categoryId, fallbackItems) {
  if (!categoryId) {
    state.freeListItems = fallbackItems || [];
    state.freeBrowseLabel = "Grátis no servidor";
    return;
  }
  const shelf = findFreeShelf(categoryId);
  state.freeBrowseLabel = shelf?.label || "Grátis no servidor";
  const limit = Math.min(200, Math.max(50, shelf?.total || fallbackItems?.length || 50));
  const res = await fetch(
    rutUrl(
      `/api/catalog/free/category/${encodeURIComponent(categoryId)}?offset=0&limit=${limit}`
    )
  );
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || res.statusText);
  const items = data.items || fallbackItems || [];
  mergeFreeItemsIntoHistory(items);
  state.freeListItems = items;
  state.freeBrowseCategoryId = categoryId;
}

function createFreeShelfCard(shelf) {
  const wrap = document.createElement("div");
  wrap.className = "mix-card-wrap";
  const preview = shelf.coverPreview || [];
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mix-card";
  btn.dataset.freeShelfId = shelf.id || "";
  btn.setAttribute("role", "listitem");
  const sub = shelf.subtitle || `${shelf.total || 0} faixas · sem busca`;
  btn.innerHTML = `${mixCoverArtHtml(preview)}<div class="mix-card-body"><span class="mix-card-title">${escapeHtml(shelf.label || "")}</span><span class="mix-card-sub">${escapeHtml(sub)}</span></div>`;
  btn.addEventListener("click", () => {
    void openFreeCategoryBrowse(shelf.id, shelf.label, { originEl: btn });
  });
  wrap.appendChild(btn);
  return wrap;
}

function scrollContentToFreeCategory(categoryId) {
  const target = document.getElementById(`free-section-${categoryId}`);
  const scrollRoot = document.querySelector(".content");
  if (!target || !scrollRoot) {
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  const top =
    target.getBoundingClientRect().top -
    scrollRoot.getBoundingClientRect().top +
    scrollRoot.scrollTop -
    6;
  scrollRoot.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
}

function setFreeBrowseUi(_active, _title = "") {
  homeMainBlock?.classList.remove("hidden");
}

function renderFreeList(items, { append = false, indexOffset = 0 } = {}) {
  if (!freeListEl) return;
  if (!append) freeListEl.innerHTML = "";
  if (!items.length && !append) {
    freeListEl.innerHTML = "<li class=\"status-line\">Nenhuma faixa nesta categoria.</li>";
    return;
  }
  items.forEach((item, i) => {
    freeListEl.appendChild(buildTrackRow(item, indexOffset + i, { mode: "free" }));
  });
  highlightPlayingRows();
  updateLibraryButtons();
  updateTrackRowLoadingStates();
}

function updateFreeShowMoreUi() {
  if (!freeShowMore) return;
  const hasMore = state.freeListItems.length < state.freeListTotal;
  freeShowMore.classList.toggle("hidden", !hasMore);
  freeShowMore.disabled = state.freeLoading;
  freeShowMore.textContent = state.freeLoading ? "Carregando…" : "Mostrar mais";
}

async function fetchFreeListPage({ reset = false } = {}) {
  const q = state.freeFilterQuery.trim();
  const offset = reset ? 0 : state.freeListOffset;
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(FREE_LIST_PAGE),
  });
  let url;
  if (q) {
    params.set("q", q);
    url = rutUrl(`/api/catalog/free/search?${params}`);
  } else if (state.freeBrowseCategoryId) {
    url = rutUrl(
      `/api/catalog/free/category/${encodeURIComponent(state.freeBrowseCategoryId)}?${params}`
    );
  } else {
    return;
  }
  state.freeLoading = true;
  updateFreeShowMoreUi();
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    const items = filterDiscoverableItems(data.items || []);
    mergeFreeItemsIntoHistory(items);
    if (reset) {
      state.freeListItems = items;
      state.freeListOffset = items.length;
    } else {
      state.freeListItems = state.freeListItems.concat(items);
      state.freeListOffset = state.freeListItems.length;
    }
    state.freeListTotal = data.total ?? state.freeListItems.length;
    renderFreeList(items, { append: !reset, indexOffset: reset ? 0 : state.freeListItems.length - items.length });
    updateFreeShowMoreUi();
  } catch (err) {
    if (freeStatusEl) freeStatusEl.textContent = err.message || "Erro ao carregar catálogo";
  } finally {
    state.freeLoading = false;
    updateFreeShowMoreUi();
  }
}

async function openFreeCategoryBrowse(categoryId, label, opts = {}) {
  pushNavigationReturn({ originEl: opts.originEl });
  if (state.view !== "home") {
    setView("home", { skipHomeRefresh: true });
  }
  await ensureServerCatalogLoaded();
  state.freeBrowseCategoryId = categoryId;
  state.freeBrowseLabel = label || "";
  state.freeFilterQuery = "";
  if (freeSearchInput) freeSearchInput.value = "";
  setFreeBrowseUi(true, label);
  if (freeStatusEl) freeStatusEl.textContent = "";
  await fetchFreeListPage({ reset: true });
}

function exitFreeBrowse() {
  state.freeBrowseCategoryId = null;
  state.freeBrowseLabel = "";
  state.freeFilterQuery = "";
  state.freeListItems = [];
  state.freeListOffset = 0;
  state.freeListTotal = 0;
  if (freeSearchInput) freeSearchInput.value = "";
  setFreeBrowseUi(false);
  if (freeStatusEl) freeStatusEl.textContent = "";
  freeShowMore?.classList.add("hidden");
}

function appendServerCatalogSections(
  container,
  { includeSectionIds = null, excludeSectionIds = [], useExploreIds = false } = {}
) {
  if (!container || !state.freeSections.length) return;
  for (const sec of state.freeSections) {
    const secId = sec.id || "";
    if (excludeSectionIds.includes(secId)) continue;
    if (includeSectionIds && !includeSectionIds.includes(secId)) continue;
    const shelves = sec.shelves || [];
    if (!shelves.length) continue;

    const titleId = useExploreIds
      ? `explore-class-${secId || "cat"}`
      : `free-class-${secId || "cat"}`;

    const section = document.createElement("section");
    section.className = "explore-class";
    if (!useExploreIds) section.id = `free-section-${secId || "cat"}`;
    section.dataset.category = secId || "";
    section.setAttribute("role", "listitem");
    section.setAttribute("aria-labelledby", titleId);

    const head = document.createElement("div");
    head.className = "explore-class-head";

    const title = document.createElement("h2");
    title.id = titleId;
    title.className = "explore-class-title";
    title.textContent = sec.label || "";
    head.appendChild(title);

    const nav = document.createElement("div");
    nav.className = "explore-class-nav";
    nav.innerHTML = `<button type="button" class="explore-mais-btn" hidden>Mais</button><button type="button" class="explore-scroll-btn" data-dir="prev" aria-label="Anterior">${EXPLORE_SHELF_SCROLL_ICON.prev}</button><button type="button" class="explore-scroll-btn" data-dir="next" aria-label="Próximo">${EXPLORE_SHELF_SCROLL_ICON.next}</button>`;
    head.appendChild(nav);
    section.appendChild(head);

    const shelfWrap = document.createElement("div");
    shelfWrap.className = "explore-shelf-wrap";
    const shelf = document.createElement("div");
    shelf.className = "explore-shelf";
    shelf.setAttribute("role", "list");

    for (const sh of shelves) {
      shelf.appendChild(createFreeShelfCard(sh));
    }

    shelfWrap.appendChild(shelf);
    section.appendChild(shelfWrap);
    container.appendChild(section);
    bindExploreShelfNav(section, shelf);
  }
}

async function loadServerCatalogForHome() {
  if (freeStatusEl) freeStatusEl.textContent = "";
  try {
    const res = await fetch(rutUrl("/api/catalog/free?shelf_limit=20"));
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    state.freeSections = data.sections || [];
    state.freeCatalogTotal = data.total ?? 0;
    for (const sec of state.freeSections) {
      for (const sh of sec.shelves || []) {
        mergeFreeItemsIntoHistory(sh.items);
      }
    }
  } catch (err) {
    if (freeStatusEl) {
      freeStatusEl.textContent = err.message || "Não foi possível carregar o catálogo no servidor";
    }
    state.freeSections = [];
    state.freeCatalogTotal = 0;
  }
}

function scheduleFreeFilterSearch() {
  if (freeSearchTimer) clearTimeout(freeSearchTimer);
  freeSearchTimer = setTimeout(() => {
    freeSearchTimer = null;
    void runFreeFilterSearch();
  }, 280);
}

async function runFreeFilterSearch() {
  const q = (freeSearchInput?.value || "").trim();
  state.freeFilterQuery = q;
  if (!q) {
    if (navigationBackAvailable()) navigateBackUi();
    else exitFreeBrowse();
    return;
  }
  const filterBrowseActive =
    freeBrowseBar && !freeBrowseBar.classList.contains("hidden") && state.freeFilterQuery;
  if (!filterBrowseActive) pushNavigationReturn();
  await ensureServerCatalogLoaded();
  state.freeBrowseCategoryId = null;
  state.freeBrowseLabel = `Filtrar: ${q}`;
  setFreeBrowseUi(true, state.freeBrowseLabel);
  await fetchFreeListPage({ reset: true });
}

freeSearchForm?.addEventListener("submit", (e) => {
  e.preventDefault();
  void runFreeFilterSearch();
});
freeSearchInput?.addEventListener("input", () => scheduleFreeFilterSearch());
freeBrowseBack?.addEventListener("click", () => navigateBackUi());
navViewBack?.addEventListener("click", () => navigateBackUi());
freeShowMore?.addEventListener("click", () => {
  void fetchFreeListPage({ reset: false });
});

async function startMix(mix) {
  const q = (mix?.label || mix?.query || "").trim();
  if (!q) return;
  await runTextSearch(q);
}

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => {
    const view = btn.dataset.view;
    if (view === "nowplaying") {
      openNowPlaying();
      return;
    }
    if (view === "search") {
      input.focus();
      return;
    }
    resetNavigationReturnStack();
    setView(view);
  });
});

input.addEventListener("focus", () => {
  openSearchFromInput();
});

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    input.focus();
    input.select();
  }
  if (e.code === "Space" && document.activeElement !== input) {
    e.preventDefault();
    togglePlayPause();
  }
});

function setStatus(msg, opts = false) {
  if (!statusEl) return;
  const options =
    typeof opts === "boolean" ? { error: opts, loading: false } : { error: false, loading: false, ...opts };
  const wasLoading = statusEl.classList.contains("is-loading");
  if (statusTextEl) statusTextEl.textContent = msg;
  else statusEl.textContent = msg;
  statusEl.classList.toggle("error", options.error);
  statusEl.classList.toggle("is-loading", options.loading);
  if (options.loading) {
    statusSpinnerEl?.style.setProperty("--progress", "0.28");
    setGlobalLoading(true);
  } else if (wasLoading) {
    setGlobalLoading(false);
  }
  statusSpinnerEl?.classList.toggle("hidden", true);
}

function setPlayerStatus(msg) {
  playerStatus.textContent = msg || "";
}

function formatQuotaUnits(n) {
  if (!Number.isFinite(n)) return "—";
  return Math.max(0, Math.round(n)).toLocaleString("pt-BR");
}

function clearQuotaIndicator() {
  if (!userMenuQuotaEl) return;
  userMenuQuotaEl.classList.add("hidden");
  userMenuQuotaEl.setAttribute("aria-hidden", "true");
  userMenuQuotaEl.title = "";
  userMenuQuotaEl.classList.remove("warn", "low");
  userMenuQuotaDividerEl?.classList.add("hidden");
  const titleEl = userMenuQuotaEl.querySelector(".user-menu-quota-title");
  const detailEl = userMenuQuotaEl.querySelector(".user-menu-quota-detail");
  if (titleEl) titleEl.textContent = "";
  if (detailEl) detailEl.textContent = "";
}

function showUserMenuQuota({ title, detail, level, titleAttr }) {
  if (!userMenuQuotaEl || !state.user) return;
  userMenuQuotaEl.classList.remove("hidden");
  userMenuQuotaEl.setAttribute("aria-hidden", "false");
  userMenuQuotaEl.title = titleAttr || "";
  userMenuQuotaEl.classList.toggle("warn", level === "warn");
  userMenuQuotaEl.classList.toggle("low", level === "low");
  userMenuQuotaDividerEl?.classList.remove("hidden");
  const titleEl = userMenuQuotaEl.querySelector(".user-menu-quota-title");
  const detailEl = userMenuQuotaEl.querySelector(".user-menu-quota-detail");
  if (titleEl) titleEl.textContent = title;
  if (detailEl) detailEl.textContent = detail;
}

function renderQuotaIndicator() {
  if (!userMenuQuotaEl || !state.user) {
    clearQuotaIndicator();
    return;
  }

  const q = state.quotaSnapshot;
  const us = q?.userSearch;
  const userSearchTitleAttr =
    "Cada consulta nova de busca consome 1 das suas buscas diárias. Resultados em cache e «Mostrar mais» de mix já aberto não contam. Reinicia à meia-noite (horário dos EUA).";

  if (us && (us.unlimited || (typeof us.remaining === "number" && typeof us.limit === "number"))) {
    if (us.unlimited) {
      clearQuotaIndicator();
      return;
    }

    let level = "ok";
    let title = "Suas buscas hoje";
    let detail = `${us.remaining} de ${us.limit} consultas restantes`;
    if (us.remaining <= 0) {
      level = "low";
      title = "Sem buscas hoje";
      detail =
        "Ouça em Recentes, Biblioteca ou mixes já carregados. «Mostrar mais» do catálogo salvo não gasta.";
    } else if (us.remaining <= 1) {
      level = "low";
      title = "Última busca do dia";
      detail = "1 consulta restante · cache e catálogo salvo no servidor não consomem.";
    } else if (us.remaining <= 2) {
      level = "warn";
      detail = `${us.remaining} de ${us.limit} consultas restantes · use com cuidado.`;
    }

    showUserMenuQuota({ title, detail, level, titleAttr: userSearchTitleAttr });
    return;
  }

  if (!q || typeof q.remaining !== "number" || typeof q.limit !== "number") {
    clearQuotaIndicator();
    return;
  }

  const remaining = q.remaining;
  const reserve = Number(q.minRemainingSearch) > 0 ? Number(q.minRemainingSearch) : 120;
  let level = "ok";
  let title = "Cota da API (estimativa)";
  let detail = `Cerca de ${formatQuotaUnits(remaining)} un. restantes hoje.`;
  if (remaining <= 0) {
    level = "low";
    title = "Buscas indisponíveis";
    detail = "Mixes em cache, recentes e biblioteca continuam disponíveis.";
  } else if (remaining <= reserve) {
    level = "low";
    title = "Pouca cota restante";
    detail = `${formatQuotaUnits(remaining)} un. estimadas · novas buscas podem falhar.`;
  } else if (remaining <= Math.max(500, Math.floor(q.limit * 0.35))) {
    level = "warn";
  }

  showUserMenuQuota({
    title,
    detail,
    level,
    titleAttr:
      "Estimativa do servidor. Reinicia à meia-noite (horário dos EUA). Downloads e cache local não consomem busca.",
  });
}

async function refreshQuota() {
  try {
    const res = await fetch("/api/quota");
    const data = await res.json();
    if (res.ok) {
      state.quotaSnapshot = data;
      renderQuotaIndicator();
    }
  } catch {
    /* silencioso */
  }
}

function setPlayUi(playing) {
  if (!playing) holdMediaSessionPlaying = false;
  state.isPlaying = playing;
  if (!state.isLoading) {
    iconPlaySpinner?.classList.add("hidden");
    iconPlay.classList.toggle("hidden", playing);
    iconPause.classList.toggle("hidden", !playing);
  }
  highlightPlayingRows();
  syncMediaSessionPlaybackState();
}

function trackLoadKey(item) {
  if (item?.deezerId) return `dz:${item.deezerId}`;
  return item?.videoId || "";
}

function getTrackRowLoadingId() {
  if (state.rowLoadingVideoId) return state.rowLoadingVideoId;
  if (state.isLoading && state.pendingPlayVideoId) return state.pendingPlayVideoId;
  return null;
}

function rowMatchesLoading(row) {
  const loadingId = getTrackRowLoadingId();
  const key = state.rowLoadingKey;
  if (loadingId && row.dataset.videoId && row.dataset.videoId === loadingId) return true;
  if (key?.startsWith("dz:") && row.dataset.deezerId === key.slice(3)) return true;
  if (key && row.dataset.videoId === key) return true;
  return false;
}

function updateTrackRowLoadingProgress(videoId, progressFraction) {
  const p = Math.max(0.08, Math.min(1, progressFraction ?? 0.15));
  document.querySelectorAll(".track-row").forEach((row) => {
    const matchVid = videoId && row.dataset.videoId === videoId;
    if (!matchVid && !rowMatchesLoading(row)) return;
    row.querySelector(".col-play-spinner")?.style.setProperty("--progress", String(p));
  });
}

function updateTrackRowLoadingStates() {
  const progress =
    iconPlaySpinner?.style.getPropertyValue("--progress")?.trim() || "0.15";
  document.querySelectorAll(".track-row").forEach((row) => {
    const loading = rowMatchesLoading(row);
    row.classList.toggle("is-loading", loading);
    const cover = row.querySelector(".col-cover");
    const spin = row.querySelector(".col-play-spinner");
    spin?.classList.toggle("hidden", !loading);
    if (loading) {
      spin?.style.setProperty("--progress", progress);
      cover?.setAttribute("aria-busy", "true");
    } else {
      cover?.removeAttribute("aria-busy");
    }
  });
}

function setPlayLoading(loading, progressFraction = null) {
  state.isLoading = loading;
  btnPlay.classList.toggle("loading", loading);
  btnPlay.disabled = loading;
  if (progressFraction != null) {
    const p = Math.max(0.08, Math.min(1, progressFraction));
    iconPlaySpinner?.style.setProperty("--progress", String(p));
  }
  if (loading) {
    iconPlaySpinner?.classList.remove("hidden");
    iconPlay.classList.add("hidden");
    iconPause.classList.add("hidden");
  } else {
    iconPlaySpinner?.classList.add("hidden");
    setPlayUi(state.isPlaying);
  }
  syncMediaSessionPlaybackState();
  updateTrackRowLoadingStates();
  updateStopQueueButton();
}

function updatePlayerBar(item) {
  if (!item) return;
  const thumb = higherResThumb(item.thumbnailUrl || "");
  if (thumb) {
    playerCover.src = thumb;
    playerCover.classList.remove("hidden");
  }
  playerTitle.textContent = item.title || "Sem título";
  const credit = trackCreditLine(item);
  if (playerArtistBtn) {
    if (credit.label) {
      playerArtistBtn.textContent = creditDisplayLabel(credit.label);
      playerArtistBtn.dataset.searchQuery = credit.query;
      playerArtistBtn.dataset.creditKind = credit.kind || "";
      playerArtistBtn.dataset.channelId = credit.channelId || "";
      playerArtistBtn.title = creditFullTitle(credit);
      playerArtistBtn.classList.remove("hidden");
    } else {
      playerArtistBtn.textContent = "";
      playerArtistBtn.dataset.searchQuery = "";
      playerArtistBtn.dataset.creditKind = "";
      playerArtistBtn.dataset.channelId = "";
      playerArtistBtn.classList.add("hidden");
    }
  }
  btnLibrary.classList.toggle("hidden", !item.videoId);
  btnLibrary.dataset.videoId = item.videoId || "";
  updateLibraryButtons();
  updatePlayerSourceLink();
  syncMediaSessionMetadata(item);
  if (state.view === "nowplaying") syncNpHeroFromPlayer();
}

function highlightPlayingRows() {
  const audibleId = videoIdFromAudioSrc();
  const uiCurrentId = audibleId || state.playingId;
  const loadingId = getTrackRowLoadingId();
  document.querySelectorAll(".track-row").forEach((row) => {
    const isCurrent = row.dataset.videoId === uiCurrentId;
    const loading = Boolean(loadingId && row.dataset.videoId === loadingId);
    row.classList.toggle("playing", isCurrent);
    row.classList.toggle("is-playing", isCurrent && state.isPlaying && !loading);
    const colPlay = row.querySelector(".col-play");
    if (colPlay && !loading) {
      const showPause = isCurrent && state.isPlaying && Boolean(audio.src);
      colPlay.setAttribute("aria-label", showPause ? "Pausar" : "Tocar");
    }
  });
  updateTrackRowLoadingStates();
}

function shuffleInPlace(arr) {
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function alignQueueIndexToVideoId(videoId) {
  if (!videoId || !state.queue.length) return false;
  if (state.queue[state.queueIndex]?.videoId === videoId) return true;
  const idx = state.queue.findIndex((i) => i.videoId === videoId);
  if (idx < 0) return false;
  if (state.queueIndex !== idx) {
    state.queueIndex = idx;
    rebuildPlayOrder();
    updateTransportControls();
  }
  return true;
}

function rebuildPlayOrder() {
  const n = state.queue.length;
  if (!n) {
    state.playOrder = [];
    return;
  }
  if (!state.shuffle) {
    state.playOrder = Array.from({ length: n }, (_, i) => i);
    return;
  }
  const cur = state.queueIndex >= 0 ? state.queueIndex : 0;
  const rest = Array.from({ length: n }, (_, i) => i).filter((i) => i !== cur);
  shuffleInPlace(rest);
  state.playOrder = [cur, ...rest];
}

function getOrderPosition() {
  if (state.queueIndex < 0 || !state.queue.length) return -1;
  const order = state.playOrder.length ? state.playOrder : state.queue.map((_, i) => i);
  return order.indexOf(state.queueIndex);
}

function updateTransportControls() {
  const n = state.queue.length;
  const pos = getOrderPosition();
  const order = state.playOrder.length ? state.playOrder : state.queue.map((_, i) => i);

  btnShuffle.classList.toggle("active", state.shuffle);
  btnShuffle.setAttribute("aria-pressed", state.shuffle ? "true" : "false");
  btnShuffle.title = state.shuffle ? "Ordem aleatória ligada" : "Ordem aleatória";

  btnRepeat.dataset.repeat = state.repeat;
  btnRepeat.classList.toggle("active", state.repeat !== "off");
  btnRepeat.setAttribute("aria-pressed", state.repeat !== "off" ? "true" : "false");
  repeatOneBadge.classList.toggle("hidden", state.repeat !== "one");
  const repeatTitles = {
    off: "Repetir desligado",
    all: "Repetir playlist",
    one: "Repetir faixa atual",
  };
  btnRepeat.title = repeatTitles[state.repeat] || repeatTitles.off;

  if (!n || state.queueIndex < 0) {
    btnPrev.disabled = true;
    btnNext.disabled = true;
    updateStopQueueButton();
    return;
  }

  const atStart = pos <= 0;
  const atEnd = pos >= order.length - 1;
  const canWrap = state.repeat === "all";
  const canContinue =
    atEnd &&
    state.repeat !== "all" &&
    state.repeat !== "one" &&
    Boolean(playbackArtistId() || state.catalogOrigin?.kind === "playlist");
  const canNext = !atEnd || canWrap || state.repeat === "one" || canContinue;
  const canPrev =
    !atStart ||
    canWrap ||
    (audio.src && audio.currentTime > 3);

  btnNext.disabled = !canNext;
  btnPrev.disabled = !canPrev && !(audio.src && audio.currentTime > 3);
  updateStopQueueButton();
}

function setPlaybackQueue(items, videoId, source) {
  state.queue = items.filter((i) => i && (i.videoId || i.deezerId));
  state.queueSource = source;
  const idx = state.queue.findIndex(
    (i) => i.videoId === videoId || (i.deezerId && `dz:${i.deezerId}` === videoId)
  );
  state.queueIndex = idx >= 0 ? idx : 0;
  rebuildPlayOrder();
  updateTransportControls();
  snapshotPlaybackContext(source);
  updatePlayerSourceLink();
  if (state.view === "nowplaying") renderNowPlaying();
}

let exploreListTracks = [];
let searchListTracks = [];

function syncCatalogListPlayButtons() {
  const deezerCount = deezerTracksEl?.querySelectorAll(".track-row").length || 0;
  const searchCount = resultsEl?.querySelectorAll(".track-row").length || 0;
  document.getElementById("deezer-list-play")?.classList.toggle("hidden", deezerCount < 1);
  document.getElementById("search-list-play")?.classList.toggle("hidden", searchCount < 1);
}

function playListedTracks(tracks) {
  const list = (tracks || []).filter((item) => item && (item.videoId || item.deezerId));
  if (!list.length) return;
  state.deezerTracks = list;
  state.autoAdvanceEnabled = true;
  playFromList(list[0], "deezer");
}

document.getElementById("deezer-list-play")?.addEventListener("click", () => {
  playListedTracks(exploreListTracks);
});
document.getElementById("search-list-play")?.addEventListener("click", () => {
  playListedTracks(searchListTracks);
});

function playFromList(item, mode) {
  let items;
  if (mode === "history") items = state.historyItems;
  else if (mode === "library") items = state.libraryItems;
  else if (mode === "search") {
    items = filterDiscoverableItems(state.searchCatalog.filter((i) => i.videoId));
  } else if (mode === "free") {
    items = filterDiscoverableItems(state.freeListItems.filter((i) => i.videoId));
  }
  else if (mode === "serverlibrary") items = state.serverLibraryItems.filter((i) => i.videoId);
  else if (mode === "deezer") items = state.deezerTracks?.length ? state.deezerTracks : [item];
  else if (mode === "queue") items = state.queue;
  else items = state.queue.length ? state.queue : [item];
  const queueKey = item.videoId || (item.deezerId ? `dz:${item.deezerId}` : "");
  setPlaybackQueue(items, queueKey, mode);
  playItem(item, { setQueue: false });
  if (state.queue.length < 2) void expandPlaybackQueue();
}

function notePlayedOrigin(origin) {
  if (!origin?.id) return;
  if (!state.playedAlbumIds) state.playedAlbumIds = new Set();
  if (!state.continuedArtistIds) state.continuedArtistIds = new Set();
  if (origin.kind === "album") state.playedAlbumIds.add(String(origin.id));
  if (origin.kind === "artist") state.continuedArtistIds.add(String(origin.id));
}

function playbackArtistId() {
  const item = state.current || state.queue[state.queueIndex];
  if (item?.artistId != null && item.artistId !== "") return item.artistId;
  if (state.catalogOrigin?.kind === "artist" && state.catalogOrigin.id) return state.catalogOrigin.id;
  return null;
}

function rememberContinuation(origin) {
  state.catalogOrigin = origin;
  if (state.playbackContext) state.playbackContext.catalogOrigin = origin;
  notePlayedOrigin(origin);
}

function appendTracksToQueue(tracks) {
  const seen = new Set(
    state.queue.map((row) => (row?.deezerId != null ? `dz:${row.deezerId}` : row?.videoId || ""))
  );
  const fresh = [];
  for (const row of tracks || []) {
    if (!row || (!row.deezerId && !row.videoId)) continue;
    const key = row.deezerId != null ? `dz:${row.deezerId}` : row.videoId;
    if (seen.has(key)) continue;
    seen.add(key);
    fresh.push(row);
  }
  if (!fresh.length) return -1;
  const start = state.queue.length;
  state.queue = state.queue.concat(fresh);
  state.queueSource = "deezer";
  const extra = [];
  for (let i = start; i < state.queue.length; i += 1) extra.push(i);
  const pos = state.playOrder.indexOf(state.queueIndex);
  const head = pos >= 0 ? state.playOrder.slice(0, pos + 1) : state.playOrder.slice();
  state.playOrder = [...head, ...extra];
  updateTransportControls();
  return start;
}

async function nextAlbumTracks(artistId) {
  const data = await deezerGet(`/api/catalog/deezer/artists/${encodeURIComponent(artistId)}`);
  const played = state.playedAlbumIds || new Set();
  if (state.catalogOrigin?.kind === "album" && state.catalogOrigin.id) {
    played.add(String(state.catalogOrigin.id));
  }
  state.playedAlbumIds = played;
  for (const album of data.albums || []) {
    if (album?.id == null || played.has(String(album.id))) continue;
    const page = await deezerGet(`/api/catalog/deezer/albums/${encodeURIComponent(album.id)}`);
    const queued = new Set(
      state.queue.map((row) => (row?.deezerId != null ? String(row.deezerId) : "")).filter(Boolean)
    );
    const fresh = (page.tracks || []).filter(
      (row) => row?.deezerId == null || !queued.has(String(row.deezerId))
    );
    played.add(String(album.id));
    if (!fresh.length) continue;
    rememberContinuation({
      kind: "album",
      id: String(album.id),
      title: page.album?.title || album.title || "",
    });
    return fresh;
  }
  return [];
}

async function pullContinuationTracks() {
  const artistId = playbackArtistId();
  if (artistId) {
    const albumTracks = await nextAlbumTracks(artistId);
    if (albumTracks.length) return { tracks: albumTracks, label: "Próximo álbum…" };
  }
  if (artistId) {
    const seen = state.continuedArtistIds || new Set();
    seen.add(String(artistId));
    state.continuedArtistIds = seen;
    try {
      const related = await deezerGet(
        `/api/catalog/deezer/artists/${encodeURIComponent(artistId)}/related`
      );
      const next = (related.artists || []).find(
        (artist) => artist?.id != null && !seen.has(String(artist.id))
      );
      if (next) {
        seen.add(String(next.id));
        rememberContinuation({ kind: "artist", id: String(next.id), title: next.name || "" });
        const page = await deezerGet(`/api/catalog/deezer/artists/${encodeURIComponent(next.id)}`);
        if ((page.tracks || []).length) {
          return { tracks: page.tracks, label: next.name || "Faixas parecidas…" };
        }
      }
    } catch {
      /* segue para o rádio */
    }
    const radio = await deezerGet(`/api/catalog/deezer/artists/${encodeURIComponent(artistId)}/radio`);
    if ((radio.tracks || []).length) return { tracks: radio.tracks, label: "Faixas parecidas…" };
  }
  return { tracks: [], label: "" };
}

function queueContinuation() {
  if (state.continuationInFlight || state.repeat === "all" || state.repeat === "one") return false;
  if (!playbackArtistId() && state.catalogOrigin?.kind !== "playlist") return false;
  state.continuationInFlight = true;
  void continuePlaybackAfterQueue();
  return true;
}

async function continuePlaybackAfterQueue() {
  const fromId = state.current?.videoId || state.playingId || null;
  setPlayerStatus("Próximo álbum…");
  try {
    const pulled = await pullContinuationTracks();
    if (pulled.label) setPlayerStatus(pulled.label);
    if (fromId && state.current?.videoId && state.current.videoId !== fromId) return;
    const start = appendTracksToQueue(pulled.tracks);
    if (start < 0) {
      holdMediaSessionPlaying = false;
      setPlayUi(false);
      setPlayerStatus("");
      updateTransportControls();
      return;
    }
    state.queueIndex = start;
    const next = state.queue[start];
    if (state.view === "nowplaying") renderNowPlaying();
    await playItem(next, { setQueue: false, skipViewChange: true });
  } catch {
    holdMediaSessionPlaying = false;
    setPlayUi(audio.paused ? false : state.isPlaying);
    setPlayerStatus("");
    updateTransportControls();
  } finally {
    state.continuationInFlight = false;
  }
}

function advancePlayback(direction) {
  if (!state.queue.length || state.queueIndex < 0) return false;

  const curId =
    videoIdFromAudioSrc() || state.playingId || state.current?.videoId || null;
  if (curId) alignQueueIndexToVideoId(curId);

  if (direction < 0 && audio.src && audio.currentTime > 3) {
    audio.currentTime = 0;
    updateTransportControls();
    return true;
  }

  if (direction > 0 && state.repeat !== "one" && handoffPrimedNext()) return true;

  const order = state.playOrder.length ? state.playOrder : state.queue.map((_, i) => i);
  const pos = order.indexOf(state.queueIndex);
  if (pos < 0) return false;

  if (direction < 0) {
    if (pos <= 0) {
      if (state.repeat !== "all") return false;
      state.queueIndex = order[order.length - 1];
    } else {
      state.queueIndex = order[pos - 1];
    }
  } else if (state.repeat === "one") {
    /* mantém índice */
  } else if (pos >= order.length - 1) {
    if (state.repeat === "all") {
      state.queueIndex = order[0];
    } else if (direction > 0 && queueContinuation()) {
      return true;
    } else {
      return false;
    }
  } else {
    state.queueIndex = order[pos + 1];
  }

  playItem(state.queue[state.queueIndex], { setQueue: false, skipViewChange: true });
  return true;
}

function isServerAudioUrl(url) {
  return typeof url === "string" && url.includes("/api/downloads/");
}

function hasCachedAudio(videoId) {
  const hist = state.history.get(videoId);
  return isServerAudioUrl(hist?.url);
}

function isTrackOnServer(item) {
  const videoId = item?.videoId;
  if (!videoId) return false;
  if (item.onServer) return true;
  if (state.serverVideoIds.has(videoId)) return true;
  if (isServerAudioUrl(item.url)) return true;
  return hasCachedAudio(videoId);
}

async function loadServerVideoIds() {
  try {
    const res = await fetch(rutUrl("/api/catalog/server-video-ids"));
    const data = await res.json();
    if (!res.ok) return;
    state.serverVideoIds = new Set(data.videoIds || []);
    refreshOnServerBadges();
  } catch {
    /* silencioso */
  }
}

async function loadDownloadBlocklist() {
  try {
    const res = await fetch(rutUrl("/api/catalog/download-blocklist"));
    const data = await res.json();
    if (!res.ok) return;
    state.downloadBlocklistIds = new Set(data.videoIds || []);
    if (Number.isFinite(data.maxFileSizeMb)) {
      state.maxDownloadFileMb = data.maxFileSizeMb;
    }
    purgeAllBlocklistedFromUi();
    evictHiddenTracksFromCatalog();
    refreshDiscoverableListsAfterPurge();
  } catch {
    /* silencioso */
  }
}

function refreshOnServerBadges() {
  if (state.view === "search") renderSearchVisible();
  if (state.libraryItems?.length) renderBiblioteca(state.libraryItems);
  if (state.serverLibraryItems?.length) {
    renderServerLibrary(state.serverLibraryItems, state.serverLibraryTotal ?? 0);
  }
  if (state.historyItems?.length) renderHistory(state.historyItems);
  if (state.freeListItems?.length && freeListEl) {
    const offset = state.freeListOffset || 0;
    freeListEl.innerHTML = "";
    state.freeListItems.forEach((item, i) => {
      freeListEl.appendChild(buildTrackRow(item, offset + i, { mode: "free" }));
    });
    highlightPlayingRows();
  }
  document.querySelectorAll("#now-playing-list .track-row").forEach((row, i) => {
    const item = state.queue[i];
    if (!item?.videoId && item?.deezerId == null) return;
    syncTrackRowServerBadge(row, item);
  });
  syncDeezerRowBadges();
}

const knownDeezerAudio = new Map();
let knownDeezerTimer = null;
const knownDeezerWait = [];

function scheduleKnownDeezerAudio(tracks) {
  if (tracks?.length) knownDeezerWait.push(tracks);
  clearTimeout(knownDeezerTimer);
  knownDeezerTimer = setTimeout(() => {
    const lists = knownDeezerWait.splice(0);
    void refreshKnownDeezerAudio(lists.flat());
  }, 40);
}

async function refreshKnownDeezerAudio(tracks) {
  const pending = [];
  const seen = new Set();
  for (const item of tracks || []) {
    if (item?.deezerId == null || isTrackOnServer(item)) continue;
    const key = String(item.deezerId);
    if (knownDeezerAudio.has(key) || seen.has(key)) continue;
    seen.add(key);
    pending.push(item.deezerId);
  }
  if (pending.length) {
    try {
      const res = await fetch(rutUrl("/api/catalog/deezer/known"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ deezerIds: pending.slice(0, 200) }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        const items = data.items || {};
        for (const id of pending) {
          knownDeezerAudio.set(String(id), items[String(id)] || null);
        }
      }
    } catch {
      /* a lista segue e o check entra quando der */
    }
  }
  let changed = false;
  for (const item of tracks || []) {
    if (item?.deezerId == null) continue;
    const known = knownDeezerAudio.get(String(item.deezerId));
    if (!known?.videoId) continue;
    if (!item.videoId) {
      item.videoId = known.videoId;
      changed = true;
    }
    if (known.onServer && !item.onServer) {
      item.onServer = true;
      changed = true;
    }
  }
  if (changed) syncDeezerRowBadges();
}

function syncDeezerRowBadges() {
  const byId = new Map();
  for (const item of state.deezerTracks || []) {
    if (item?.deezerId != null) byId.set(String(item.deezerId), item);
  }
  for (const item of state.queue || []) {
    if (item?.deezerId != null) byId.set(String(item.deezerId), item);
  }
  document.querySelectorAll(".track-row[data-deezer-id]").forEach((row) => {
    const item = byId.get(row.dataset.deezerId);
    if (item) syncTrackRowServerBadge(row, item);
  });
  document.querySelectorAll("#now-playing-list .track-row").forEach((row, i) => {
    const item = state.queue[i];
    if (item) syncTrackRowServerBadge(row, item);
  });
}

function syncTrackRowServerBadge(row, item) {
  if (!row || !item) return;
  const cover = row.querySelector(".col-cover");
  if (!cover) return;
  const hasBadge = cover.querySelector(".on-server-badge");
  const onServer = isTrackOnServer(item);
  if (onServer && !hasBadge) {
    cover.insertAdjacentHTML("beforeend", onServerBadgeHtml());
  } else if (!onServer && hasBadge) {
    hasBadge.remove();
  }
}

function onServerBadgeHtml({ inline = false } = {}) {
  const cls = inline ? "on-server-badge inline" : "on-server-badge";
  return `<span class="${cls}" title="${escapeHtml(ON_SERVER_BADGE_TITLE)}" aria-label="${escapeHtml(ON_SERVER_BADGE_TITLE)}">✓</span>`;
}

function markMixLoaded(mixId) {
  if (!mixId) return;
  state.loadedMixIds.add(mixId);
  document.querySelectorAll(`.mix-card[data-mix-id="${CSS.escape(mixId)}"]`).forEach((btn) => {
    const wrap = btn.closest(".mix-card-wrap");
    if (wrap) attachMixLoadedBadge(wrap, { mixId });
  });
}

function attachMixLoadedBadge(wrap, { mixId = null } = {}) {
  if (!wrap || !mixId || !state.loadedMixIds.has(mixId)) return;
  if (wrap.querySelector(".mix-loaded-badge")) return;
  const badge = document.createElement("span");
  badge.className = "mix-loaded-badge";
  badge.title = MIX_LOADED_BADGE_TITLE;
  badge.setAttribute("aria-label", MIX_LOADED_BADGE_TITLE);
  badge.textContent = "✓";
  wrap.appendChild(badge);
}

function syncMixSearchMeta(data) {
  if (!state.searchMixId || !data) return;
  if (typeof data.mixCatalogTotal === "number") {
    state.searchMixCatalogTotal = data.mixCatalogTotal;
  }
  if (data.mixCatalogLoaded && state.searchMixId) {
    markMixLoaded(state.searchMixId);
  }
}

function mixSearchHasMoreToLoad() {
  if (state.searchMixId) {
    if (!state.searchCatalog.length) return false;
    if (state.searchVisibleCount < state.searchCatalog.length) return true;
    if (state.searchNextPageToken) return true;
    const total = state.searchMixCatalogTotal;
    if (typeof total === "number" && total > state.searchCatalog.length) return true;
    return false;
  }
  if (!state.searchCatalog.length) return false;
  if (state.searchVisibleCount < state.searchCatalog.length) return true;
  return Boolean(state.searchNextPageToken);
}

function shouldShowCatalogShowMore() {
  if (!mixSearchHasMoreToLoad()) return false;
  if (state.searchMixId) return true;
  if (state.searchQuery || state.searchChannelId) return true;
  return false;
}

function mixHasMoreOnServerCatalog() {
  if (!state.searchMixId) return false;
  const total = state.searchMixCatalogTotal;
  return typeof total === "number" && total > state.searchCatalog.length;
}

/** Próximo clique em "Mostrar mais" chama busca YouTube (cota), não só catálogo local. */
function showMoreNextStepUsesYoutubeApi() {
  const prevVisible = state.searchVisibleCount;
  const step = prevVisible === 0 ? SEARCH_INITIAL_VISIBLE : SEARCH_SHOW_MORE_STEP;
  const target = prevVisible + step;

  if (target <= state.searchCatalog.length) return false;

  if (mixHasMoreOnServerCatalog()) return false;

  return Boolean(state.searchNextPageToken);
}

const SHOW_MORE_COST_TITLE =
  "Próximo lote vem da API do YouTube (usa cota; não usa só o catálogo salvo no servidor)";

function fillShowMoreButton(btn, { loading, disabled, showCost }) {
  if (!btn) return;
  btn.disabled = disabled;
  btn.replaceChildren();
  btn.append(document.createTextNode(loading ? "Carregando…" : "Mostrar mais"));
  if (showCost && !loading) {
    const badge = document.createElement("span");
    badge.className = "show-more-cost-badge";
    badge.title = SHOW_MORE_COST_TITLE;
    badge.setAttribute("aria-label", SHOW_MORE_COST_TITLE);
    badge.textContent = "✓$";
    btn.appendChild(badge);
  }
}

function updateCatalogShowMoreUi() {
  const show = shouldShowCatalogShowMore();
  const canLoad = mixSearchHasMoreToLoad();
  const loading = state.searchLoadingMore;
  const showCost = show && showMoreNextStepUsesYoutubeApi();
  const opts = { loading, disabled: loading || !canLoad, showCost };

  if (searchShowMore) {
    searchShowMore.classList.toggle("hidden", !show || state.view !== "search");
    if (show && state.view === "search") fillShowMoreButton(searchShowMore, opts);
  }
  if (npShowMore) {
    npShowMore.classList.toggle("hidden", !show || state.view !== "nowplaying");
    if (show && state.view === "nowplaying") fillShowMoreButton(npShowMore, opts);
  }
}

async function fetchMixCatalogBatch() {
  if (!state.searchMixId) return false;
  const beforeLen = state.searchCatalog.length;
  const exclude = state.searchCatalog.map((i) => i.videoId).filter(Boolean).join(",");
  const url = new URL(
    rutUrl(`/api/mixes/${encodeURIComponent(state.searchMixId)}/catalog`),
    window.location.origin
  );
  url.searchParams.set("limit", String(SEARCH_SHOW_MORE_STEP));
  if (exclude.length) url.searchParams.set("exclude", exclude);
  const songKeys = searchCatalogSongKeys();
  if (songKeys.length) url.searchParams.set("exclude_song_keys", songKeys.join(","));

  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(apiErrorFromResponse(res, data));

  syncMixSearchMeta(data);
  const batch = data.items || [];
  if (!batch.length) return false;

  const seenIds = new Set(state.searchCatalog.map((i) => i.videoId));
  const seenSongKeys = new Set(songKeys);
  for (const item of batch) {
    if (!item.videoId || seenIds.has(item.videoId)) continue;
    const merged = mergeLocalCatalogHints(item);
    if (shouldHideTrackFromLists(merged)) continue;
    const songKey = similarTrackDedupeKey(merged);
    if (songKey && seenSongKeys.has(songKey)) continue;
    state.searchCatalog.push(merged);
    seenIds.add(item.videoId);
    if (songKey) seenSongKeys.add(songKey);
  }
  compactSearchCatalog();
  if (state.searchMixId && batch.length) {
    void submitMixCoversFromItems(state.searchMixId, batch);
  }
  if (shouldBindSearchResultsToQueue()) syncSearchQueue();
  refreshQuota();
  hydrateSearchCatalogInBackground();
  return state.searchCatalog.length > beforeLen;
}

function mergeHistoryEntry(data) {
  if (!data?.videoId) return;
  const prev = state.history.get(data.videoId) || {};
  state.history.set(data.videoId, { ...prev, ...data });
  if (isServerAudioUrl(data.url) || data.alreadyExisted) {
    state.serverVideoIds.add(data.videoId);
    refreshOnServerBadges();
  }
}

function getUpcomingTracks(max = PREFETCH_AHEAD) {
  if (state.queueIndex < 0 || !state.queue.length) return [];
  const order =
    state.playOrder.length > 0
      ? state.playOrder
      : state.queue.map((_, i) => i);
  const pos = order.indexOf(state.queueIndex);
  if (pos < 0) return [];

  const out = [];
  const maxSteps = order.length * 2 + max + 2;
  for (let step = 1; step < maxSteps && out.length < max; step += 1) {
    const nextPos = pos + step;
    let track;
    if (nextPos < order.length) {
      track = state.queue[order[nextPos]];
    } else {
      if (state.repeat !== "all") break;
      if (order.length <= 1) break;
      const wrap = nextPos % order.length;
      track = state.queue[order[wrap]];
      if (wrap <= pos && step >= order.length) break;
    }
    if (!trackEligibleForPrefetch(track)) continue;
    out.push(track);
  }
  return out;
}

function trackEligibleForPrefetch(track) {
  if (!track || (!track.videoId && !track.deezerId)) return false;
  if (track.videoId && hasCachedAudio(track.videoId)) return false;
  const sec = durationIsoToSeconds(track.duration);
  if (sec != null && sec > AUTO_PREFETCH_MAX_DURATION_SEC) return false;
  if (isOverMaxFileSizeEstimate(track)) return false;
  if (track.videoId && isTrackDownloadBlocked(track)) return false;
  if (track.videoId && isCatalogHiddenVideo(track) && !isTrackOnServer(track)) return false;
  return true;
}

async function prefetchTracksSequential(items, generation) {
  for (const item of items) {
    if (generation !== state.prefetchGeneration || !state.autoAdvanceEnabled) return;
    try {
      if (!item.videoId && item.deezerId) await ensureDeezerResolved(item, { quiet: true });
    } catch {
      continue;
    }
    if (generation !== state.prefetchGeneration || !state.autoAdvanceEnabled) return;
    if (!item?.videoId || hasCachedAudio(item.videoId)) continue;
    if (!isAutoPrefetchAllowed(item)) continue;

    try {
      await scheduleDownload(item.videoId, item, DOWNLOAD_PRIORITY_PREFETCH);
      if (generation !== state.prefetchGeneration) return;
    } catch {
      /* carregamento em segundo plano */
    }
  }
  if (generation === state.prefetchGeneration) {
    refreshQuota();
    refreshHistory();
  }
}

async function prefetchQueueAhead(generation) {
  const upcoming = getUpcomingTracks(PREFETCH_AHEAD);
  const ids = upcoming.map((t) => t.videoId).filter(Boolean);
  try {
    await ensureVideoIdsHydrated(ids);
  } catch {
    /* prefetch segue sem duração */
  }
  if (generation !== state.prefetchGeneration) return;
  await prefetchTracksSequential(upcoming, generation);
}

function releaseBlobUrl(url) {
  if (!url || url === activeBlobUrl || !String(url).startsWith("blob:")) return;
  try {
    URL.revokeObjectURL(url);
  } catch {
    /* já liberado */
  }
}

function clearPrimedNext() {
  primeToken += 1;
  primeAbort?.abort();
  primeAbort = null;
  const blob = primedNext?.blobUrl || "";
  primedNext = null;
  releaseBlobUrl(blob);
}

function serverAudioUrlFor(item) {
  if (isServerAudioUrl(item?.url)) return item.url;
  const hist = item?.videoId ? state.history.get(item.videoId) : null;
  if (isServerAudioUrl(hist?.url)) return hist.url;
  return "";
}

function peekNextQueueSlot() {
  if (!state.queue.length || state.queueIndex < 0 || state.repeat === "one") return null;
  const order = state.playOrder.length ? state.playOrder : state.queue.map((_, i) => i);
  const pos = order.indexOf(state.queueIndex);
  if (pos < 0) return null;
  const queueIndex = pos >= order.length - 1 ? (state.repeat === "all" ? order[0] : -1) : order[pos + 1];
  if (queueIndex < 0) return null;
  const item = state.queue[queueIndex];
  if (!item) return null;
  return { item, queueIndex };
}

function readyNextForHandoff() {
  const slot = peekNextQueueSlot();
  if (!slot?.item) return null;
  const slotId = slot.item.videoId || "";
  const primed = primedNext;
  const primedMatches = Boolean(
    primed &&
      ((slotId && primed.videoId === slotId) ||
        (!slotId &&
          slot.item.deezerId != null &&
          String(primed.deezerId) === String(slot.item.deezerId)))
  );
  if (primedMatches && (primed.blobUrl || primed.url)) {
    const url = primed.url || serverAudioUrlFor(slot.item);
    return {
      videoId: primed.videoId || slotId,
      url,
      blobUrl: primed.blobUrl || "",
      queueIndex: slot.queueIndex,
      item: {
        ...slot.item,
        ...primed.item,
        url: url || primed.url,
        videoId: primed.videoId || slotId,
      },
    };
  }
  if (!slotId) return null;
  const url = serverAudioUrlFor(slot.item);
  if (!url) return null;
  return {
    videoId: slotId,
    url,
    blobUrl: "",
    queueIndex: slot.queueIndex,
    item: { ...slot.item, url },
  };
}

function handoffPrimedNext() {
  const primed = readyNextForHandoff();
  let src = primed?.blobUrl || primed?.url;
  if (!primed || !src) return false;

  state.playSession += 1;
  const playSession = state.playSession;
  state.prefetchGeneration += 1;
  const prefetchGen = state.prefetchGeneration;
  ignoreAutoPauseUntil = Date.now() + 1200;

  const previousBlob = activeBlobUrl;
  const leftover = primedNext?.blobUrl || "";
  primedNext = null;
  primeAbort?.abort();
  primeAbort = null;
  primeToken += 1;

  const sameTrackPlaying =
    Boolean(primed.videoId) &&
    primed.videoId === (videoIdFromAudioSrc() || state.playingId) &&
    Boolean(audio.src);
  if (sameTrackPlaying) {
    activeBlobUrl = previousBlob;
    if (primed.blobUrl && primed.blobUrl !== previousBlob) releaseBlobUrl(primed.blobUrl);
    src = audio.currentSrc || audio.src;
  } else {
    activeBlobUrl = primed.blobUrl || null;
    if (leftover && leftover !== src) releaseBlobUrl(leftover);
  }

  state.queueIndex = primed.queueIndex;
  state.current = primed.item;
  state.playingId = primed.videoId;
  state.pendingPlayVideoId = null;
  state.rowLoadingVideoId = null;
  state.rowLoadingKey = null;
  state.isLoading = false;
  state.isPlaying = true;
  state.autoAdvanceEnabled = true;
  holdMediaSessionPlaying = true;

  const sameFile = sameTrackPlaying;
  if (sameFile) {
    try {
      audio.currentTime = 0;
    } catch {
      /* a duração ainda não carregou */
    }
  } else {
    assignAudioSource(src);
  }
  audio.volume = Number(volume.value) / 100;
  const pending = audio.play();
  const dropBlob = !sameTrackPlaying && previousBlob && previousBlob !== src ? previousBlob : "";

  try {
    updatePlayerBar(primed.item);
    highlightPlayingRows();
    syncMediaSessionMetadata(primed.item);
    if (state.view === "nowplaying") renderNowPlaying();
    updateTransportControls();
  } catch {
    /* a troca de áudio já foi pedida */
  }
  if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";

  pending
    .then(() => {
      if (!isActivePlaybackSession(playSession)) return;
      holdMediaSessionPlaying = false;
      setPlayUi(true);
      setPlayerStatus("");
      consecutivePlayFailures = 0;
      saveLastListen();
      notePlaybackStarted(primed.item);
      updateStopQueueButton();
      if (dropBlob) releaseBlobUrl(dropBlob);
      void prefetchQueueAhead(prefetchGen);
      void primeUpcomingPlayback();
    })
    .catch((err) => {
      if (!isActivePlaybackSession(playSession)) return;
      if (!userPauseRequested && err?.name === "AbortError" && audio.paused) {
        holdMediaSessionPlaying = true;
        if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";
        audio.play().then(() => {
          if (!isActivePlaybackSession(playSession)) return;
          holdMediaSessionPlaying = false;
          setPlayUi(true);
          setPlayerStatus("");
          consecutivePlayFailures = 0;
          saveLastListen();
          notePlaybackStarted(primed.item);
          updateStopQueueButton();
          if (dropBlob) releaseBlobUrl(dropBlob);
          void prefetchQueueAhead(prefetchGen);
          void primeUpcomingPlayback();
        }).catch((retryErr) => {
          if (!isActivePlaybackSession(playSession)) return;
          holdMediaSessionPlaying = false;
          if (dropBlob) releaseBlobUrl(dropBlob);
          handleDownloadFailure(primed.item, retryErr);
        });
        return;
      }
      holdMediaSessionPlaying = false;
      if (dropBlob) releaseBlobUrl(dropBlob);
      if (primed.blobUrl && primed.blobUrl === activeBlobUrl) {
        activeBlobUrl = null;
        try {
          URL.revokeObjectURL(primed.blobUrl);
        } catch {
          /* já liberado */
        }
      }
      handleDownloadFailure(primed.item, err);
    });
  return true;
}

async function primeUpcomingPlayback() {
  if (!state.autoAdvanceEnabled || state.repeat === "one") {
    clearPrimedNext();
    return;
  }
  const slot = peekNextQueueSlot();
  if (!slot) {
    clearPrimedNext();
    return;
  }
  const slotId = slot.item.videoId || "";
  const blobInFlight = Boolean(primeAbort && !primeAbort.signal.aborted);
  if (
    primedNext &&
    slotId &&
    primedNext.videoId === slotId &&
    (primedNext.blobUrl || blobInFlight)
  ) {
    return;
  }

  const token = ++primeToken;
  primeAbort?.abort();
  primeAbort = null;
  if (primedNext?.blobUrl) releaseBlobUrl(primedNext.blobUrl);
  primedNext = null;

  let item = slot.item;
  try {
    if (!item.videoId && item.deezerId) await ensureDeezerResolved(item, { quiet: true });
  } catch {
    return;
  }
  if (token !== primeToken) return;
  if (!item?.videoId) return;
  if (!hasCachedAudio(item.videoId) && !isAutoPrefetchAllowed(item)) return;

  let url = serverAudioUrlFor(item);
  if (!url) {
    try {
      const data = await scheduleDownload(item.videoId, item, DOWNLOAD_PRIORITY_PREFETCH);
      if (token !== primeToken) return;
      if (!isServerAudioUrl(data?.url)) return;
      mergeHistoryEntry(data);
      url = data.url;
      item = { ...item, ...data, url };
    } catch {
      return;
    }
  }
  if (token !== primeToken || !url) return;

  const still = peekNextQueueSlot();
  if (!still || still.item.videoId !== item.videoId) return;
  primedNext = {
    videoId: item.videoId,
    deezerId: item.deezerId,
    url,
    blobUrl: "",
    item: { ...still.item, ...item, url },
    queueIndex: still.queueIndex,
  };
  if (item.videoId === state.playingId && isServerAudioUrl(audio.currentSrc || audio.src)) return;

  const controller = new AbortController();
  primeAbort = controller;
  try {
    const res = await fetch(rutUrl(url), { signal: controller.signal, credentials: "same-origin" });
    if (token !== primeToken || !res.ok) return;
    const announced = Number(res.headers.get("content-length") || 0);
    if (announced > 24 * 1024 * 1024) {
      controller.abort();
      primeAbort = null;
      return;
    }
    const blob = await res.blob();
    if (token !== primeToken || !blob.size) return;
    const blobUrl = URL.createObjectURL(blob);
    if (token !== primeToken || !primedNext || primedNext.videoId !== item.videoId) {
      URL.revokeObjectURL(blobUrl);
      return;
    }
    primedNext.blobUrl = blobUrl;
  } catch {
    if (primeAbort === controller) primeAbort = null;
  }
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function parseApiErrorDetail(data, fallback = "") {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || d).join(", ") || fallback;
  }
  return fallback;
}

function apiErrorFromResponse(res, data) {
  return friendlyApiError(parseApiErrorDetail(data, res.statusText), res.status);
}

function providerErrorHidden(message) {
  const m = String(message || "").toLowerCase();
  return (
    m.includes("youtube") ||
    m.includes("googleapis") ||
    m.includes("google") ||
    m.includes("quota exceeded") ||
    m.includes("quotaexceeded") ||
    m.includes("project_number") ||
    m.includes("yt-dlp")
  );
}

function friendlyApiError(message, status) {
  const text = String(message || "").trim();
  const m = text.toLowerCase();
  if (
    status === 429 ||
    m.includes("limite diário") ||
    m.includes("cota diária") ||
    providerErrorHidden(text)
  ) {
    if (text.includes("Limite diário") || text.includes("suas ") || text.includes("buscas do dia")) {
      return text;
    }
    return "Limite diário de buscas atingido. Use Recentes ou Biblioteca, ou tente de novo amanhã.";
  }
  if (providerErrorHidden(text)) {
    return "Busca temporariamente indisponível. Tente mais tarde.";
  }
  return text;
}

function friendlyPlaybackError(message) {
  const m = String(message || "").toLowerCase();
  if (!m) return "Não foi possível carregar esta faixa";
  if (m.includes("download") || m.includes("baix")) return "Não foi possível carregar esta faixa";
  if (m.includes("limite diário") || m.includes("quota exceeded") || providerErrorHidden(message)) {
    return friendlyApiError(message, 429);
  }
  if (m.includes("503")) {
    return "Serviço temporariamente indisponível";
  }
  return message;
}

async function postDownload(videoId, item, signal, priority = 0) {
  const payload = item ? itemPayload(item) : {};
  if (priority > 0) payload.downloadPriority = priority;
  const res = await fetch(`/api/download/${videoId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  const data = await res.json();
  if (!res.ok) {
    const detail = data.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg || d).join(", ")
          : res.statusText;
    noteDownloadRejected(videoId, msg);
    throw new Error(friendlyPlaybackError(msg) || "Não foi possível carregar a faixa");
  }
  return data;
}

async function ensureDownload(videoId, { onAttempt, item, priority = 0, playSession } = {}) {
  const hist = state.history.get(videoId);
  if (isServerAudioUrl(hist?.url)) return { ...hist, alreadyExisted: true };

  onAttempt?.(1, DOWNLOAD_MAX_ATTEMPTS);
  if (playSession == null || shouldDrivePlaybackUi(videoId, playSession)) {
    setPlayerStatus("Carregando…");
  }

  try {
    const data = await scheduleDownload(videoId, item, priority);
    if (playSession != null && !isActivePlaybackSession(playSession)) {
      return data;
    }
    await refreshHistory();
    if (playSession == null || shouldDrivePlaybackUi(videoId, playSession)) {
      setPlayerStatus("");
    }
    return data;
  } catch (err) {
    if (playSession == null || shouldDrivePlaybackUi(videoId, playSession)) {
      setPlayerStatus("");
    }
    throw err;
  }
}

function handleDownloadFailure(item, err) {
  consecutivePlayFailures += 1;
  const title = item?.title ? `${item.title}: ` : "";
  const reason = friendlyPlaybackError(err?.message);
  if (err?.name === "AbortError" || err?.name === "NotAllowedError") {
    consecutivePlayFailures = 0;
    if (err?.name === "NotAllowedError") {
      holdMediaSessionPlaying = false;
      setPlayUi(false);
      setPlayerStatus("Toque play para ouvir");
    }
    return;
  }
  if (!state.autoAdvanceEnabled) {
    consecutivePlayFailures = 0;
    setPlayerStatus(`${title}${reason || "Não foi possível carregar"}`);
    return;
  }
  if (consecutivePlayFailures >= MAX_CONSECUTIVE_PLAY_FAILURES) {
    consecutivePlayFailures = 0;
    setPlayerStatus(`${title}${reason}. Várias faixas falharam — tente mais tarde.`);
    return;
  }
  setPlayerStatus(`${title}${reason} — pulando…`);
  if (!advancePlayback(1)) {
    consecutivePlayFailures = 0;
    setPlayerStatus("Escolha outra faixa para continuar");
  }
}

async function toggleLibrary(item) {
  if (!item?.videoId) return;
  const id = item.videoId;
  if (isInLibrary(id)) {
    const res = await fetch(`/api/library/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(apiErrorFromResponse(res, data));
    state.library.delete(id);
    updateLibraryButtons();
    if (state.view === "home") await refreshHome();
    return false;
  }

  setPlayerStatus("Salvando na biblioteca…");
  const res = await fetch(`/api/library/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(itemPayload(item)),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(apiErrorFromResponse(res, data));
  await refreshLibrary();
  await refreshHistory();
  updateLibraryButtons();
  setPlayerStatus("Na biblioteca ✓");
  setTimeout(() => setPlayerStatus(""), 2000);
  return true;
}

function markTrackLoading(item) {
  const key = trackLoadKey(item);
  state.rowLoadingKey = key || null;
  state.rowLoadingVideoId = item?.videoId || key || null;
  const audibleId = videoIdFromAudioSrc();
  const otherPlaying = Boolean(audibleId && audibleId !== item?.videoId && !audio.paused);
  if (otherPlaying) updateTrackRowLoadingStates();
  else {
    setPlayLoading(true, 0.12);
    setPlayerStatus("Carregando…");
  }
}

function clearTrackLoading(item) {
  const key = trackLoadKey(item);
  if (
    !item ||
    state.rowLoadingVideoId === item.videoId ||
    (key && state.rowLoadingKey === key)
  ) {
    state.rowLoadingVideoId = null;
    state.rowLoadingKey = null;
  }
  setPlayLoading(false);
}

async function playItem(item, { setQueue = true, skipViewChange = false } = {}) {
  if (!item) return;
  const loadKey = trackLoadKey(item);
  if (loadKey && state.rowLoadingKey === loadKey) return;
  const previousBlob = activeBlobUrl;
  let adoptedBlob = "";
  if (primedNext?.blobUrl && item.videoId && primedNext.videoId === item.videoId) {
    adoptedBlob = primedNext.blobUrl;
    activeBlobUrl = adoptedBlob;
  }
  clearPrimedNext();

  state.autoAdvanceEnabled = true;
  state.playSession += 1;
  const playSession = state.playSession;
  markTrackLoading(item);

  if (!item.videoId && item.deezerId) {
    try {
      await ensureDeezerResolved(item);
    } catch (err) {
      if (!isActivePlaybackSession(playSession)) return;
      clearTrackLoading(item);
      handleDownloadFailure(item, err);
      return;
    }
    if (!isActivePlaybackSession(playSession)) return;
    if (item.videoId) state.rowLoadingVideoId = item.videoId;
    updateTrackRowLoadingStates();
  }
  if (!item?.videoId) {
    if (isActivePlaybackSession(playSession)) clearTrackLoading(item);
    return;
  }

  if (state.pendingResumeVideoId && state.pendingResumeVideoId !== item.videoId) {
    state.pendingResumeTime = 0;
    state.pendingResumeVideoId = null;
  }

  alignQueueIndexToVideoId(item.videoId);
  updateStopQueueButton();
  const downloadPriority = DOWNLOAD_PRIORITY_PLAY_BASE + playSession;

  if (shouldHideTrackFromLists(item)) {
    state.catalogHiddenVideoIds.add(item.videoId);
    purgeTrackFromDiscoverableLists(item.videoId);
    if (shouldDrivePlaybackUi(item.videoId, playSession)) {
      const mb = state.maxDownloadFileMb;
      handleDownloadFailure(
        item,
        new Error(
          mb > 0
            ? `Faixa muito pesada (limite ${mb} MB). Não será baixada.`
            : "Faixa bloqueada para download no servidor."
        )
      );
    }
    if (isActivePlaybackSession(playSession)) clearTrackLoading(item);
    return;
  }

  if (!hasCachedAudio(item.videoId) && !isAutoPrefetchAllowed(item)) {
    state.catalogHiddenVideoIds.add(item.videoId);
    purgeTrackFromDiscoverableLists(item.videoId);
    if (shouldDrivePlaybackUi(item.videoId, playSession)) {
      handleDownloadFailure(
        item,
        new Error("Faixas com mais de 20 minutos não podem ser baixadas.")
      );
    }
    if (isActivePlaybackSession(playSession)) clearTrackLoading(item);
    return;
  }

  state.prefetchGeneration += 1;
  const prefetchGen = state.prefetchGeneration;

  if (setQueue) {
    if (state.queue.length) {
      const idx = state.queue.findIndex((x) => x.videoId === item.videoId);
      if (idx >= 0) {
        state.queueIndex = idx;
        rebuildPlayOrder();
      }
    } else {
      setPlaybackQueue([item], item.videoId, "single");
    }
  }

  const stayOnQueue = shouldStayOnNowPlayingQueue();
  const openNowPlayingView = !skipViewChange && !stayOnQueue;
  if (!openNowPlayingView && state.view === "nowplaying") {
    renderNowPlaying();
  }

  state.pendingPlayVideoId = item.videoId;
  state.rowLoadingVideoId = item.videoId;
  const audibleId = videoIdFromAudioSrc();
  const keepMainPlayerWhileOtherPlays = Boolean(
    audio.src &&
      !audio.paused &&
      (audibleId ? audibleId !== item.videoId : true)
  );
  if (!audibleId || audibleId === item.videoId) {
    state.playingId = item.videoId;
    state.current = item;
    updatePlayerBar(item);
  } else {
    syncPlayingIdFromAudio();
  }
  highlightPlayingRows();
  void ensureSearchVisibleForPlayingItem(item.videoId);
  void ensureVideoIdsHydrated([item.videoId]);

  if (keepMainPlayerWhileOtherPlays) {
    updateTrackRowLoadingProgress(item.videoId, 0.12);
  } else {
    setPlayLoading(true, 0.12);
  }
  let playOk = false;
  let downloadFailed = false;
  let downloadError = null;

  try {
    const data = await ensureDownload(item.videoId, {
      item,
      playSession,
      priority: downloadPriority,
      onAttempt: (attempt, max) => {
        if (!isActivePlaybackSession(playSession)) return;
        const frac = attempt / max;
        if (keepMainPlayerWhileOtherPlays) {
          updateTrackRowLoadingProgress(item.videoId, frac);
        } else if (shouldDrivePlaybackUi(item.videoId, playSession)) {
          setPlayLoading(true, frac);
        }
      },
    });
    if (!isActivePlaybackSession(playSession)) return;
    if (!isServerAudioUrl(data?.url)) {
      throw new Error("Não foi possível carregar esta faixa");
    }

    const merged = { ...item, ...data };
    state.current = merged;
    state.playingId = item.videoId;
    state.pendingPlayVideoId = null;
    state.rowLoadingVideoId = null;
    updatePlayerBar(merged);

    const resumeAt =
      state.pendingResumeVideoId === item.videoId && state.pendingResumeTime > 3
        ? state.pendingResumeTime
        : 0;
    state.pendingResumeTime = 0;
    state.pendingResumeVideoId = null;
    const dropBlob = previousBlob && previousBlob !== adoptedBlob ? previousBlob : "";
    if (!adoptedBlob) activeBlobUrl = null;
    userPauseRequested = false;
    ignoreAutoPauseUntil = Date.now() + 1200;
    holdMediaSessionPlaying = true;
    assignAudioSource(adoptedBlob || data.url);
    if (dropBlob) releaseBlobUrl(dropBlob);
    if (resumeAt) {
      const seekWhenReady = () => {
        const d = audio.duration;
        if (!Number.isFinite(d) || resumeAt >= d - 2) return;
        audio.currentTime = resumeAt;
        seek.value = String(Math.round((resumeAt / d) * 1000));
        syncSeekProgressVisual();
        timeCurrent.textContent = formatSeconds(resumeAt);
      };
      if (audio.readyState >= 1) seekWhenReady();
      else audio.addEventListener("loadedmetadata", seekWhenReady, { once: true });
    }
    audio.volume = Number(volume.value) / 100;

    try {
      await audio.play();
    } catch (err) {
      if (userPauseRequested || err?.name !== "AbortError" || !audio.paused) throw err;
      holdMediaSessionPlaying = true;
      if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";
      await audio.play();
    }
    alignQueueIndexToVideoId(item.videoId);
    setPlayUi(true);
    setPlayerStatus("");
    playOk = true;
    notePlaybackStarted(merged);
    consecutivePlayFailures = 0;
    saveLastListen();
    if (openNowPlayingView) {
      openNowPlaying({ applySearchContext: true });
    } else if (state.view === "nowplaying") {
      renderNowPlaying();
    }
  } catch (err) {
    if (!isActivePlaybackSession(playSession)) {
      state.pendingPlayVideoId = null;
      if (state.rowLoadingKey === trackLoadKey(item)) {
        state.rowLoadingVideoId = null;
        state.rowLoadingKey = null;
      }
      syncPlayingIdFromAudio();
      updateTrackRowLoadingStates();
      return;
    }
    downloadFailed = true;
    downloadError = err;
    state.pendingPlayVideoId = null;
    state.rowLoadingVideoId = null;
    state.rowLoadingKey = null;
    syncPlayingIdFromAudio();
    setPlayUi(audio.paused ? false : state.isPlaying);
  } finally {
    if (isActivePlaybackSession(playSession)) {
      if (state.rowLoadingVideoId === item.videoId || state.rowLoadingKey === trackLoadKey(item)) {
        state.rowLoadingVideoId = null;
        state.rowLoadingKey = null;
      }
      if (keepMainPlayerWhileOtherPlays && !shouldDrivePlaybackUi(item.videoId, playSession)) {
        updateTrackRowLoadingStates();
      } else {
        setPlayLoading(false);
      }
      updateTransportControls();
    }
    if (playOk) {
      void prefetchQueueAhead(prefetchGen);
      void primeUpcomingPlayback();
    }
  }

  if (
    downloadFailed &&
    isActivePlaybackSession(playSession) &&
    state.playingId === item.videoId
  ) {
    handleDownloadFailure(item, downloadError);
  }
}

function togglePlayPause() {
  if (!audio.src) return;
  if (audio.paused) {
    userPauseRequested = false;
    ignoreAutoPauseUntil = 0;
    audio.play().then(() => setPlayUi(true)).catch(() => {});
  } else {
    userPauseRequested = true;
    ignoreAutoPauseUntil = 0;
    clearTimeout(trackEndTimer);
    audio.pause();
    setPlayUi(false);
  }
}

playerSourceBtn?.addEventListener("click", () => {
  if (!audio.src && state.current?.videoId) {
    playItem(state.current, { setQueue: false });
    return;
  }
  void goToPlaybackSource();
});

playerArtistBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  if (!artistCreditSearchEnabled()) return;
  void runCreditSearch({
    label: playerArtistBtn.textContent,
    query: playerArtistBtn.dataset.searchQuery || playerArtistBtn.textContent,
    kind: playerArtistBtn.dataset.creditKind || "",
    channelId: playerArtistBtn.dataset.channelId || "",
  });
});

npMinimizeBtn?.addEventListener("click", () => {
  closeNowPlaying();
});

npScrollToPlayingBtn?.addEventListener("click", () => {
  scrollPlayingRowIntoView();
});

npHeroArtist?.addEventListener("click", (e) => {
  e.stopPropagation();
  if (!artistCreditSearchEnabled()) return;
  void runCreditSearch({
    label: npHeroArtist.textContent,
    query: npHeroArtist.dataset.searchQuery || npHeroArtist.textContent,
    kind: npHeroArtist.dataset.creditKind || "",
    channelId: npHeroArtist.dataset.channelId || "",
  });
});

btnPlay.addEventListener("click", () => {
  if (!audio.src && state.current) {
    playItem(state.current, { setQueue: false });
    return;
  }
  togglePlayPause();
});

btnLibrary.addEventListener("click", async () => {
  if (!state.current) return;
  try {
    await toggleLibrary(state.current);
  } catch (err) {
    setPlayerStatus(err.message || "Erro");
  }
});

audio.addEventListener("play", () => {
  if (Date.now() >= ignoreAutoPauseUntil) holdMediaSessionPlaying = false;
  setPlayUi(true);
});
audio.addEventListener("pause", () => {
  if (userPauseRequested) {
    userPauseRequested = false;
    clearTimeout(trackEndTimer);
    holdMediaSessionPlaying = false;
    setPlayUi(false);
    return;
  }
  if (Date.now() < ignoreAutoPauseUntil || holdMediaSessionPlaying) {
    holdMediaSessionPlaying = true;
    if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";
    return;
  }
  if (state.autoAdvanceEnabled && (audio.ended || heardNearEnd())) {
    holdMediaSessionPlaying = true;
    if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";
    clearTimeout(trackEndTimer);
    const token = audioSrcToken;
    trackEndTimer = setTimeout(() => {
      if (token !== audioSrcToken || userPauseRequested) return;
      finishTrackIfEnded();
    }, 450);
    return;
  }
  setPlayUi(false);
});
function syncSeekProgressVisual() {
  if (!seekFillBar) return;
  const max = Number(seek.max) || 1000;
  const pct = Math.max(0, Math.min(100, (Number(seek.value) / max) * 100));
  seekFillBar.style.width = `${pct}%`;
}

audio.addEventListener("timeupdate", () => {
  if (state.seeking) return;
  const d = audio.duration;
  const t = audio.currentTime;
  if (Number.isFinite(t) && t > audioHeardSeconds) audioHeardSeconds = t;
  if (
    holdMediaSessionPlaying &&
    Date.now() >= ignoreAutoPauseUntil &&
    Number.isFinite(t) &&
    t > 1 &&
    !audio.paused
  ) {
    holdMediaSessionPlaying = false;
  }
  if (
    trackEndConsumedToken === audioSrcToken &&
    Number.isFinite(t) &&
    t > 1 &&
    !heardNearEnd()
  ) {
    trackEndConsumedToken = -1;
  }
  if (Number.isFinite(d) && d > 0) {
    seek.value = String(Math.round((t / d) * 1000));
    syncSeekProgressVisual();
    timeCurrent.textContent = formatSeconds(t);
    timeTotal.textContent = formatSeconds(d);
    if (!audio.paused) scheduleSaveLastListen();
  }
  syncMediaSessionPosition();
});
audio.addEventListener("loadedmetadata", () => {
  timeTotal.textContent = formatSeconds(audio.duration);
  if (!state.seeking) {
    const resumeId = videoIdFromAudioSrc();
    if (
      resumeId &&
      state.pendingResumeVideoId === resumeId &&
      state.pendingResumeTime > 3 &&
      Number.isFinite(audio.duration) &&
      state.pendingResumeTime < audio.duration - 2
    ) {
      const resumeAt = state.pendingResumeTime;
      audio.currentTime = resumeAt;
      seek.value = String(Math.round((resumeAt / audio.duration) * 1000));
      timeCurrent.textContent = formatSeconds(resumeAt);
      state.pendingResumeTime = 0;
      state.pendingResumeVideoId = null;
    } else {
      seek.value = "0";
    }
    syncSeekProgressVisual();
  }
});
audio.addEventListener("pause", () => {
  saveLastListen();
});
window.addEventListener("pagehide", () => {
  saveLastListen();
  persistUserVolume();
});
let audioSrcToken = 0;
let audioSrcReadyToken = 0;

function heardNearEnd() {
  const heard = Math.max(Number(audio.currentTime) || 0, audioHeardSeconds || 0);
  if (!Number.isFinite(heard) || heard < 1) return false;
  const dur = audio.duration;
  if (!Number.isFinite(dur) || dur <= 0) return heard >= 12;
  const slack = Math.max(6, dur * 0.12);
  return heard >= dur - slack;
}

function assignAudioSource(url) {
  audioHeardSeconds = 0;
  audioSrcToken += 1;
  const token = audioSrcToken;
  audioSrcReadyToken = 0;
  const next = rutUrl(url);
  let same = false;
  try {
    const abs = new URL(next, window.location.href).href;
    const cur = audio.currentSrc || audio.src || "";
    same = Boolean(cur) && cur.split("#")[0] === abs.split("#")[0];
  } catch {
    same = false;
  }
  const markReady = () => {
    if (token !== audioSrcToken) return;
    audioSrcReadyToken = token;
  };
  if (same) {
    markReady();
    try {
      audio.currentTime = 0;
    } catch {
      /* a duração ainda não carregou */
    }
    return token;
  }
  audio.addEventListener("loadedmetadata", markReady, { once: true });
  audio.src = next;
  return token;
}

function isGenuineTrackEnd() {
  const heard = Math.max(Number(audio.currentTime) || 0, audioHeardSeconds || 0);
  if (!Number.isFinite(heard) || heard < 1) return false;
  if (audioSrcReadyToken !== audioSrcToken && heard < 8) return false;
  if (heardNearEnd()) return true;
  return Boolean(audio.ended && heard >= 8);
}

function finishTrackIfEnded() {
  if (userPauseRequested || trackEndConsumedToken === audioSrcToken) return;
  if (!isGenuineTrackEnd()) return;
  trackEndConsumedToken = audioSrcToken;
  clearTimeout(trackEndTimer);
  const endedId = videoIdFromAudioSrc() || state.playingId || state.current?.videoId;
  if (endedId) alignQueueIndexToVideoId(endedId);
  if (state.repeat === "one") {
    holdMediaSessionPlaying = true;
    ignoreAutoPauseUntil = Date.now() + 1200;
    audioHeardSeconds = 0;
    try {
      audio.currentTime = 0;
    } catch {
      /* a duração ainda não carregou */
    }
    audio.play().then(() => setPlayUi(true)).catch(() => {
      holdMediaSessionPlaying = false;
      setPlayUi(false);
    });
    return;
  }
  if (!state.autoAdvanceEnabled) {
    holdMediaSessionPlaying = false;
    setPlayUi(false);
    updateTransportControls();
    updateStopQueueButton();
    return;
  }
  // play() no mesmo instante do ended. Qualquer espera antes disso faz o
  // celular bloqueado recusar a faixa seguinte.
  if (handoffPrimedNext()) return;
  if (!advancePlayback(1)) {
    holdMediaSessionPlaying = false;
    setPlayUi(false);
    updateTransportControls();
  }
}

audio.addEventListener("ended", () => {
  // Trocar o src dispara "ended" de novo no começo da faixa nova.
  // Sem o tempo ouvido, o player parava ou pulava mais uma.
  finishTrackIfEnded();
});

btnPrev.addEventListener("click", () => {
  state.autoAdvanceEnabled = true;
  updateStopQueueButton();
  advancePlayback(-1);
});

btnNext.addEventListener("click", () => {
  state.autoAdvanceEnabled = true;
  updateStopQueueButton();
  advancePlayback(1);
});

btnStopQueue?.addEventListener("click", () => {
  stopQueueActivity();
});

btnShuffle.addEventListener("click", () => toggleShuffleMode());

btnRepeat.addEventListener("click", () => cycleRepeatMode());

seek.addEventListener("input", () => {
  state.seeking = true;
  syncSeekProgressVisual();
  const d = audio.duration;
  if (Number.isFinite(d)) {
    timeCurrent.textContent = formatSeconds((Number(seek.value) / 1000) * d);
  }
});
seek.addEventListener("change", () => {
  const d = audio.duration;
  if (Number.isFinite(d)) {
    audio.currentTime = (Number(seek.value) / 1000) * d;
  }
  state.seeking = false;
  syncSeekProgressVisual();
});

function syncVolumeVisual() {
  if (!volumeFillBar || !volume) return;
  const max = Number(volume.max) || 100;
  const pct = Math.max(0, Math.min(100, (Number(volume.value) / max) * 100));
  volumeFillBar.style.width = `${pct}%`;
}

volume.addEventListener("input", () => {
  audio.volume = Number(volume.value) / 100;
  syncVolumeVisual();
  persistUserVolume();
});
loadUserVolume();

function buildTrackRow(item, index, { mode = "search" } = {}) {
  const li = document.createElement("li");
  li.className = "track-row";
  li.dataset.videoId = item.videoId || "";

  const inLib = isInLibrary(item.videoId);
  const needsHydrate = mode === "search" && catalogItemNeedsHydrate(item);
  const dur = item.duration ? formatDurationIso(item.duration) : "—";

  if (item.deezerId) li.dataset.deezerId = String(item.deezerId);
  const credit = trackCreditLine(item);
  const catalogAlbum = [item.album, item.genre].filter(Boolean).join(" · ");
  const albumCol =
    mode === "search" ? descSnippet(item.description) : catalogAlbum || item.channelTitle || "—";
  const artistHtml = artistCreditInnerHtml(credit);
  const serverBadge = isTrackOnServer(item) ? onServerBadgeHtml() : "";
  li.innerHTML = `
    <div class="col-title">
      <div class="col-leading">
        <button type="button" class="col-play" aria-label="Tocar">
          ${PLAY_SVG}${PAUSE_SVG}
        </button>
      </div>
      <div class="col-cover">
        <img src="${escapeHtml(item.thumbnailUrl || "")}" alt="" loading="lazy" width="40" height="40" />
        ${serverBadge}
        <span class="col-play-spinner spinner spinner-green hidden" aria-hidden="true"></span>
      </div>
      <div class="col-title-text">
        <span class="track-name">${escapeHtml(item.title || item.filename || "")}</span>
        ${artistHtml}
      </div>
    </div>
    <span class="col-album">${escapeHtml(albumCol)}</span>
    <span class="col-duration${needsHydrate ? " hydrate-pending" : ""}">${escapeHtml(dur)}</span>
    <div class="row-actions">
      <button type="button" class="icon-btn btn-add-lib ${inLib ? "saved" : ""}" data-video-id="${escapeHtml(item.videoId || "")}" title="${inLib ? "Remover da biblioteca" : "Adicionar à biblioteca"}">${inLib ? "✓" : "+"}</button>
    </div>
  `;

  const play = () => playFromList(item, mode);
  const colPlayBtn = li.querySelector(".col-play");
  colPlayBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    const uiCurrentId = getUiCurrentVideoId();
    if (item.videoId === uiCurrentId && audio.src && !state.isLoading) {
      togglePlayPause();
      return;
    }
    if (state.rowLoadingKey && state.rowLoadingKey === trackLoadKey(item)) return;
    play();
  });
  li.addEventListener("click", (e) => {
    if (e.target.closest(".row-actions")) return;
    if (e.target.closest(".track-artist-btn")) return;
    if (e.target.closest("a[href]")) return;
    if (state.rowLoadingKey && state.rowLoadingKey === trackLoadKey(item)) return;
    play();
  });

  bindTrackArtistCreditButton(li);
  if (item.catalogSource === "deezer" && item.artistId) {
    li.querySelector(".track-artist-btn")?.addEventListener(
      "click",
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (state.view === "search") void openSearchCatalogLevel("artist", item.artistId, item.artist);
    else void openDeezerLevel("artist", item.artistId, item.artist);
      },
      true
    );
  }

  li.querySelector(".btn-add-lib")?.addEventListener("click", async (e) => {
    e.stopPropagation();
    try {
      if (!item.videoId && item.deezerId) await ensureDeezerResolved(item);
      await toggleLibrary(item);
    } catch (err) {
      setStatus(err.message || "Erro ao salvar", { error: true });
    }
  });

  return li;
}

function mergeCatalogItem(updated) {
  if (!updated?.videoId) return;
  const idx = state.searchCatalog.findIndex((i) => i.videoId === updated.videoId);
  let merged = updated;
  if (idx >= 0) {
    merged = { ...state.searchCatalog[idx], ...updated };
    state.searchCatalog[idx] = merged;
  }
  const qIdx = state.queue.findIndex((i) => i.videoId === updated.videoId);
  if (qIdx >= 0) {
    state.queue[qIdx] = { ...state.queue[qIdx], ...updated };
  }
  if (updated.duration) {
    state.searchHydrated.add(updated.videoId);
  }
  if (shouldHideTrackFromLists(merged)) {
    purgeTrackFromDiscoverableLists(updated.videoId);
  }
}

function mergeLocalCatalogHints(item) {
  if (!item?.videoId) return item;
  if (item.duration) state.searchHydrated.add(item.videoId);
  const hist = state.history.get(item.videoId);
  if (!hist) return item;
  const patch = {};
  for (const key of [
    "duration",
    "artist",
    "channelId",
    "channelTitle",
    "description",
    "thumbnailUrl",
  ]) {
    if (!item[key] && hist[key]) patch[key] = hist[key];
  }
  if (!Object.keys(patch).length) return item;
  const merged = { ...item, ...patch };
  if (merged.duration) state.searchHydrated.add(merged.videoId);
  return merged;
}

function catalogItemNeedsHydrate(item) {
  if (!item?.videoId) return false;
  if (state.searchHydrated.has(item.videoId)) return false;
  if (item.duration) {
    state.searchHydrated.add(item.videoId);
    return false;
  }
  return true;
}

function patchSearchTrackRow(videoId) {
  if (state.view !== "search") return;
  const item = state.searchCatalog.find((i) => i.videoId === videoId);
  if (!item) return;
  const row = resultsEl.querySelector(`.track-row[data-video-id="${CSS.escape(videoId)}"]`);
  if (!row) return;

  const durEl = row.querySelector(".col-duration");
  if (durEl) {
    durEl.textContent = item.duration ? formatDurationIso(item.duration) : "—";
    durEl.classList.remove("hydrate-pending");
  }
  const albumEl = row.querySelector(".col-album");
  if (albumEl && item.description) {
    albumEl.textContent = descSnippet(item.description);
  }

  const credit = trackCreditLine(item);
  const artistBtn = row.querySelector(".track-artist-btn");
  const artistSpan = row.querySelector(".track-artist");
  if (credit.label && artistBtn) {
    artistBtn.textContent = creditDisplayLabel(credit.label);
    artistBtn.dataset.searchQuery = credit.query;
    artistBtn.dataset.creditKind = credit.kind || "";
    artistBtn.dataset.channelId = credit.channelId || "";
    artistBtn.title = creditFullTitle(credit);
  } else if (credit.label && artistSpan) {
    if (artistCreditSearchEnabled()) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "track-artist-btn";
      btn.dataset.searchQuery = credit.query;
      btn.dataset.creditKind = credit.kind || "";
      btn.dataset.channelId = credit.channelId || "";
      btn.title = creditFullTitle(credit);
      btn.textContent = creditDisplayLabel(credit.label);
      artistSpan.replaceWith(btn);
      bindTrackArtistCreditButton(row);
    } else {
      artistSpan.textContent = creditDisplayLabel(credit.label);
      artistSpan.title = creditFullTitle(credit);
      artistSpan.classList.add("track-artist-static");
    }
  }
}

let lazyHydrateObserver = null;
let lazyHydrateTimer = null;
const lazyHydratePending = new Set();

function lazyHydrateScrollRoot() {
  return document.querySelector(".content");
}

function scheduleLazyHydrateFlush() {
  if (lazyHydrateTimer) return;
  lazyHydrateTimer = setTimeout(() => {
    lazyHydrateTimer = null;
    void flushLazyHydrate();
  }, LAZY_HYDRATE_DEBOUNCE_MS);
}

function collectVisibleHydrateIds() {
  const root = lazyHydrateScrollRoot();
  if (!root) return;
  const rootRect = root.getBoundingClientRect();
  const margin = LAZY_HYDRATE_ROOT_MARGIN_PX;
  resultsEl.querySelectorAll(".track-row[data-video-id]").forEach((row) => {
    const rect = row.getBoundingClientRect();
    if (rect.bottom < rootRect.top - margin || rect.top > rootRect.bottom + margin) return;
    const id = row.dataset.videoId;
    const item = state.searchCatalog.find((i) => i.videoId === id);
    if (item && catalogItemNeedsHydrate(item)) lazyHydratePending.add(id);
  });
}

function ensureLazyHydrateObserver() {
  if (lazyHydrateObserver) return;
  const root = lazyHydrateScrollRoot();
  if (!root) return;
  lazyHydrateObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const id = entry.target.dataset.videoId;
        if (!id) continue;
        const item = state.searchCatalog.find((i) => i.videoId === id);
        if (item && catalogItemNeedsHydrate(item)) lazyHydratePending.add(id);
      }
      scheduleLazyHydrateFlush();
    },
    {
      root,
      rootMargin: `${LAZY_HYDRATE_ROOT_MARGIN_PX}px 0px`,
      threshold: 0,
    }
  );
}

function bindLazyHydrateRows() {
  if (state.view !== "search" || !state.searchCatalog.length) return;
  ensureLazyHydrateObserver();
  if (!lazyHydrateObserver) return;
  lazyHydrateObserver.disconnect();
  resultsEl.querySelectorAll(".track-row[data-video-id]").forEach((row) => {
    const id = row.dataset.videoId;
    const item = state.searchCatalog.find((i) => i.videoId === id);
    const durEl = row.querySelector(".col-duration");
    if (durEl && item && catalogItemNeedsHydrate(item)) {
      durEl.classList.add("hydrate-pending");
    }
    lazyHydrateObserver.observe(row);
  });
  collectVisibleHydrateIds();
  scheduleLazyHydrateFlush();
}

function resetLazyHydrate() {
  state.searchHydrateGen += 1;
  lazyHydratePending.clear();
  if (lazyHydrateTimer) {
    clearTimeout(lazyHydrateTimer);
    lazyHydrateTimer = null;
  }
  lazyHydrateObserver?.disconnect();
}

async function hydrateVideoIds(_ids) {
  return;
  const gen = state.searchHydrateGen;
  const need = [];
  for (const id of ids) {
    if (!id || state.searchHydrated.has(id)) continue;
    const item = state.searchCatalog.find((i) => i.videoId === id);
    if (!item || !catalogItemNeedsHydrate(item)) continue;
    need.push(id);
  }
  if (!need.length) return;

  const url = new URL(rutUrl("/api/videos"), window.location.origin);
  url.searchParams.set("ids", need.join(","));
  if (state.searchMixId) url.searchParams.set("mix_id", state.searchMixId);
  const res = await fetch(url);
  const data = await res.json();
  if (gen !== state.searchHydrateGen) return;
  if (!res.ok) throw new Error(apiErrorFromResponse(res, data));

  const returned = new Set();
  for (const item of data.items || []) {
    if (!item?.videoId) continue;
    returned.add(item.videoId);
    state.searchHydrated.add(item.videoId);
    mergeCatalogItem(item);
    const merged = state.searchCatalog.find((i) => i.videoId === item.videoId);
    if (merged && shouldHideTrackFromLists(merged)) {
      purgeTrackFromDiscoverableLists(item.videoId);
    } else {
      patchSearchTrackRow(item.videoId);
    }
  }
  for (const id of data.hiddenVideoIds || []) {
    if (!id) continue;
    state.searchHydrated.add(id);
    state.catalogHiddenVideoIds.add(id);
    purgeTrackFromDiscoverableLists(id);
  }
  for (const id of need) {
    if (!returned.has(id) && !(data.hiddenVideoIds || []).includes(id)) {
      state.searchHydrated.add(id);
    }
  }
  refreshQuota();
}

async function flushLazyHydrate() {
  if (!lazyHydratePending.size) return;
  const gen = state.searchHydrateGen;
  const ids = [...lazyHydratePending];
  lazyHydratePending.clear();
  for (let i = 0; i < ids.length; i += LAZY_HYDRATE_BATCH) {
    if (gen !== state.searchHydrateGen) return;
    try {
      await hydrateVideoIds(ids.slice(i, i + LAZY_HYDRATE_BATCH));
    } catch {
      /* metadados em segundo plano */
    }
  }
}

async function ensureVideoIdsHydrated(ids) {
  const need = (ids || []).filter((id) => {
    const item = state.searchCatalog.find((i) => i.videoId === id);
    return item && catalogItemNeedsHydrate(item);
  });
  if (!need.length) return;
  for (let i = 0; i < need.length; i += LAZY_HYDRATE_BATCH) {
    await hydrateVideoIds(need.slice(i, i + LAZY_HYDRATE_BATCH));
  }
}

/** Busca duração de todo o catálogo da busca (remove álbums longos sem precisar rolar). */
function hydrateSearchCatalogInBackground() {
  const ids = state.searchCatalog.map((i) => i.videoId).filter(Boolean);
  if (!ids.length) return;
  void (async () => {
    try {
      await ensureVideoIdsHydrated(ids);
      evictHiddenTracksFromCatalog();
      compactSearchCatalog();
    } catch {
      /* metadados em segundo plano */
    }
  })();
}

function syncSearchQueue() {
  const catalog = filterDiscoverableItems(state.searchCatalog.filter((i) => i.videoId));
  let cap =
    state.searchVisibleCount > 0
      ? Math.min(state.searchVisibleCount, catalog.length)
      : catalog.length;
  const playingId =
    state.playingId || state.current?.videoId || state.pendingPlayVideoId || null;
  if (playingId) {
    const playIdx = catalog.findIndex((i) => i.videoId === playingId);
    if (playIdx >= 0) cap = Math.max(cap, playIdx + 1);
  }
  state.queue = catalog.slice(0, cap);
  if (playingId) alignQueueIndexToVideoId(playingId);
  rebuildPlayOrder();
  updateTransportControls();
}

function updateSearchStatusLine() {
  const loaded = state.searchCatalog.length;
  const shown = state.searchVisibleCount;
  if (!loaded) return;
  const moreOnServer = Boolean(state.searchNextPageToken);
  let msg = `Mostrando ${shown} de ${loaded} resultado${loaded > 1 ? "s" : ""}`;
  if (moreOnServer) msg += " · mais resultados disponíveis";
  setStatus(msg);
}

function updateSearchShowMoreUi() {
  updateCatalogShowMoreUi();
}

function renderResults(items, { indexOffset = 0 } = {}) {
  resultsEl.innerHTML = "";
  if (!items.length) {
    resultsEl.innerHTML = "<li class=\"status-line\">Nenhum resultado.</li>";
    return;
  }
  items.forEach((item, i) =>
    resultsEl.appendChild(buildTrackRow(item, indexOffset + i, { mode: "search" }))
  );
  highlightPlayingRows();
  updateLibraryButtons();
  updateTrackRowLoadingStates();
}

function setSearchTrackHeadVisible(show) {
  document.getElementById("search-track-head")?.classList.toggle("hidden", !show);
}

function renderSearchRecents() {
  searchHeading.textContent = "Buscas recentes";
  clearSearchEntityCover();
  setStatus("");
  resultsEl.innerHTML = "";
  searchShowMore?.classList.add("hidden");
  searchTracksLabelEl?.closest(".catalog-list-heading")?.classList.add("hidden");
  searchSaveShortcut?.classList.add("hidden");
  setSearchTrackHeadVisible(false);
  if (!searchCatalogEl) return;
  searchCatalogEl.innerHTML = "";
  const recent = loadRecentSearches();
  if (!recent.length) {
    searchCatalogEl.innerHTML = '<p class="status-line">Nenhuma busca recente.</p>';
    return;
  }
  const section = appendShelfSection(searchCatalogEl, "Buscas recentes", "search-recent", () =>
    recent.map((entry) => createRecentSearchMixCard(entry))
  );
  section?.querySelector(".explore-class-title")?.remove();
}

function openSearchFromInput() {
  if (state.view === "search") return;
  pushNavigationReturn();
  clearSearchFilters();
  state.searchQuery = "";
  state.searchCatalog = [];
  state.searchVisibleCount = 0;
  state.searchNextPageToken = null;
  setView("search", { keepSearchFocus: true });
  renderSearchRecents();
}

function renderSearchVisible() {
  const catalog = filterDiscoverableItems(state.searchCatalog);
  const slice = catalog.slice(0, state.searchVisibleCount);
  renderResults(slice, { indexOffset: 0 });
  setSearchTrackHeadVisible(slice.length > 0);
  updateSearchShowMoreUi();
  updateSearchStatusLine();
  bindLazyHydrateRows();
}

function scrollPlayingRowIntoViewIfSearch() {
  if (state.view !== "search") return;
  scrollPlayingRowIntoView();
}

async function ensureSearchVisibleForPlayingItem(videoId) {
  if (state.queueSource !== "search" || !videoId || !state.searchCatalog.length) return;
  if (state.searchExpandInFlight || state.searchLoadingMore) return;

  const idx = state.searchCatalog.findIndex((i) => i.videoId === videoId);
  if (idx < 0) return;
  if (idx < state.searchVisibleCount) {
    scrollPlayingRowIntoViewIfSearch();
    return;
  }

  state.searchExpandInFlight = true;
  try {
    let target = state.searchVisibleCount || SEARCH_INITIAL_VISIBLE;
    while (target <= idx) target += SEARCH_SHOW_MORE_STEP;
    expandSearchVisibleCount(target);

    while (idx >= state.searchCatalog.length && state.searchNextPageToken) {
      try {
        await fetchNextSearchBatch();
      } catch {
        break;
      }
    }
    if (idx >= state.searchCatalog.length) return;

    target = state.searchVisibleCount;
    while (target <= idx) target += SEARCH_SHOW_MORE_STEP;
    expandSearchVisibleCount(target);
    void ensureVideoIdsHydrated([videoId]);
    scrollPlayingRowIntoViewIfSearch();
  } catch {
    /* expansão automática silenciosa */
  } finally {
    state.searchExpandInFlight = false;
  }
}

async function fetchNextSearchBatch() {
  return false;
  const beforeLen = state.searchCatalog.length;
  if (!state.searchQuery && !state.searchMixId && !state.searchChannelId) {
    return false;
  }
  if (mixHasMoreOnServerCatalog()) {
    await fetchMixCatalogBatch();
    if (state.searchCatalog.length > beforeLen) return true;
  }
  if (!state.searchNextPageToken) {
    await fetchMixCatalogBatch();
    return state.searchCatalog.length > beforeLen;
  }
  const url = buildSearchFetchUrl();
  url.searchParams.set("page_token", state.searchNextPageToken);

  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(apiErrorFromResponse(res, data));

  syncMixSearchMeta(data);

  const seenIds = new Set(state.searchCatalog.map((i) => i.videoId));
  const seenSongKeys = new Set(
    state.searchCatalog.map((i) => similarTrackDedupeKey(i)).filter(Boolean)
  );
  for (const item of data.items || []) {
    if (!item.videoId || seenIds.has(item.videoId)) continue;
    const merged = mergeLocalCatalogHints(item);
    if (shouldHideTrackFromLists(merged)) continue;
    const songKey = similarTrackDedupeKey(merged);
    if (songKey && seenSongKeys.has(songKey)) continue;
    state.searchCatalog.push(merged);
    seenIds.add(item.videoId);
    if (songKey) seenSongKeys.add(songKey);
  }
  state.searchNextPageToken = data.nextPageToken || null;
  if (state.searchMixId && Array.isArray(data.coverPreview) && data.coverPreview.length) {
    applyMixCoverPreview(state.searchMixId, data.coverPreview);
  }
  if (state.searchMixId && (data.items || []).length) {
    void submitMixCoversFromItems(state.searchMixId, data.items);
  }
  compactSearchCatalog();
  if (shouldBindSearchResultsToQueue()) syncSearchQueue();
  refreshQuota();
  hydrateSearchCatalogInBackground();
  return state.searchCatalog.length > beforeLen;
}

function expandSearchVisibleCount(target) {
  const prev = state.searchVisibleCount;
  const next = Math.min(Math.max(target, 0), state.searchCatalog.length);
  if (next <= prev) return prev;
  state.searchVisibleCount = next;
  if (shouldBindSearchResultsToQueue()) syncSearchQueue();
  if (state.view === "search") renderSearchVisible();
  else if (state.view === "nowplaying") renderNowPlaying();
  else updateCatalogShowMoreUi();
  updateSearchStatusLine();
  return next;
}

async function showMoreSearchResults() {
  if (state.searchLoadingMore) return;
  state.searchLoadingMore = true;
  updateSearchShowMoreUi();

  const prevVisible = state.searchVisibleCount;
  let target = prevVisible + (prevVisible === 0 ? SEARCH_INITIAL_VISIBLE : SEARCH_SHOW_MORE_STEP);

  try {
    // 1) Revela o que já está no catálogo (sem API) — funciona mesmo com cota esgotada.
    expandSearchVisibleCount(target);

    // 2) Só busca mais páginas se ainda precisar e houver token.
    if (target > state.searchCatalog.length) {
      try {
        if (state.view === "search") {
          setStatus("Carregando mais…", { loading: true });
        }
        let fetchGuard = 0;
        while (target > state.searchCatalog.length && fetchGuard < 40) {
          fetchGuard += 1;
          const added = await fetchNextSearchBatch();
          if (!added) break;
        }
        expandSearchVisibleCount(target);
      } catch (err) {
        if (state.searchVisibleCount > prevVisible) {
          const loaded = state.searchCatalog.length;
          const shown = state.searchVisibleCount;
          setStatus(
            `Mostrando ${shown} de ${loaded} · ${friendlyApiError(err.message, 429)}`,
            { error: true }
          );
        } else {
          throw err;
        }
      }
    }

    if (state.searchVisibleCount <= prevVisible) {
      updateSearchStatusLine();
    }
  } catch (err) {
    setStatus(friendlyApiError(err.message, 429) || "Erro ao carregar", { error: true });
  } finally {
    state.searchLoadingMore = false;
    if (shouldBindSearchResultsToQueue()) syncSearchQueue();
    if (state.view === "nowplaying") {
      renderNowPlaying();
      if (nowPlayingSub && state.searchCatalog.length) {
        const shown = state.queue.length;
        const loaded = state.searchCatalog.length;
        const origin = nowPlayingOriginLabel();
        const tail =
          shown < loaded || mixSearchHasMoreToLoad()
            ? ` · mostrando ${shown} de ${loaded}`
            : "";
        nowPlayingSub.textContent = origin
          ? `${shown} faixa${shown > 1 ? "s" : ""} · de ${origin}${tail}`
          : `${shown} faixa${shown > 1 ? "s" : ""} na fila${tail}`;
      }
    } else {
      updateCatalogShowMoreUi();
    }
    refreshQuota();
  }
}

async function beginSearchResults(q) {
  const term = (typeof q === "string" && q.trim()) || (state.searchQuery || "").trim();
  if (term) await showSearchCatalog(term);
  return;
  clearSearchCatalogChrome(false);
  if (typeof q === "string" && q.trim()) {
    state.searchQuery = q.trim();
    state.searchChannelId = null;
    state.searchChannelTitle = null;
  }
  state.searchCatalog = [];
  state.searchVisibleCount = 0;
  state.searchNextPageToken = null;
  state.searchMixCatalogTotal = 0;
  state.searchHydrated = new Set();
  state.catalogHiddenVideoIds = new Set();
  resetLazyHydrate();

  const url = buildSearchFetchUrl();

  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(apiErrorFromResponse(res, data));

  state.searchCatalog = filterDiscoverableItems(
    (data.items || []).map((item) => mergeLocalCatalogHints(item))
  );
  state.searchNextPageToken = data.nextPageToken || null;
  syncMixSearchMeta(data);
  if (state.searchMixId && state.searchCatalog.length) {
    void submitMixCoversFromItems(state.searchMixId, state.searchCatalog);
  } else if (state.searchMixId && Array.isArray(data.coverPreview) && data.coverPreview.length) {
    applyMixCoverPreview(state.searchMixId, data.coverPreview);
  }
  if (shouldBindSearchResultsToQueue()) {
    syncSearchQueue();
    state.queueIndex = -1;
  }

  if (!state.searchCatalog.length) {
    setStatus("Nenhum resultado.");
    renderResults([]);
    searchShowMore.classList.add("hidden");
    updateSearchSaveButton();
    return;
  }

  state.searchVisibleCount = Math.min(SEARCH_INITIAL_VISIBLE, state.searchCatalog.length);
  renderSearchVisible();
  updateSearchStatusLine();
  if (state.searchMixId) {
    void submitMixCoversFromItems(state.searchMixId, state.searchCatalog);
  }
  updateSearchSaveButton();
  hydrateSearchCatalogInBackground();
}

async function refreshHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    if (!res.ok) return;
    state.history = new Map(data.items.map((i) => [i.videoId, i]));
    renderHistory(data.items);
    updateLibraryButtons();
  } catch {
    /* silencioso */
  }
}

function renderHistory(items) {
  state.historyItems = items;
  historyEl.innerHTML = "";
  historyCountEl.textContent = items.length
    ? `${items.length} faixa${items.length > 1 ? "s" : ""} ouvida${items.length > 1 ? "s" : ""} recentemente`
    : "Nada por aqui ainda — busque algo para ouvir.";

  if (!items.length) return;
  items.forEach((item, i) => {
    historyEl.appendChild(
      buildTrackRow(
        { ...item, title: item.title || item.filename, url: item.url || item.url },
        i,
        { mode: "history" }
      )
    );
  });
  highlightPlayingRows();
}

async function refreshLibrary() {
  try {
    const libRes = await fetch("/api/library");
    const data = await libRes.json();
    if (!libRes.ok) {
      state.library = new Map();
      renderBiblioteca([]);
      updateLibraryButtons();
      return;
    }
    const items = Array.isArray(data.items) ? data.items : [];
    state.library = new Map(items.map((i) => [i.videoId, i]));
    renderBiblioteca(items);
    updateLibraryButtons();
  } catch {
    /* silencioso */
  }
}

function renderBiblioteca(items) {
  state.libraryItems = items;
  libraryEl.innerHTML = "";
  libraryCountEl.textContent = items.length
    ? `${items.length} faixa${items.length > 1 ? "s" : ""} salvas com +`
    : "Biblioteca vazia — clique em + numa música para salvar.";

  items.forEach((item, i) => {
    mergeFreeItemsIntoHistory([item]);
    libraryEl.appendChild(
      buildTrackRow(
        {
          ...item,
          onServer: item.onServer || isTrackOnServer(item),
          title: item.title || item.filename,
          url: item.url?.startsWith("/api/") ? item.url : item.url,
        },
        i,
        { mode: "library" }
      )
    );
  });
  highlightPlayingRows();
}

function renderServerLibrary(items, total) {
  state.serverLibraryItems = items;
  state.serverLibraryTotal = total;
  if (!serverLibraryEl || !homeServerTracks) return;
  mergeFreeItemsIntoHistory(items);
  serverLibraryEl.innerHTML = "";
  if (!items.length) {
    homeServerTracks.classList.add("hidden");
    return;
  }
  homeServerTracks.classList.remove("hidden");
  if (serverLibraryCountEl) {
    serverLibraryCountEl.textContent = `${total} faixa${total !== 1 ? "s" : ""} no servidor que você ainda não salvou`;
  }
  items.forEach((item, i) => {
    serverLibraryEl.appendChild(
      buildTrackRow(
        {
          ...item,
          onServer: true,
          title: item.title || item.filename,
          url: item.url,
        },
        i,
        { mode: "serverlibrary" }
      )
    );
  });
  highlightPlayingRows();
}

searchShowMore?.addEventListener("click", () => {
  void showMoreSearchResults();
});
npShowMore?.addEventListener("click", () => {
  void showMoreSearchResults();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  await runTextSearch(q);
});

function isAndroidDevice() {
  return /Android/i.test(navigator.userAgent);
}

function isPwaStandalone() {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    window.matchMedia("(display-mode: fullscreen)").matches ||
    navigator.standalone === true
  );
}

function bindPwaInstall() {
  const banner = document.getElementById("pwa-install-banner");
  const installBtn = document.getElementById("pwa-install-btn");
  const dismissBtn = document.getElementById("pwa-install-dismiss");
  const subEl = banner?.querySelector(".pwa-install-sub");
  if (!banner || !installBtn || !dismissBtn) return;

  let deferredPrompt = null;

  const hideBanner = () => banner.classList.add("hidden");
  const showBanner = () => banner.classList.remove("hidden");

  const shouldOfferInstall = () => isAndroidDevice() && !isPwaStandalone();

  const pwaInstallUrl = () => {
    const host = window.location.hostname || "192.168.0.5";
    return `https://${host}:8443${window.location.pathname}${window.location.search}`;
  };

  const isPublicHttpsSite = () => {
    const host = (window.location.hostname || "").toLowerCase();
    return host === "ruts.dev" || host.endsWith(".ruts.dev");
  };

  const isOnPwaInstallOrigin = () => {
    if (isPublicHttpsSite() && window.isSecureContext) return true;
    const port = String(window.location.port || "");
    if (port === "8443") return true;
    return /:8443(?:\/|$|\?|#)/.test(window.location.href);
  };

  const isSamePageUrl = (target) => {
    try {
      const here = new URL(window.location.href);
      const next = new URL(target, window.location.href);
      return (
        here.protocol === next.protocol &&
        here.hostname === next.hostname &&
        here.port === next.port &&
        here.pathname === next.pathname &&
        here.search === next.search
      );
    } catch {
      return target === window.location.href;
    }
  };

  const downloadLanCert = () => {
    const link = document.createElement("a");
    link.href = "/assets/certs/lan.crt";
    link.download = "rutsfy-lan.crt";
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const absorbDeferredPrompt = () => {
    if (window.__deferredPwaInstall) {
      deferredPrompt = window.__deferredPwaInstall;
      window.__deferredPwaInstall = null;
    }
  };

  const refreshInstallCopy = () => {
    if (!subEl) return;
    installBtn.disabled = false;
    installBtn.textContent = "Instalar";
    if (deferredPrompt) {
      subEl.textContent = "Toque Instalar para adicionar o RutsFy à tela inicial.";
      return;
    }
    if (isPublicHttpsSite()) {
      subEl.textContent =
        "Toque Instalar ou use o menu do Chrome (⋮) → Instalar app ou Adicionar à tela inicial.";
      return;
    }
    if (!isOnPwaInstallOrigin()) {
      subEl.textContent = "Instalar abre a conexão segura (porta 8443) para concluir.";
      return;
    }
    subEl.textContent =
      "O Chrome ainda não liberou a instalação. Aguarde alguns segundos ou baixe o certificado da rede em Configurações > Segurança.";
    installBtn.textContent = "Baixar certificado";
  };

  const maybeShowInstallBanner = () => {
    if (!shouldOfferInstall()) return;
    refreshInstallCopy();
    showBanner();
  };

  const onInstallPromptReady = () => {
    absorbDeferredPrompt();
    refreshInstallCopy();
    if (shouldOfferInstall()) showBanner();
  };

  let installWaitTimer = null;
  const scheduleInstallWaitHint = () => {
    if (installWaitTimer) window.clearTimeout(installWaitTimer);
    if (!shouldOfferInstall() || deferredPrompt) return;
    if (!isPublicHttpsSite() && !isOnPwaInstallOrigin()) return;
    installWaitTimer = window.setTimeout(() => {
      absorbDeferredPrompt();
      if (!deferredPrompt) refreshInstallCopy();
    }, 4000);
  };

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredPrompt = event;
    window.__deferredPwaInstall = event;
    onInstallPromptReady();
  });

  window.addEventListener("rutsfy-pwa-install-ready", onInstallPromptReady);

  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    hideBanner();
  });

  installBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    absorbDeferredPrompt();
    if (deferredPrompt) {
      installBtn.disabled = true;
      try {
        await deferredPrompt.prompt();
        const choice = await deferredPrompt.userChoice;
        if (choice?.outcome === "accepted") {
          deferredPrompt = null;
          window.__deferredPwaInstall = null;
          hideBanner();
        }
      } catch {
        if (subEl) {
          subEl.textContent = isPublicHttpsSite()
            ? "Use o menu do Chrome (⋮) → Instalar app ou Adicionar à tela inicial."
            : "Não foi possível abrir a instalação automática. Baixe o certificado da rede ou use o menu do Chrome.";
        }
      } finally {
        installBtn.disabled = false;
        refreshInstallCopy();
      }
      return;
    }
    if (!isOnPwaInstallOrigin()) {
      const target = pwaInstallUrl();
      if (!isSamePageUrl(target)) {
        window.location.assign(target);
      } else if (subEl) {
        subEl.textContent =
          "Você já está na porta 8443. Aguarde o Chrome liberar a instalação ou baixe o certificado.";
      }
      return;
    }
    if (isPublicHttpsSite()) {
      if (subEl) {
        subEl.textContent =
          "Se o diálogo não abrir, use o menu do Chrome (⋮) → Instalar app ou Adicionar à tela inicial.";
      }
      return;
    }
    downloadLanCert();
    if (subEl) {
      subEl.textContent =
        "Arquivo baixado: instale como certificado CA (Configurações → Segurança), reinicie o Chrome e abra de novo esta página.";
    }
  });

  dismissBtn.addEventListener("click", () => {
    hideBanner();
  });

  if ("serviceWorker" in navigator) {
    const base = (window.RUTSFY_BASE || "").replace(/\/$/, "");
    const scope = base ? `${base}/` : "/";
    navigator.serviceWorker.register(rutUrl("/sw.js?v=3"), { scope }).catch(() => {});
  }

  absorbDeferredPrompt();
  window.__showPwaInstallBanner = maybeShowInstallBanner;
  window.setTimeout(() => {
    maybeShowInstallBanner();
    scheduleInstallWaitHint();
  }, 600);
  window.addEventListener("pageshow", () => {
    window.setTimeout(maybeShowInstallBanner, 300);
  });
}

installApiFetch();
bindAuthUi();
bindUserMenuUi();
bindPwaInstall();
applyTheme("rutsfy", {});
applyColorScheme("dark");

async function bootstrapApp() {
  document.documentElement.classList.toggle("platform-ios", isIosDevice());
  document.documentElement.classList.toggle("platform-android", isAndroidDevice());
  bindMobileBackNavigation();
  initMediaSessionHandlers();
  const ok = await bootstrapAuth();
  if (ok) {
    await onAuthenticated();
    const params = new URLSearchParams(window.location.search);
    if (params.get("q")) {
      input.value = params.get("q");
      form.requestSubmit();
    }
  } else {
    loadUserVolume();
  }
}

void bootstrapApp();
