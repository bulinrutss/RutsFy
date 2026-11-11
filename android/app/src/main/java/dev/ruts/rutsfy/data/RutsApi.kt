package dev.ruts.rutsfy.data

import dev.ruts.rutsfy.BuildConfig
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

class RutsApi(private val http: OkHttpClient) {
    private val origin = BuildConfig.API_ORIGIN.trimEnd('/')
    private val prefix = BuildConfig.API_PREFIX.trimEnd('/')
    private val jsonType = "application/json; charset=utf-8".toMediaType()

    fun absolute(path: String): String {
        if (path.startsWith("http://") || path.startsWith("https://")) return path
        val normalized = if (path.startsWith("/")) path else "/$path"
        return origin + normalized
    }

    fun me(): String? {
        return try {
            val data = get("/api/auth/me")
            data.optJSONObject("user")?.optString("nickname")?.ifBlank { null }
        } catch (exc: ApiException) {
            if (exc.code == 401) null else throw exc
        }
    }

    fun login(nickname: String, password: String, register: Boolean): String {
        val path = if (register) "/api/auth/register" else "/api/auth/login"
        val body = JSONObject().put("nickname", nickname).put("password", password)
        val data = post(path, body)
        return data.optJSONObject("user")?.optString("nickname").orEmpty().ifBlank { nickname }
    }

    fun logout() {
        runCatching { post("/api/auth/logout", JSONObject()) }
    }

    fun remoteAppVersion(): AppUpdate? {
        val data = get("/api/app/version")
        val code = data.optInt("versionCode")
        val url = data.optString("url")
        if (code <= 0) return null
        return AppUpdate(code, data.optString("versionName"), url)
    }

    fun downloadApp(url: String, dest: java.io.File) {
        dest.parentFile?.mkdirs()
        val temp = java.io.File(dest.parentFile, dest.name + ".part")
        http.newCall(Request.Builder().url(absolute(url)).get().build()).execute().use { response ->
            if (!response.isSuccessful) throw ApiException("Não baixou a atualização")
            temp.outputStream().use { out ->
                response.body?.byteStream()?.copyTo(out) ?: throw ApiException("Atualização vazia")
            }
        }
        if (dest.exists()) dest.delete()
        if (!temp.renameTo(dest)) throw ApiException("Não salvou a atualização")
    }

    fun library(): List<Track> = tracksOf(get("/api/library"))

    fun libraryExtras(): Pair<List<UserPlaylist>, List<SavedCollection>> {
        val data = runCatching { get("/api/me/preferences") }.getOrDefault(JSONObject())
        return playlistsOf(data.optJSONArray("userPlaylists")) to collectionsOf(data.optJSONArray("savedCollections"))
    }

    fun saveLibraryExtras(playlists: List<UserPlaylist>, collections: List<SavedCollection>) {
        val body = JSONObject()
        body.put("userPlaylists", JSONArray().apply {
            playlists.forEach { playlist ->
                put(JSONObject()
                    .put("id", playlist.id)
                    .put("title", playlist.title)
                    .put("tracks", JSONArray().apply {
                        playlist.tracks.forEach { track ->
                            val body = track.payload()
                            track.videoId?.let { body.put("videoId", it) }
                            put(body)
                        }
                    }))
            }
        })
        body.put("savedCollections", JSONArray().apply {
            collections.forEach { item ->
                put(JSONObject()
                    .put("kind", item.kind)
                    .put("id", item.id)
                    .put("title", item.title)
                    .put("picture", item.picture)
                    .put("subtitle", item.subtitle))
            }
        })
        put("/api/me/preferences", body)
    }

    fun history(): List<Track> = tracksOf(get("/api/history"))

    fun homeFeed(): HomeFeed {
        val data = get("/api/catalog/deezer/library")
        return HomeFeed(
            listenAgain = cardsOf(data.optJSONArray("listenAgain"), "artist"),
            shelves = shelvesOf(data.optJSONArray("shelves")),
            albumsForYou = cardsOf(data.optJSONArray("albumsForYou"), "album"),
            hitsToday = cardsOf(data.optJSONArray("hitsToday"), "playlist"),
            featuredPlaylists = cardsOf(data.optJSONArray("featuredPlaylists"), "playlist"),
            newReleases = cardsOf(data.optJSONArray("newReleases"), "album"),
        )
    }

    fun explore(): ExplorePage {
        val data = get("/api/catalog/deezer/explore")
        return ExplorePage(
            releases = cardsOf(data.optJSONArray("releases"), "album"),
            genres = cardsOf(data.optJSONArray("genres"), "genre"),
            trending = tracksOf(data, "trending"),
            playlists = cardsOf(data.optJSONArray("chartPlaylists"), "playlist"),
        )
    }

    fun search(query: String): SearchPage {
        val data = get("/api/catalog/deezer/search?q=${encode(query)}")
        val artist = data.optJSONObject("artist")
        val focusId = artist?.str("id")?.ifBlank { null }
        return SearchPage(
            artists = cardsOf(data.optJSONArray("artists"), "artist"),
            albums = cardsOf(data.optJSONArray("albums"), "album"),
            tracks = tracksOf(data),
            focusArtistId = focusId,
            focusArtistName = artist?.str("name").orEmpty(),
            focusArtistPicture = artist?.str("picture").orEmpty(),
        )
    }

    fun open(kind: String, id: String): CollectionPage {
        val data = get(
            when (kind) {
                "artist" -> "/api/catalog/deezer/artists/$id"
                "album" -> "/api/catalog/deezer/albums/$id"
                "playlist" -> "/api/catalog/deezer/playlists/$id"
                "genre" -> "/api/catalog/deezer/genres/$id"
                else -> error("Tipo de catálogo desconhecido")
            },
        )
        return when (kind) {
            "artist" -> {
                val artist = data.optJSONObject("artist")
                CollectionPage(
                    title = artist?.str("name") ?: "Artista",
                    cover = artist?.str("picture").orEmpty(),
                    tracks = tracksOf(data),
                    cards = cardsOf(data.optJSONArray("albums"), "album"),
                    kind = "artist",
                    id = id,
                )
            }
            "album" -> {
                val album = data.optJSONObject("album")
                CollectionPage(
                    title = album?.str("title") ?: "Álbum",
                    subtitle = album?.str("artist").orEmpty(),
                    cover = album?.str("picture").orEmpty(),
                    tracks = tracksOf(data),
                    kind = "album",
                    id = id,
                )
            }
            "playlist" -> {
                val playlist = data.optJSONObject("playlist")
                CollectionPage(
                    title = playlist?.str("title") ?: "Playlist",
                    cover = playlist?.str("picture").orEmpty(),
                    tracks = tracksOf(data),
                    kind = "playlist",
                    id = id,
                )
            }
            else -> {
                val genre = data.optJSONObject("genre")
                CollectionPage(
                    title = genre?.str("name") ?: "Gênero",
                    cover = genre?.str("picture").orEmpty(),
                    tracks = tracksOf(data),
                    cards = cardsOf(data.optJSONArray("playlists"), "playlist"),
                    kind = "genre",
                    id = id,
                )
            }
        }
    }

    fun relatedArtists(artistId: String): List<CatalogCard> {
        val data = get("/api/catalog/deezer/artists/$artistId/related")
        return cardsOf(data.optJSONArray("artists"), "artist")
    }

    fun artistRadio(artistId: String): List<Track> {
        return tracksOf(get("/api/catalog/deezer/artists/$artistId/radio"))
    }

    /** Resolve a faixa no catálogo e garante o arquivo de áudio no servidor. */
    fun prepare(track: Track): Track {
        if (track.streamPath?.contains("/api/downloads/") == true) return track
        val withVideo = if (track.videoId.isNullOrBlank()) resolve(track) else track
        val videoId = withVideo.videoId ?: throw ApiException("Faixa sem áudio")
        val saved = post("/api/download/$videoId", withVideo.payload())
        val path = saved.str("url")
        if (path.isBlank()) throw ApiException("O servidor não devolveu o áudio")
        return withVideo.copy(
            videoId = saved.str("videoId").ifBlank { videoId },
            streamPath = path,
            thumbnailUrl = saved.str("thumbnailUrl").ifBlank { withVideo.thumbnailUrl },
        )
    }

    fun addToLibrary(track: Track): Track {
        val ready = if (track.videoId.isNullOrBlank()) resolve(track) else track
        val videoId = ready.videoId ?: throw ApiException("Faixa sem áudio")
        post("/api/library/$videoId", ready.payload())
        return ready
    }

    fun removeFromLibrary(videoId: String) {
        delete("/api/library/$videoId")
    }

    fun recordPlay(track: Track) {
        val videoId = track.videoId ?: return
        runCatching {
            post(
                "/api/me/plays",
                JSONObject()
                    .put("videoId", videoId)
                    .put("title", track.title)
                    .put("artist", track.artist),
            )
        }
    }

    private fun resolve(track: Track): Track {
        val body = JSONObject().put("title", track.title)
        track.deezerId?.let { body.put("deezerId", it) }
        if (track.artist.isNotBlank()) body.put("artist", track.artist)
        if (track.album.isNotBlank()) body.put("album", track.album)
        if (track.genre.isNotBlank()) body.put("genre", track.genre)
        if (track.duration.isNotBlank()) body.put("duration", track.duration)
        if (track.thumbnailUrl.isNotBlank()) body.put("thumbnailUrl", track.thumbnailUrl)
        val found = post("/api/catalog/deezer/resolve", body)
        val videoId = found.str("videoId")
        if (videoId.isBlank()) throw ApiException("Não achei um áudio compatível com esta faixa.")
        return track.copy(videoId = videoId, catalogSource = "deezer")
    }

    private fun Track.payload(): JSONObject {
        val body = JSONObject()
        fun put(key: String, value: String?) {
            if (!value.isNullOrBlank()) body.put(key, value)
        }
        put("title", title)
        put("artist", artist)
        put("artistId", artistId)
        put("album", album)
        put("albumId", albumId)
        put("deezerId", deezerId)
        put("genre", genre)
        put("catalogSource", catalogSource)
        put("duration", duration)
        put("thumbnailUrl", thumbnailUrl)
        return body
    }

    private fun get(path: String) = call(Request.Builder().url(api(path)).get().build())

    private fun post(path: String, body: JSONObject) = call(
        Request.Builder().url(api(path)).post(body.toString().toRequestBody(jsonType)).build(),
    )

    private fun put(path: String, body: JSONObject) = call(
        Request.Builder().url(api(path)).put(body.toString().toRequestBody(jsonType)).build(),
    )

    private fun delete(path: String) {
        call(Request.Builder().url(api(path)).delete().build())
    }

    private fun call(request: Request): JSONObject {
        http.newCall(request).execute().use { response ->
            val text = response.body?.string().orEmpty()
            if (response.code == 401) throw ApiException("Faça login para continuar", 401)
            if (!response.isSuccessful) throw ApiException(errorMessage(text, response.code), response.code)
            if (text.isBlank()) return JSONObject()
            return runCatching { JSONObject(text) }.getOrElse {
                throw ApiException("Resposta inválida do servidor")
            }
        }
    }

    private fun api(path: String): String {
        val normalized = if (path.startsWith("/")) path else "/$path"
        return origin + prefix + normalized
    }

    private fun encode(value: String) = java.net.URLEncoder.encode(value, Charsets.UTF_8.name())

    private fun errorMessage(body: String, code: Int): String {
        val json = runCatching { JSONObject(body) }.getOrNull() ?: return "Erro $code"
        return when (val detail = json.opt("detail")) {
            is String -> detail.ifBlank { "Erro $code" }
            is JSONArray -> buildString {
                for (i in 0 until detail.length()) {
                    val item = detail.opt(i)
                    append(if (item is JSONObject) item.optString("msg") else item?.toString().orEmpty())
                    if (i < detail.length() - 1) append(", ")
                }
            }.ifBlank { "Erro $code" }
            else -> "Erro $code"
        }
    }

    private fun playlistsOf(arr: JSONArray?): List<UserPlaylist> {
        if (arr == null) return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                val id = obj.str("id")
                val title = obj.str("title")
                if (id.isBlank() || title.isBlank()) continue
                add(UserPlaylist(id, title, tracksOf(obj, "tracks")))
            }
        }
    }

    private fun collectionsOf(arr: JSONArray?): List<SavedCollection> {
        if (arr == null) return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                val id = obj.str("id")
                val title = obj.str("title")
                val kind = obj.str("kind")
                if (id.isBlank() || title.isBlank() || kind.isBlank()) continue
                add(SavedCollection(kind, id, title, obj.str("picture"), obj.str("subtitle")))
            }
        }
    }

    private fun tracksOf(data: JSONObject, key: String = "items"): List<Track> {
        val arr = data.optJSONArray(key) ?: data.optJSONArray("tracks") ?: return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                add(obj.toTrack())
            }
        }
    }

    private fun shelvesOf(arr: JSONArray?): List<NamedShelf> {
        if (arr == null) return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                val title = obj.str("title")
                val cards = cardsOf(obj.optJSONArray("cards"), "playlist")
                if (title.isNotBlank() && cards.isNotEmpty()) add(NamedShelf(title, cards))
            }
        }
    }

    private fun cardsOf(arr: JSONArray?, kind: String): List<CatalogCard> {
        if (arr == null) return emptyList()
        return buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                val id = obj.str("id")
                val title = obj.str("title").ifBlank { obj.str("name") }
                if (id.isBlank() || title.isBlank()) continue
                add(
                    CatalogCard(
                        kind = obj.str("kind").ifBlank { kind },
                        id = id,
                        title = title,
                        picture = obj.str("picture"),
                        subtitle = obj.str("subtitle"),
                    ),
                )
            }
        }
    }

    private fun JSONObject.toTrack() = Track(
        videoId = str("videoId").ifBlank { null },
        deezerId = str("deezerId").ifBlank { null },
        title = str("title").ifBlank { "Faixa" },
        artist = str("artist"),
        album = str("album"),
        genre = str("genre"),
        duration = str("duration"),
        thumbnailUrl = str("thumbnailUrl"),
        streamPath = str("url").ifBlank { null },
        artistId = str("artistId").ifBlank { null },
        albumId = str("albumId").ifBlank { null },
        catalogSource = str("catalogSource").ifBlank { "deezer" },
    )

    private fun JSONObject.str(key: String): String {
        if (!has(key) || isNull(key)) return ""
        val value = get(key)
        return when (value) {
            is Double -> if (value % 1.0 == 0.0) value.toLong().toString() else value.toString()
            else -> value.toString()
        }
    }
}
