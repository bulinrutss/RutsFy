package dev.ruts.rutsfy

import android.app.Application
import android.os.Build
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.ruts.rutsfy.BuildConfig
import dev.ruts.rutsfy.data.AppUpdate
import dev.ruts.rutsfy.data.CatalogCard
import dev.ruts.rutsfy.data.CollectionPage
import dev.ruts.rutsfy.data.ExplorePage
import dev.ruts.rutsfy.data.HomeFeed
import dev.ruts.rutsfy.data.SavedCollection
import dev.ruts.rutsfy.data.SearchPage
import dev.ruts.rutsfy.data.Track
import dev.ruts.rutsfy.data.UserPlaylist
import dev.ruts.rutsfy.player.DownloadedCollection
import dev.ruts.rutsfy.player.DownloadsState
import dev.ruts.rutsfy.player.NowPlaying
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import java.io.File
import java.util.UUID
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

enum class MainTab { Library, Explore, History }

const val DOWNLOADED_ARTIST = "downloaded-artist"

data class BrowseFrame(
    val page: CollectionPage,
    val returnToSearch: Boolean,
)

data class UiState(
    val booting: Boolean = true,
    val loggedIn: Boolean = false,
    val nickname: String = "",
    val tab: MainTab = MainTab.Library,
    val home: HomeFeed = HomeFeed(),
    val explore: ExplorePage = ExplorePage(),
    val library: List<Track> = emptyList(),
    val history: List<Track> = emptyList(),
    val libraryIds: Set<String> = emptySet(),
    val userPlaylists: List<UserPlaylist> = emptyList(),
    val savedCollections: List<SavedCollection> = emptyList(),
    val saveTarget: Track? = null,
    val query: String = "",
    val search: SearchPage? = null,
    val searchOnTop: Boolean = false,
    val stack: List<BrowseFrame> = emptyList(),
    val loading: Boolean = false,
    val catalogLoading: Boolean = false,
    val message: String = "",
    val updateMessage: String = "",
    val installedVersionName: String = "",
    val installedVersionCode: Int = 0,
    val remoteVersionName: String = "",
    val remoteVersionCode: Int = 0,
    val updateAvailable: Boolean = false,
    val updateBusy: Boolean = false,
)

private fun networkUserMessage(exc: Throwable, fallback: String): String {
    val raw = exc.message.orEmpty()
    if (
        raw.contains("Unable to resolve host", ignoreCase = true) ||
            raw.contains("No address associated", ignoreCase = true) ||
            raw.contains("failed to connect", ignoreCase = true) ||
            raw.contains("timeout", ignoreCase = true)
    ) {
        return "Sem acesso ao servidor (ruts.dev). Verifique a internet, troque Wi‑Fi/dados ou desative DNS privado no Android."
    }
    return raw.ifBlank { fallback }
}

class AppViewModel(app: Application) : AndroidViewModel(app) {
    private val ruts = app as RutsFyApp
    private val api = ruts.api
    private val _ui = MutableStateFlow(UiState())
    val ui: StateFlow<UiState> = _ui.asStateFlow()
    val now: StateFlow<NowPlaying> = ruts.player.state
    val downloads: StateFlow<DownloadsState> = ruts.offline.state
    private val session = app.getSharedPreferences("rutsfy_session", Application.MODE_PRIVATE)
    private val _pendingUpdate = MutableStateFlow<File?>(null)
    val pendingUpdate: StateFlow<File?> = _pendingUpdate.asStateFlow()
    private var searchJob: Job? = null
    private var pendingRemote: AppUpdate? = null

    init {
        refreshAppVersion()
        viewModelScope.launch {
            val nick = withContext(Dispatchers.IO) { runCatching { api.me() } }
                .getOrElse { session.getString("nickname", null) }
            if (nick == null) {
                _ui.update { it.copy(booting = false, loggedIn = false) }
            } else {
                enter(nick)
            }
        }
    }

    fun consumeUpdate() {
        _pendingUpdate.value = null
    }

    fun refreshAppVersion() {
        viewModelScope.launch {
            val installed = installedVersionCode()
            val label = BuildConfig.VERSION_NAME.ifBlank { installed.toString() }
            _ui.update {
                it.copy(
                    installedVersionName = label,
                    installedVersionCode = installed.toInt(),
                )
            }
            val info = withContext(Dispatchers.IO) { runCatching { api.remoteAppVersion() }.getOrNull() } ?: return@launch
            val remoteCode = info.versionCode.toLong()
            val remoteLabel = info.versionName.ifBlank { info.versionCode.toString() }
            val available = remoteCode > installed && info.url.isNotBlank()
            pendingRemote = if (available) info else null
            _ui.update {
                it.copy(
                    remoteVersionCode = info.versionCode,
                    remoteVersionName = remoteLabel,
                    updateAvailable = available,
                )
            }
        }
    }

    fun downloadAndInstallUpdate() {
        val info = pendingRemote ?: return
        if (_ui.value.updateBusy) return
        viewModelScope.launch {
            val installed = installedVersionCode()
            if (info.versionCode.toLong() <= installed) {
                _ui.update { it.copy(updateAvailable = false, updateMessage = "Você já está na versão mais recente") }
                return@launch
            }
            val label = info.versionName.ifBlank { info.versionCode.toString() }
            _ui.update { it.copy(updateBusy = true, updateMessage = "Baixando atualização $label…") }
            val dest = File(getApplication<Application>().cacheDir, "updates/rutsfy.apk")
            try {
                withContext(Dispatchers.IO) { api.downloadApp(info.url, dest) }
            } catch (exc: Exception) {
                if (exc is CancellationException) throw exc
                _ui.update { it.copy(updateBusy = false, updateMessage = "Não foi possível baixar a atualização") }
                return@launch
            }
            val packed = archiveVersionCode(dest)
            if (packed <= installed) {
                _ui.update {
                    it.copy(
                        updateBusy = false,
                        updateAvailable = false,
                        updateMessage = "O APK baixado não é mais novo que o instalado",
                    )
                }
                return@launch
            }
            _ui.update { it.copy(updateBusy = false, updateMessage = "Confirme a instalação da versão $label") }
            _pendingUpdate.value = dest
        }
    }

    private fun archiveVersionCode(file: File): Long {
        val app = getApplication<Application>()
        val info = app.packageManager.getPackageArchiveInfo(file.absolutePath, 0) ?: return 0L
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) info.longVersionCode else @Suppress("DEPRECATION") info.versionCode.toLong()
    }

    private fun installedVersionCode(): Long {
        val app = getApplication<Application>()
        val info = app.packageManager.getPackageInfo(app.packageName, 0)
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) info.longVersionCode else @Suppress("DEPRECATION") info.versionCode.toLong()
    }

    fun login(nickname: String, password: String, register: Boolean) {
        viewModelScope.launch {
            _ui.update { it.copy(loading = true, message = "") }
            try {
                val nick = withContext(Dispatchers.IO) { api.login(nickname.trim(), password, register) }
                enter(nick)
            } catch (exc: Exception) {
                _ui.update { it.copy(loading = false, message = networkUserMessage(exc, "Não foi possível entrar")) }
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { api.logout() }
            ruts.cookies.clear()
            session.edit().remove("nickname").apply()
            ruts.player.stop()
            _ui.value = UiState(booting = false, loggedIn = false)
            refreshAppVersion()
        }
    }

    fun selectTab(tab: MainTab) {
        _ui.update { it.copy(tab = tab, stack = emptyList(), query = "", search = null, searchOnTop = false, message = "") }
        viewModelScope.launch {
            if (tab == MainTab.History) refreshHistory()
            if (tab == MainTab.Library) refreshLibrary()
        }
    }

    fun setQuery(query: String) {
        _ui.update { it.copy(query = query, searchOnTop = query.isNotBlank()) }
        searchJob?.cancel()
        val term = query.trim()
        if (term.length < 2) {
            _ui.update { it.copy(search = null, loading = false) }
            return
        }
        searchJob = viewModelScope.launch {
            delay(350)
            _ui.update { it.copy(loading = true) }
            try {
                val page = withContext(Dispatchers.IO) { api.search(term) }
                _ui.update { it.copy(search = page, loading = false, message = "") }
            } catch (exc: Exception) {
                if (exc is CancellationException) throw exc
                _ui.update { it.copy(loading = false, message = networkUserMessage(exc, "Busca falhou")) }
            }
        }
    }

    /** Álbum ou artista de "Ouvir de novo": monta as faixas e toca, como no site. */
    fun playOrigin(card: CatalogCard) {
        viewModelScope.launch {
            _ui.update { it.copy(loading = true, message = "Montando a lista…") }
            try {
                val page = withContext(Dispatchers.IO) { api.open(card.kind, card.id) }
                if (page.tracks.isEmpty()) {
                    _ui.update { it.copy(loading = false, message = "Nenhuma faixa nesta lista") }
                } else {
                    _ui.update { it.copy(loading = false, message = "") }
                    ruts.player.play(page.tracks, 0, card.kind, card.id)
                }
            } catch (exc: Exception) {
                _ui.update { it.copy(loading = false, message = networkUserMessage(exc, "Não achei as faixas")) }
            }
        }
    }

    fun open(card: CatalogCard) {
        viewModelScope.launch {
            val current = _ui.value
            val returnToSearch = current.query.isNotBlank() && (current.searchOnTop || current.stack.isEmpty())
            val search = current.search
            if (card.kind == "artist" && search != null && search.focusArtistId == card.id && search.tracks.isNotEmpty()) {
                val page = CollectionPage(
                    title = search.focusArtistName.ifBlank { card.title },
                    cover = search.focusArtistPicture.ifBlank { card.picture },
                    tracks = search.tracks,
                    cards = search.albums,
                    kind = "artist",
                    id = card.id,
                )
                _ui.update {
                    it.copy(
                        stack = it.stack + BrowseFrame(page, returnToSearch),
                        searchOnTop = false,
                        message = "",
                    )
                }
                return@launch
            }
            _ui.update { it.copy(loading = true, message = "") }
            try {
                val page = withContext(Dispatchers.IO) { api.open(card.kind, card.id) }
                _ui.update {
                    it.copy(
                        stack = it.stack + BrowseFrame(page, returnToSearch),
                        searchOnTop = false,
                        loading = false,
                    )
                }
            } catch (exc: Exception) {
                _ui.update { it.copy(loading = false, message = networkUserMessage(exc, "Catálogo indisponível")) }
            }
        }
    }

    fun back() {
        _ui.update { state ->
            val top = state.stack.lastOrNull() ?: return@update state
            state.copy(
                stack = state.stack.dropLast(1),
                searchOnTop = top.returnToSearch && state.query.isNotBlank(),
                message = "",
            )
        }
    }

    fun play(
        tracks: List<Track>,
        index: Int,
        originKind: String? = null,
        originId: String? = null,
        keepContinuation: Boolean = false,
    ) {
        if (tracks.isEmpty()) return
        ruts.player.play(tracks, index, originKind, originId, keepContinuation)
    }

    fun togglePlay() = ruts.player.toggle()

    fun next() = ruts.player.next()

    fun previous() = ruts.player.previous()

    fun seekTo(positionMs: Long) = ruts.player.seekTo(positionMs)

    fun positionMs(): Long = ruts.player.positionMs()

    fun durationMs(): Long = ruts.player.durationMs()

    fun promptSave(track: Track) {
        if (_ui.value.userPlaylists.isEmpty()) {
            toggleLibrary(track)
        } else {
            _ui.update { it.copy(saveTarget = track) }
        }
    }

    fun dismissSave() {
        _ui.update { it.copy(saveTarget = null) }
    }

    fun toggleDownload(track: Track) {
        val state = downloads.value
        if (state.isSingle(track)) ruts.offline.removeSingle(track) else ruts.offline.downloadSingle(track)
    }

    fun toggleDownloadCollection(page: CollectionPage) {
        if (page.tracks.isEmpty()) return
        if (downloads.value.collection(page.kind, page.id) != null) {
            ruts.offline.removeCollection(page.kind, page.id)
            return
        }
        ruts.offline.downloadCollection(
            DownloadedCollection(
                kind = page.kind,
                id = page.id,
                title = page.title,
                picture = page.cover.ifBlank { page.tracks.firstOrNull()?.thumbnailUrl.orEmpty() },
                subtitle = page.subtitle,
                tracks = page.tracks,
            ),
        )
    }

    fun openDownloadedCollection(kind: String, id: String) {
        val item = downloads.value.collection(kind, id) ?: return
        pushPage(
            CollectionPage(
                title = item.title,
                subtitle = item.subtitle,
                cover = item.picture,
                tracks = item.tracks,
                kind = item.kind,
                id = item.id,
            ),
        )
    }

    fun openDownloadedArtist(artist: String) {
        val tracks = downloads.value.singles.filter { it.artist.ifBlank { "Outros" } == artist }
        pushPage(
            CollectionPage(
                title = artist,
                subtitle = "${tracks.size} baixadas",
                cover = tracks.firstOrNull()?.thumbnailUrl.orEmpty(),
                tracks = tracks,
                kind = DOWNLOADED_ARTIST,
                id = artist,
            ),
        )
    }

    private fun pushPage(page: CollectionPage) {
        _ui.update { it.copy(stack = it.stack + BrowseFrame(page, false), searchOnTop = false, message = "") }
    }

    fun createPlaylist(title: String) {
        val name = title.trim()
        if (name.isBlank()) return
        val next = listOf(UserPlaylist(UUID.randomUUID().toString(), name)) + _ui.value.userPlaylists
        storePlaylists(next, "Playlist criada")
    }

    fun saveTrackIn(track: Track, playlistId: String?) {
        _ui.update { it.copy(saveTarget = null) }
        if (playlistId == null) {
            toggleLibrary(track)
            return
        }
        val playlists = _ui.value.userPlaylists.map { playlist ->
            if (playlist.id != playlistId) playlist
            else {
                val exists = playlist.tracks.any { it.sameSong(track) }
                val tracks = if (exists) playlist.tracks.filterNot { it.sameSong(track) } else listOf(track) + playlist.tracks
                playlist.copy(tracks = tracks)
            }
        }
        val added = playlists.find { it.id == playlistId }?.tracks?.any { it.sameSong(track) } == true
        storePlaylists(playlists, if (added) "Na playlist" else "Removida da playlist")
    }

    fun openUserPlaylist(id: String) {
        val playlist = _ui.value.userPlaylists.find { it.id == id } ?: return
        val page = CollectionPage(
            title = playlist.title,
            subtitle = if (playlist.tracks.isEmpty()) "Playlist vazia" else "${playlist.tracks.size} faixas",
            cover = playlist.tracks.firstOrNull()?.thumbnailUrl.orEmpty(),
            tracks = playlist.tracks,
            kind = "user",
            id = playlist.id,
        )
        _ui.update {
            it.copy(
                stack = it.stack + BrowseFrame(page, false),
                searchOnTop = false,
                message = "",
            )
        }
    }

    fun toggleSavedCollection(page: CollectionPage) {
        if (page.kind != "album" && page.kind != "playlist") return
        if (page.id.isBlank()) return
        val current = _ui.value.savedCollections
        val exists = current.any { it.kind == page.kind && it.id == page.id }
        val next = if (exists) {
            current.filterNot { it.kind == page.kind && it.id == page.id }
        } else {
            listOf(
                SavedCollection(
                    kind = page.kind,
                    id = page.id,
                    title = page.title,
                    picture = page.cover,
                    subtitle = if (page.kind == "album") "Álbum" else "Playlist",
                ),
            ) + current
        }
        _ui.update { it.copy(savedCollections = next, message = if (exists) "Removido" else "Na biblioteca") }
        viewModelScope.launch {
            runCatching {
                withContext(Dispatchers.IO) { api.saveLibraryExtras(_ui.value.userPlaylists, next) }
            }.onFailure { exc ->
                _ui.update { it.copy(message = networkUserMessage(exc, "Não foi possível salvar")) }
            }
        }
    }

    private fun storePlaylists(playlists: List<UserPlaylist>, message: String) {
        val saved = _ui.value.savedCollections
        _ui.update { it.copy(userPlaylists = playlists, message = message) }
        viewModelScope.launch {
            runCatching {
                withContext(Dispatchers.IO) { api.saveLibraryExtras(playlists, saved) }
            }.onFailure { exc ->
                _ui.update { it.copy(message = networkUserMessage(exc, "Não foi possível salvar")) }
            }
        }
    }

    private fun Track.sameSong(other: Track): Boolean {
        val videoId = videoId
        if (!videoId.isNullOrBlank() && videoId == other.videoId) return true
        val deezerId = deezerId
        if (!deezerId.isNullOrBlank() && deezerId == other.deezerId) return true
        return key == other.key
    }

    fun toggleLibrary(track: Track) {
        val videoId = track.videoId
        val saved = videoId != null && videoId in _ui.value.libraryIds
        viewModelScope.launch {
            _ui.update {
                it.copy(
                    loading = true,
                    message = if (saved) "Removendo…" else "Salvando na biblioteca…",
                )
            }
            try {
                withContext(Dispatchers.IO) {
                    if (saved && videoId != null) api.removeFromLibrary(videoId) else api.addToLibrary(track)
                }
                refreshLibrary()
                _ui.update {
                    it.copy(loading = false, message = if (saved) "Removida da biblioteca" else "Na biblioteca")
                }
            } catch (exc: Exception) {
                _ui.update { it.copy(loading = false, message = networkUserMessage(exc, "Não foi possível salvar")) }
            }
        }
    }

    fun clearMessage() {
        _ui.update { it.copy(message = "") }
    }

    private suspend fun enter(nickname: String) {
        session.edit().putString("nickname", nickname).apply()
        _ui.update {
            it.copy(
                booting = false,
                loggedIn = true,
                nickname = nickname,
                loading = true,
                catalogLoading = true,
                message = "",
            )
        }
        try {
            coroutineScope {
                val libraryJob = async(Dispatchers.IO) { runCatching { api.library() }.getOrDefault(emptyList()) }
                val extrasJob = async(Dispatchers.IO) {
                    runCatching { api.libraryExtras() }.getOrDefault(emptyList<UserPlaylist>() to emptyList())
                }
                val homeJob = async(Dispatchers.IO) { runCatching { api.homeFeed() }.getOrDefault(HomeFeed()) }
                val exploreJob = async(Dispatchers.IO) { runCatching { api.explore() }.getOrDefault(ExplorePage()) }
                val historyJob = async(Dispatchers.IO) { runCatching { api.history() }.getOrDefault(emptyList()) }

                val library = libraryJob.await()
                val extras = extrasJob.await()
                _ui.update {
                    it.copy(
                        library = library,
                        libraryIds = library.mapNotNull { track -> track.videoId }.toSet(),
                        userPlaylists = extras.first,
                        savedCollections = extras.second,
                        loading = false,
                    )
                }

                val home = homeJob.await()
                val explore = exploreJob.await()
                val history = historyJob.await()
                _ui.update {
                    it.copy(
                        home = home,
                        explore = explore,
                        history = history,
                        catalogLoading = false,
                    )
                }
            }
        } catch (exc: Exception) {
            if (exc is CancellationException) throw exc
            _ui.update {
                it.copy(
                    loading = false,
                    catalogLoading = false,
                    message = networkUserMessage(exc, "Falha ao carregar"),
                )
            }
        }
    }

    private suspend fun refreshLibrary() {
        val library = withContext(Dispatchers.IO) { api.library() }
        _ui.update { it.copy(library = library, libraryIds = library.mapNotNull { track -> track.videoId }.toSet()) }
    }

    private suspend fun refreshHistory() {
        val history = withContext(Dispatchers.IO) { api.history() }
        _ui.update { it.copy(history = history) }
    }
}
