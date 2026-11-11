package dev.ruts.rutsfy.data

data class Track(
    val videoId: String? = null,
    val deezerId: String? = null,
    val title: String = "",
    val artist: String = "",
    val album: String = "",
    val genre: String = "",
    val duration: String = "",
    val thumbnailUrl: String = "",
    val streamPath: String? = null,
    val artistId: String? = null,
    val albumId: String? = null,
    val catalogSource: String = "deezer",
) {
    val key: String get() = videoId ?: deezerId ?: "$title|$artist"
}

data class CatalogCard(
    val kind: String,
    val id: String,
    val title: String,
    val picture: String = "",
    val subtitle: String = "",
)

data class NamedShelf(
    val title: String,
    val cards: List<CatalogCard> = emptyList(),
)

data class HomeFeed(
    val listenAgain: List<CatalogCard> = emptyList(),
    val shelves: List<NamedShelf> = emptyList(),
    val albumsForYou: List<CatalogCard> = emptyList(),
    val hitsToday: List<CatalogCard> = emptyList(),
    val featuredPlaylists: List<CatalogCard> = emptyList(),
    val newReleases: List<CatalogCard> = emptyList(),
)

data class ExplorePage(
    val releases: List<CatalogCard> = emptyList(),
    val genres: List<CatalogCard> = emptyList(),
    val trending: List<Track> = emptyList(),
    val playlists: List<CatalogCard> = emptyList(),
)

data class SearchPage(
    val artists: List<CatalogCard> = emptyList(),
    val albums: List<CatalogCard> = emptyList(),
    val tracks: List<Track> = emptyList(),
    val focusArtistId: String? = null,
    val focusArtistName: String = "",
    val focusArtistPicture: String = "",
)

data class CollectionPage(
    val title: String,
    val subtitle: String = "",
    val cover: String = "",
    val tracks: List<Track> = emptyList(),
    val cards: List<CatalogCard> = emptyList(),
    val kind: String = "",
    val id: String = "",
)

data class AppUpdate(
    val versionCode: Int,
    val versionName: String,
    val url: String,
)

data class UserPlaylist(
    val id: String,
    val title: String,
    val tracks: List<Track> = emptyList(),
)

data class SavedCollection(
    val kind: String,
    val id: String,
    val title: String,
    val picture: String = "",
    val subtitle: String = "",
)

class ApiException(message: String, val code: Int = 0) : Exception(message)
