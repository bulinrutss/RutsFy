package dev.ruts.rutsfy.player

import android.net.Uri
import androidx.media3.common.MediaItem
import androidx.media3.common.MediaMetadata
import androidx.media3.common.MimeTypes
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import dev.ruts.rutsfy.RutsFyApp
import dev.ruts.rutsfy.data.Track
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

data class NowPlaying(
    val track: Track? = null,
    val queue: List<Track> = emptyList(),
    val index: Int = -1,
    val loadingKey: String? = null,
    val queueSize: Int = 0,
    val playing: Boolean = false,
    val status: String = "",
)

class PlaybackCoordinator(private val app: RutsFyApp) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val _state = MutableStateFlow(NowPlaying())
    val state: StateFlow<NowPlaying> = _state.asStateFlow()

    private var exo: ExoPlayer? = null
    private var queue: List<Track> = emptyList()
    private var index: Int = -1
    private var job: Job? = null
    private var prefetchJob: Job? = null
    private var generation: Int = 0
    private var armEnded: Boolean = false
    private var continuationExhausted: Boolean = false
    private var originKind: String? = null
    private var originId: String? = null
    private val playedAlbumIds = mutableSetOf<String>()
    private val playedPlaylistIds = mutableSetOf<String>()
    private val continuedArtistIds = mutableSetOf<String>()
    private var continuationJob: Job? = null
    private val readyTracks = mutableMapOf<String, Track>()
    private val loadingTracks = mutableMapOf<String, Deferred<Track>>()

    fun bind(player: ExoPlayer) {
        exo = player
        player.addListener(
            object : Player.Listener {
                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    _state.update { it.copy(playing = isPlaying) }
                }

                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_READY) armEnded = true
                    if (playbackState == Player.STATE_ENDED && armEnded && job?.isActive != true) {
                        armEnded = false
                        next()
                    }
                }

                override fun onPlayerError(error: PlaybackException) {
                    if (job?.isActive == true || !armEnded) return
                    armEnded = false
                    next()
                }
            },
        )
    }

    fun canNext(): Boolean = index + 1 < queue.size || !continuationExhausted

    fun canPrevious(): Boolean = index > 0 || (exo?.currentPosition ?: 0L) > 3_000

    fun play(
        tracks: List<Track>,
        start: Int,
        originKind: String? = null,
        originId: String? = null,
        keepContinuation: Boolean = false,
    ) {
        if (tracks.isEmpty()) return
        if (!keepContinuation) {
            continuationExhausted = false
            this.originKind = originKind
            this.originId = originId
            playedAlbumIds.clear()
            playedPlaylistIds.clear()
            continuedArtistIds.clear()
            if (originKind == "album" && !originId.isNullOrBlank()) playedAlbumIds.add(originId)
            if (originKind == "artist" && !originId.isNullOrBlank()) continuedArtistIds.add(originId)
            if (originKind == "playlist" && !originId.isNullOrBlank()) playedPlaylistIds.add(originId)
        }
        queue = tracks
        startAt(start.coerceIn(tracks.indices))
    }

    fun stop() {
        generation += 1
        job?.cancel()
        queue = emptyList()
        index = -1
        armEnded = false
        prefetchJob?.cancel()
        synchronized(loadingTracks) {
            readyTracks.clear()
            loadingTracks.clear()
        }
        continuationJob?.cancel()
        exo?.stop()
        exo?.clearMediaItems()
        _state.value = NowPlaying()
    }

    fun toggle() {
        val player = exo ?: return
        if (player.isPlaying) player.pause() else if (player.playbackState != Player.STATE_IDLE) player.play()
    }

    fun next() {
        val start = if (index < 0) 0 else index + 1
        if (start < queue.size) {
            startAt(start)
            return
        }
        val pending = continuationJob
        if (pending?.isActive == true) {
            val token = generation
            scope.launch {
                pending.join()
                if (token != generation) return@launch
                val at = index + 1
                if (at < queue.size) startAt(at)
            }
            return
        }
        continueAfterQueue()
    }

    fun previous() {
        val player = exo
        if (player != null && player.currentPosition > 3_000) {
            player.seekTo(0)
            return
        }
        if (index <= 0) {
            player?.seekTo(0)
            return
        }
        startAt(index - 1)
    }

    fun seekTo(positionMs: Long) {
        exo?.seekTo(positionMs)
    }

    fun positionMs(): Long = exo?.currentPosition ?: 0L

    fun durationMs(): Long = exo?.duration?.takeIf { it > 0 } ?: 0L

    private fun startAt(target: Int, fromContinuation: Boolean = false) {
        if (queue.getOrNull(target) == null) return
        val token = ++generation
        armEnded = false
        job?.cancel()
        prefetchJob?.cancel()
        if (!fromContinuation) continuationJob?.cancel()
        job = scope.launch {
            prefetchFromIndex(target, token)
            var cursor = target
            while (cursor < queue.size && token == generation) {
                val track = queue[cursor]
                index = cursor
                _state.update { it.copy(loadingKey = track.key, queue = queue, queueSize = queue.size) }
                try {
                    val player = awaitPlayer()
                    if (token != generation) return@launch
                    val ready = loadTrack(track).await()
                    if (token != generation) return@launch
                    val local = app.offline.localTrack(ready)
                    val path = (local ?: ready).streamPath ?: error("Sem áudio")
                    val url = if (local != null) path else app.api.absolute(path)
                    if (local == null) saveOffline(ready)
                    player.setMediaItem(ready.toMediaItem(url))
                    player.prepare()
                    player.play()
                    awaitAudible(player)
                    if (token != generation) return@launch
                    queue = queue.toMutableList().also { rows ->
                        if (cursor in rows.indices) rows[cursor] = ready
                    }
                    index = cursor
                    _state.update {
                        it.copy(
                            track = ready,
                            queue = queue,
                            index = cursor,
                            queueSize = queue.size,
                            loadingKey = null,
                            status = "",
                            playing = true,
                        )
                    }
                    withContext(Dispatchers.IO) { app.api.recordPlay(ready) }
                    prefetchFromIndex(cursor, token)
                    if (cursor == queue.lastIndex) preloadContinuation(token)
                    return@launch
                } catch (exc: CancellationException) {
                    throw exc
                } catch (_: Exception) {
                    cursor += 1
                }
            }
            if (token != generation) return@launch
            continueAfterQueue()
        }
    }

    /** Na última faixa, busca a sequência seguinte e já começa o download, sem trocar o que está tocando. */
    private fun preloadContinuation(token: Int) {
        if (continuationExhausted || continuationJob?.isActive == true) return
        if (index < queue.lastIndex) return
        continuationJob = scope.launch {
            val extra = withContext(Dispatchers.IO) { runCatching { pullContinuation() }.getOrDefault(emptyList()) }
            if (token != generation) return@launch
            if (extra.isEmpty()) {
                continuationExhausted = true
                return@launch
            }
            queue = queue + extra
            _state.update { it.copy(queue = queue, queueSize = queue.size) }
            prefetchFromIndex(index, token)
        }
    }

    /** Quando a fila acaba, entra no próximo álbum, num artista parecido ou no gênero. */
    private fun continueAfterQueue() {
        if (continuationExhausted || continuationJob?.isActive == true) return
        val token = generation
        job?.cancel()
        prefetchJob?.cancel()
        armEnded = false
        _state.update { it.copy(status = "Próximo álbum…") }
        continuationJob = scope.launch {
            val extra = withContext(Dispatchers.IO) { runCatching { pullContinuation() }.getOrDefault(emptyList()) }
            if (token != generation) return@launch
            if (extra.isEmpty()) {
                continuationExhausted = true
                _state.update { it.copy(status = "", loadingKey = null) }
                return@launch
            }
            val start = queue.size
            queue = queue + extra
            _state.update { it.copy(queue = queue, queueSize = queue.size, status = "") }
            startAt(start, fromContinuation = true)
        }
    }

    private fun pullContinuation(): List<Track> {
        val fromGenre = nextGenrePlaylist()
        if (fromGenre.isNotEmpty()) return fromGenre
        val artistId = currentArtistId()
        if (artistId != null) {
            val albumTracks = nextAlbumTracks(artistId)
            if (albumTracks.isNotEmpty()) return albumTracks
            continuedArtistIds.add(artistId)
            val related = runCatching { app.api.relatedArtists(artistId) }.getOrDefault(emptyList())
            val nextArtist = related.firstOrNull { it.id.isNotBlank() && it.id !in continuedArtistIds }
            if (nextArtist != null) {
                continuedArtistIds.add(nextArtist.id)
                originKind = "artist"
                originId = nextArtist.id
                val page = runCatching { app.api.open("artist", nextArtist.id) }.getOrNull()
                val fresh = filterFresh(page?.tracks.orEmpty())
                if (fresh.isNotEmpty()) return fresh
            }
            val radio = filterFresh(runCatching { app.api.artistRadio(artistId) }.getOrDefault(emptyList()))
            if (radio.isNotEmpty()) return radio
        }
        val genre = queue.getOrNull(index)?.genre?.ifBlank { null }
            ?: queue.lastOrNull { it.genre.isNotBlank() }?.genre
        if (!genre.isNullOrBlank()) {
            val found = runCatching { app.api.search(genre) }.getOrNull()
            val fresh = filterFresh(found?.tracks.orEmpty())
            if (fresh.isNotEmpty()) return fresh
        }
        return emptyList()
    }

    private fun nextGenrePlaylist(): List<Track> {
        if (originKind != "genre" || originId.isNullOrBlank()) return emptyList()
        val genre = runCatching { app.api.open("genre", originId!!) }.getOrNull() ?: return emptyList()
        for (card in genre.cards) {
            if (card.kind != "playlist" || card.id.isBlank() || card.id in playedPlaylistIds) continue
            playedPlaylistIds.add(card.id)
            val page = runCatching { app.api.open("playlist", card.id) }.getOrNull() ?: continue
            val fresh = filterFresh(page.tracks)
            if (fresh.isNotEmpty()) return fresh
        }
        originKind = null
        return emptyList()
    }

    private fun nextAlbumTracks(artistId: String): List<Track> {
        val artist = runCatching { app.api.open("artist", artistId) }.getOrNull() ?: return emptyList()
        val currentAlbum = queue.getOrNull(index)?.albumId
        if (!currentAlbum.isNullOrBlank() && queue.all { it.albumId == currentAlbum }) {
            playedAlbumIds.add(currentAlbum)
        }
        for (card in artist.cards) {
            if (card.kind != "album" || card.id.isBlank() || card.id in playedAlbumIds) continue
            playedAlbumIds.add(card.id)
            val album = runCatching { app.api.open("album", card.id) }.getOrNull() ?: continue
            val fresh = filterFresh(album.tracks)
            if (fresh.isNotEmpty()) {
                originKind = "album"
                originId = card.id
                return fresh
            }
        }
        return emptyList()
    }

    private fun filterFresh(tracks: List<Track>): List<Track> {
        val seen = queue.map { it.deezerId ?: it.videoId ?: it.key }.toSet()
        return tracks.filter { track ->
            val key = track.deezerId ?: track.videoId ?: track.key
            key.isNotBlank() && key !in seen
        }
    }

    private fun currentArtistId(): String? {
        return queue.getOrNull(index)?.artistId?.takeIf { it.isNotBlank() }
            ?: queue.lastOrNull { !it.artistId.isNullOrBlank() }?.artistId
    }

    private suspend fun awaitAudible(player: ExoPlayer) {
        if (player.isPlaying || (player.playbackState == Player.STATE_READY && player.playWhenReady)) return
        withTimeout(20_000) {
            suspendCancellableCoroutine { cont ->
                val listener = object : Player.Listener {
                    private fun finish(error: Exception? = null) {
                        player.removeListener(this)
                        if (!cont.isActive) return
                        if (error == null) cont.resume(Unit) else cont.resumeWithException(error)
                    }

                    override fun onIsPlayingChanged(isPlaying: Boolean) {
                        if (isPlaying) finish()
                    }

                    override fun onPlaybackStateChanged(playbackState: Int) {
                        if (playbackState == Player.STATE_READY && player.playWhenReady) finish()
                    }

                    override fun onPlayerError(error: PlaybackException) {
                        finish(error)
                    }
                }
                player.addListener(listener)
                cont.invokeOnCancellation { player.removeListener(listener) }
                if (player.isPlaying || (player.playbackState == Player.STATE_READY && player.playWhenReady)) {
                    listener.onIsPlayingChanged(true)
                }
            }
        }
    }

    /** Baixa todas as faixas restantes da fila carregada (playlist/busca), em paralelo limitado. */
    private fun prefetchFromIndex(fromIndex: Int, token: Int) {
        prefetchJob?.cancel()
        if (fromIndex + 1 >= queue.size) return
        val upcoming = (fromIndex + 1 until queue.size).mapNotNull { queue.getOrNull(it) }
        if (upcoming.isEmpty()) return
        prefetchJob = scope.launch {
            val gate = Semaphore(MAX_PREFETCH_CONCURRENT)
            upcoming.map { track ->
                async(Dispatchers.IO) {
                    gate.withPermit {
                        if (token != generation) return@async
                        try {
                            app.offline.download(loadTrack(track).await())
                        } catch (exc: CancellationException) {
                            throw exc
                        } catch (_: Exception) {
                            /* tenta de novo quando a faixa for tocada */
                        }
                    }
                }
            }.awaitAll()
        }
    }

    private fun loadTrack(track: Track): Deferred<Track> {
        val key = track.key
        synchronized(loadingTracks) {
            readyTracks[key]?.let { return CompletableDeferred(it) }
            loadingTracks[key]?.let { return it }
            val deferred = scope.async(Dispatchers.IO) {
                val prepared = app.offline.localTrack(track) ?: app.api.prepare(track)
                synchronized(loadingTracks) {
                    readyTracks[key] = prepared
                    prepared.videoId?.let { readyTracks[it] = prepared }
                }
                prepared
            }
            loadingTracks[key] = deferred
            deferred.invokeOnCompletion {
                synchronized(loadingTracks) {
                    if (loadingTracks[key] === deferred) loadingTracks.remove(key)
                }
            }
            return deferred
        }
    }

    private fun saveOffline(ready: Track) {
        scope.launch(Dispatchers.IO) {
            runCatching { app.offline.download(ready) }
        }
    }

    private suspend fun awaitPlayer(): ExoPlayer {
        repeat(50) {
            exo?.let { return it }
            delay(100)
        }
        error("O player ainda não iniciou")
    }

    private fun Track.toMediaItem(url: String): MediaItem {
        val mime = when {
            url.contains(".opus") || url.contains(".ogg") -> MimeTypes.AUDIO_OGG
            url.contains(".webm") -> MimeTypes.AUDIO_WEBM
            url.contains(".m4a") || url.contains(".mp4") -> MimeTypes.AUDIO_MP4
            url.contains(".mp3") -> MimeTypes.AUDIO_MPEG
            else -> MimeTypes.AUDIO_UNKNOWN
        }
        val art = thumbnailUrl.takeIf { it.startsWith("http://") || it.startsWith("https://") }
        return MediaItem.Builder()
            .setMediaId(videoId ?: deezerId ?: title)
            .setUri(url)
            .setMimeType(mime)
            .setMediaMetadata(
                MediaMetadata.Builder()
                    .setTitle(title)
                    .setArtist(artist)
                    .setAlbumTitle(album)
                    .setArtworkUri(art?.let(Uri::parse))
                    .build(),
            )
            .build()
    }

    private companion object {
        /** Downloads simultâneos em background (resto da fila segue enfileirado). */
        const val MAX_PREFETCH_CONCURRENT = 3
    }
}
