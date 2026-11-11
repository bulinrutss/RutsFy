package dev.ruts.rutsfy.player

import android.content.Context
import android.net.Uri
import dev.ruts.rutsfy.RutsFyApp
import dev.ruts.rutsfy.data.Track
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import okhttp3.Request
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.concurrent.ConcurrentHashMap

data class DownloadedCollection(
    val kind: String,
    val id: String,
    val title: String,
    val picture: String = "",
    val subtitle: String = "",
    val tracks: List<Track> = emptyList(),
)

data class DownloadsState(
    val singles: List<Track> = emptyList(),
    val collections: List<DownloadedCollection> = emptyList(),
    val doneIds: Set<String> = emptySet(),
    val pending: Set<String> = emptySet(),
) {
    fun isDone(track: Track): Boolean =
        track.videoId?.let { it in doneIds } == true || track.deezerId?.let { it in doneIds } == true

    fun isPending(track: Track): Boolean = downloadId(track) in pending

    fun isSingle(track: Track): Boolean = singles.any { sameTrack(it, track) }

    fun collection(kind: String, id: String): DownloadedCollection? =
        collections.firstOrNull { it.kind == kind && it.id == id }
}

fun downloadId(track: Track): String = track.deezerId ?: track.videoId ?: track.key

private fun sameTrack(a: Track, b: Track): Boolean {
    if (!a.videoId.isNullOrBlank() && a.videoId == b.videoId) return true
    if (!a.deezerId.isNullOrBlank() && a.deezerId == b.deezerId) return true
    return a.key == b.key
}

/**
 * Áudio guardado no aparelho. Faixas da fila ficam num cache com limite de espaço;
 * as baixadas pelo usuário (avulsas, álbuns, playlists) ficam presas até serem removidas.
 */
class OfflineAudio(private val app: RutsFyApp) {
    private val dir = File(app.filesDir, "offline-audio").apply { mkdirs() }
    private val manifest = File(dir, "downloads.json")
    private val prefs = app.getSharedPreferences("offline_audio", Context.MODE_PRIVATE)
    private val locks = ConcurrentHashMap<String, Any>()
    private val queued = ConcurrentHashMap.newKeySet<String>()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val gate = Semaphore(MAX_DOWNLOADS)
    private val _state = MutableStateFlow(load())
    val state: StateFlow<DownloadsState> = _state.asStateFlow()

    init {
        resumePending()
    }

    /** A faixa apontando para o arquivo local, ou null se ainda não foi baixada. */
    fun localTrack(track: Track): Track? {
        val videoId = track.videoId ?: track.deezerId?.let { prefs.getString("dz:$it", null) } ?: return null
        val file = fileOf(videoId) ?: return null
        file.setLastModified(System.currentTimeMillis())
        return track.copy(videoId = videoId, streamPath = Uri.fromFile(file).toString())
    }

    fun download(ready: Track) {
        val videoId = ready.videoId ?: return
        val path = ready.streamPath ?: return
        ready.deezerId?.let { prefs.edit().putString("dz:$it", videoId).apply() }
        if (!path.startsWith("file:") && fileOf(videoId) == null) {
            synchronized(locks.getOrPut(videoId) { Any() }) {
                if (fileOf(videoId) == null) fetch(videoId, path)
            }
            trim()
        }
        if (fileOf(videoId) != null) markDone(ready)
    }

    fun downloadSingle(track: Track) {
        change { it.copy(singles = listOf(track) + it.singles.filterNot { row -> sameTrack(row, track) }) }
        enqueue(track)
    }

    fun removeSingle(track: Track) {
        change { it.copy(singles = it.singles.filterNot { row -> sameTrack(row, track) }) }
    }

    fun downloadCollection(collection: DownloadedCollection) {
        change { state ->
            val rest = state.collections.filterNot { it.kind == collection.kind && it.id == collection.id }
            state.copy(collections = listOf(collection) + rest)
        }
        collection.tracks.forEach(::enqueue)
    }

    fun removeCollection(kind: String, id: String) {
        change { state -> state.copy(collections = state.collections.filterNot { it.kind == kind && it.id == id }) }
    }

    private fun enqueue(track: Track) {
        if (_state.value.isDone(track)) return
        val id = downloadId(track)
        if (!queued.add(id)) return
        _state.update { it.copy(pending = it.pending + id) }
        scope.launch {
            try {
                gate.withPermit {
                    if (!isPinned(track)) return@withPermit
                    download(localTrack(track) ?: app.api.prepare(track))
                }
            } catch (exc: CancellationException) {
                throw exc
            } catch (_: Exception) {
                /* tenta de novo na próxima abertura do app */
            } finally {
                queued.remove(id)
                _state.update { it.copy(pending = it.pending - id) }
            }
        }
    }

    private fun resumePending() {
        val state = _state.value
        (state.singles + state.collections.flatMap { it.tracks })
            .filterNot(state::isDone)
            .forEach(::enqueue)
    }

    private fun isPinned(track: Track): Boolean {
        val state = _state.value
        return state.singles.any { sameTrack(it, track) } ||
            state.collections.any { collection -> collection.tracks.any { sameTrack(it, track) } }
    }

    private fun markDone(ready: Track) {
        if (!isPinned(ready)) return
        val stored = ready.copy(streamPath = null)
        change { state ->
            state.copy(
                singles = state.singles.map { if (sameTrack(it, ready)) stored else it },
                collections = state.collections.map { collection ->
                    collection.copy(tracks = collection.tracks.map { if (sameTrack(it, ready)) stored else it })
                },
                doneIds = state.doneIds + listOfNotNull(ready.videoId, ready.deezerId),
            )
        }
    }

    private fun fetch(videoId: String, path: String) {
        val ext = path.substringBefore('?').substringAfterLast('.', "opus").take(5)
        val dest = File(dir, "$videoId.$ext")
        val temp = File(dir, "$videoId.$ext.part")
        val request = Request.Builder().url(app.api.absolute(path)).build()
        app.http.newCall(request).execute().use { response ->
            val body = response.body
            if (!response.isSuccessful || body == null) return
            temp.outputStream().use { out -> body.byteStream().copyTo(out) }
        }
        if (!temp.renameTo(dest)) {
            temp.delete()
            return
        }
        prefs.edit().putString("vid:$videoId", dest.name).apply()
    }

    private fun fileOf(videoId: String): File? {
        val name = prefs.getString("vid:$videoId", null) ?: return null
        return File(dir, name).takeIf { it.isFile && it.length() > 0 }
    }

    private fun trim() {
        val state = _state.value
        val pinned = (state.singles + state.collections.flatMap { it.tracks }).mapNotNull { it.videoId }.toSet()
        val files = dir.listFiles { file ->
            file.isFile && file.extension != "part" && file.name != manifest.name && file.nameWithoutExtension !in pinned
        }.orEmpty()
        var total = files.sumOf { it.length() }
        if (total <= MAX_CACHE_BYTES) return
        val editor = prefs.edit()
        for (file in files.sortedBy { it.lastModified() }) {
            if (total <= MAX_CACHE_BYTES) break
            total -= file.length()
            file.delete()
            editor.remove("vid:${file.nameWithoutExtension}")
        }
        editor.apply()
    }

    private fun change(block: (DownloadsState) -> DownloadsState) {
        synchronized(this) {
            _state.update(block)
            save(_state.value)
        }
    }

    private fun load(): DownloadsState {
        val root = runCatching { JSONObject(manifest.readText()) }.getOrNull() ?: return DownloadsState()
        val singles = tracksOf(root.optJSONArray("singles"))
        val collections = buildList {
            val arr = root.optJSONArray("collections") ?: JSONArray()
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                add(
                    DownloadedCollection(
                        kind = obj.optString("kind"),
                        id = obj.optString("id"),
                        title = obj.optString("title"),
                        picture = obj.optString("picture"),
                        subtitle = obj.optString("subtitle"),
                        tracks = tracksOf(obj.optJSONArray("tracks")),
                    ),
                )
            }
        }
        val done = (singles + collections.flatMap { it.tracks })
            .filter { track -> track.videoId?.let { fileOf(it) } != null }
            .flatMap { listOfNotNull(it.videoId, it.deezerId) }
            .toSet()
        return DownloadsState(singles = singles, collections = collections, doneIds = done)
    }

    private fun save(state: DownloadsState) {
        val root = JSONObject()
            .put("singles", JSONArray().apply { state.singles.forEach { put(trackJson(it)) } })
            .put(
                "collections",
                JSONArray().apply {
                    state.collections.forEach { collection ->
                        put(
                            JSONObject()
                                .put("kind", collection.kind)
                                .put("id", collection.id)
                                .put("title", collection.title)
                                .put("picture", collection.picture)
                                .put("subtitle", collection.subtitle)
                                .put("tracks", JSONArray().apply { collection.tracks.forEach { put(trackJson(it)) } }),
                        )
                    }
                },
            )
        val temp = File(dir, manifest.name + ".part")
        temp.writeText(root.toString())
        temp.renameTo(manifest)
    }

    private fun trackJson(track: Track): JSONObject = JSONObject()
        .put("videoId", track.videoId)
        .put("deezerId", track.deezerId)
        .put("title", track.title)
        .put("artist", track.artist)
        .put("album", track.album)
        .put("genre", track.genre)
        .put("duration", track.duration)
        .put("thumbnailUrl", track.thumbnailUrl)
        .put("artistId", track.artistId)
        .put("albumId", track.albumId)
        .put("catalogSource", track.catalogSource)

    private fun tracksOf(arr: JSONArray?): List<Track> {
        if (arr == null) return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                fun str(key: String): String? = obj.optString(key).takeIf { it.isNotBlank() && it != "null" }
                add(
                    Track(
                        videoId = str("videoId"),
                        deezerId = str("deezerId"),
                        title = str("title") ?: "Faixa",
                        artist = str("artist").orEmpty(),
                        album = str("album").orEmpty(),
                        genre = str("genre").orEmpty(),
                        duration = str("duration").orEmpty(),
                        thumbnailUrl = str("thumbnailUrl").orEmpty(),
                        artistId = str("artistId"),
                        albumId = str("albumId"),
                        catalogSource = str("catalogSource") ?: "deezer",
                    ),
                )
            }
        }
    }

    private companion object {
        const val MAX_CACHE_BYTES = 1_500L * 1024 * 1024
        const val MAX_DOWNLOADS = 2
    }
}
