package dev.ruts.rutsfy.ui

import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.offset
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntOffset
import kotlin.math.roundToInt
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.DownloadDone
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material.icons.filled.SkipPrevious
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import dev.ruts.rutsfy.AppViewModel
import dev.ruts.rutsfy.DOWNLOADED_ARTIST
import dev.ruts.rutsfy.MainTab
import dev.ruts.rutsfy.UiState
import dev.ruts.rutsfy.data.CatalogCard
import dev.ruts.rutsfy.data.Track
import dev.ruts.rutsfy.player.DownloadsState
import dev.ruts.rutsfy.player.NowPlaying
import kotlinx.coroutines.delay
import java.util.Calendar

private val ScreenLoadingSize = 36.dp
private val ScreenLoadingStroke = 3.dp

@Composable
private fun CenterScreenLoading(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator(
            color = Accent,
            strokeWidth = ScreenLoadingStroke,
            modifier = Modifier.size(ScreenLoadingSize),
        )
    }
}

@Composable
fun RutsApp(viewModel: AppViewModel) {
    val ui by viewModel.ui.collectAsState()
    val now by viewModel.now.collectAsState()
    var playerOpen by remember { mutableStateOf(false) }

    if (ui.booting) {
        Box(Modifier.fillMaxSize().background(BgBase), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("RutsFy", color = TextMain, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(22.dp))
                CircularProgressIndicator(
                    color = Accent,
                    strokeWidth = ScreenLoadingStroke,
                    modifier = Modifier.size(ScreenLoadingSize),
                )
                UpdateBanner(ui.updateMessage)
            }
        }
        return
    }
    if (!ui.loggedIn) {
        LoginScreen(ui, viewModel)
        return
    }

    val playbackBusy = !playerOpen && (
        now.status.isNotBlank() ||
            (now.loadingKey != null && (now.track == null || now.track?.key != now.loadingKey))
        )
    val showScreenLoading = !playerOpen && (ui.loading || ui.catalogLoading || playbackBusy)

    Box(Modifier.fillMaxSize()) {
    Column(
        Modifier
            .fillMaxSize()
            .background(BgBase)
            .windowInsetsPadding(WindowInsets.statusBars),
    ) {
        if (!playerOpen) {
            TopSearch(ui, viewModel)
        }
        UpdateBanner(ui.updateMessage)
        Box(Modifier.weight(1f)) {
            when {
                ui.query.isNotBlank() && (ui.searchOnTop || ui.stack.isEmpty()) -> SearchResults(ui, viewModel)
                ui.stack.isNotEmpty() -> CollectionScreen(ui.stack.last().page, ui, viewModel)
                else -> when (ui.tab) {
                    MainTab.Library -> LibraryScreen(ui, viewModel)
                    MainTab.Explore -> ExploreScreen(ui, viewModel)
                    MainTab.History -> HistoryScreen(ui, viewModel)
                }
            }
            if (playerOpen && now.track != null) {
                FullPlayer(now, ui, viewModel) { playerOpen = false }
            }
        }
        if (ui.message.isNotBlank() && !playerOpen) {
            Text(
                ui.message,
                color = TextSub,
                fontSize = 13.sp,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
            )
        }
        if (!playerOpen && now.track != null) {
            MiniPlayer(now, ui, viewModel) { playerOpen = true }
        }
        BottomTabs(
            ui,
            Modifier.windowInsetsPadding(WindowInsets.navigationBars),
            onLibrary = {
                playerOpen = false
                viewModel.selectTab(MainTab.Library)
            },
            onExplore = {
                playerOpen = false
                viewModel.selectTab(MainTab.Explore)
            },
            onHistory = {
                playerOpen = false
                viewModel.selectTab(MainTab.History)
            },
        )
    }
    val target = ui.saveTarget
    if (target != null) {
        SavePicker(target, ui, viewModel)
    }
    if (showScreenLoading) {
        CenterScreenLoading(
            Modifier
                .matchParentSize()
                .background(Color.Black.copy(alpha = 0.35f))
                .clickable(
                    indication = null,
                    interactionSource = remember { MutableInteractionSource() },
                    onClick = {},
                ),
        )
    }
    }
}

@Composable
private fun UpdateBanner(message: String) {
    if (message.isBlank()) return
    Text(
        message,
        color = TextMain,
        fontSize = 13.sp,
        modifier = Modifier
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .fillMaxWidth(),
    )
}

@Composable
private fun SavePicker(track: Track, ui: UiState, viewModel: AppViewModel) {
    val inLibrary = track.videoId != null && track.videoId in ui.libraryIds
    Box(Modifier.fillMaxSize()) {
        Box(
            Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.55f))
                .clickable(onClick = viewModel::dismissSave),
        )
        Column(
            Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .clip(RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp))
                .background(BgElevated)
                .windowInsetsPadding(WindowInsets.navigationBars)
                .padding(bottom = 12.dp),
        ) {
            Text("Salvar em", color = TextMain, fontWeight = FontWeight.Bold, fontSize = 18.sp, modifier = Modifier.padding(start = 16.dp, top = 16.dp, bottom = 8.dp))
            SaveChoice("Músicas salvas", inLibrary) { viewModel.saveTrackIn(track, null) }
            ui.userPlaylists.forEach { playlist ->
                val inside = playlist.tracks.any { song ->
                    (!track.videoId.isNullOrBlank() && track.videoId == song.videoId) ||
                        (!track.deezerId.isNullOrBlank() && track.deezerId == song.deezerId) ||
                        track.key == song.key
                }
                SaveChoice(playlist.title, inside) { viewModel.saveTrackIn(track, playlist.id) }
            }
        }
    }
}

@Composable
private fun SaveChoice(label: String, selected: Boolean, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().clickable(onClick = onClick).padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = if (selected) Accent else TextMain, fontSize = 16.sp, modifier = Modifier.weight(1f))
        if (selected) Icon(Icons.Filled.Check, contentDescription = null, tint = Accent)
    }
}

@Composable
private fun LoginScreen(ui: UiState, viewModel: AppViewModel) {
    var nickname by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var register by remember { mutableStateOf(false) }
    Box(
        Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.78f)).windowInsetsPadding(WindowInsets.statusBars),
        contentAlignment = Alignment.Center,
    ) {
        if (ui.loading) {
            CenterScreenLoading(Modifier.matchParentSize().background(Color.Black.copy(alpha = 0.35f)))
        }
        Column(
            Modifier
                .padding(24.dp)
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(BgElevated)
                .padding(horizontal = 28.dp, vertical = 32.dp),
        ) {
            Text(
                "RutsFy",
                modifier = Modifier.fillMaxWidth(),
                color = TextMain,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            )
            Spacer(Modifier.height(12.dp))
            Text(
                if (register) "Criar conta" else "Entrar no RutsFy",
                color = TextMain,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = (-0.5).sp,
                modifier = Modifier.fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            )
            Text(
                "Sua biblioteca, recentes e sessão ficam na sua conta.",
                color = TextSub,
                fontSize = 15.sp,
                modifier = Modifier.padding(top = 8.dp, bottom = 20.dp).fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            )
            UpdateBanner(ui.updateMessage)
            Row(Modifier.fillMaxWidth()) {
                AuthTab("Entrar", !register, Modifier.weight(1f)) { register = false }
                AuthTab("Criar conta", register, Modifier.weight(1f)) { register = true }
            }
            Spacer(Modifier.height(16.dp))
            FieldLabel("Apelido")
            SiteField(nickname, { nickname = it })
            Spacer(Modifier.height(14.dp))
            FieldLabel("Senha")
            SiteField(password, { password = it }, password = true)
            if (ui.message.isNotBlank()) {
                Text(ui.message, color = Color(0xFFFFB199), fontSize = 14.sp, modifier = Modifier.padding(top = 12.dp))
            }
            Spacer(Modifier.height(16.dp))
            Box(
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(500.dp))
                    .background(if (ui.loading) Accent.copy(alpha = 0.55f) else Accent)
                    .clickable(enabled = !ui.loading && nickname.isNotBlank() && password.isNotBlank()) {
                        viewModel.login(nickname, password, register)
                    }
                    .padding(vertical = 14.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(if (register) "Criar conta" else "Entrar", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp)
            }
        }
    }
}

@Composable
private fun AuthTab(label: String, active: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Column(modifier.clickable(onClick = onClick), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, color = if (active) TextMain else TextSub, fontWeight = FontWeight.Bold, fontSize = 14.sp, modifier = Modifier.padding(vertical = 10.dp))
        Box(Modifier.fillMaxWidth().height(2.dp).background(if (active) Accent else Color.Transparent))
    }
}

@Composable
private fun FieldLabel(text: String) {
    Text(text, color = TextSub, fontSize = 13.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 6.dp))
}

@Composable
private fun SiteField(value: String, onChange: (String) -> Unit, password: Boolean = false) {
    BasicTextField(
        value = value,
        onValueChange = onChange,
        singleLine = true,
        textStyle = TextStyle(color = TextMain, fontSize = 15.sp),
        cursorBrush = SolidColor(TextMain),
        visualTransformation = if (password) PasswordVisualTransformation() else VisualTransformation.None,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(4.dp))
            .background(BgHighlight)
            .padding(horizontal = 14.dp, vertical = 12.dp),
    )
}

@Composable
private fun TopSearch(ui: UiState, viewModel: AppViewModel) {
    var menu by remember { mutableStateOf(false) }
    LaunchedEffect(menu) {
        if (menu) viewModel.refreshAppVersion()
    }
    val focus = remember { MutableInteractionSource() }
    val focused by focus.collectIsFocusedAsState()
    val fieldBg = if (focused) Color.White else BgHighlight
    val fieldFg = if (focused) Color.Black else TextMain
    Row(
        Modifier.fillMaxWidth().height(56.dp).padding(horizontal = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(
            Modifier
                .weight(1f)
                .clip(RoundedCornerShape(500.dp))
                .background(fieldBg)
                .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Filled.Search, contentDescription = null, tint = if (focused) Color.Black else TextSub, modifier = Modifier.size(22.dp))
            Spacer(Modifier.width(10.dp))
            BasicTextField(
                value = ui.query,
                onValueChange = viewModel::setQuery,
                singleLine = true,
                interactionSource = focus,
                textStyle = TextStyle(color = fieldFg, fontSize = 16.sp),
                cursorBrush = SolidColor(fieldFg),
                modifier = Modifier.fillMaxWidth(),
                decorationBox = { inner ->
                    if (ui.query.isEmpty()) {
                        Text("O que você quer ouvir?", color = if (focused) TextMuted else TextSub, fontSize = 16.sp)
                    }
                    inner()
                },
            )
        }
        Spacer(Modifier.width(8.dp))
        Box {
            Box(
                Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(BgHighlight)
                    .clickable { menu = true },
                contentAlignment = Alignment.Center,
            ) {
                Text(ui.nickname.take(1).uppercase(), color = TextMain, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            }
            DropdownMenu(expanded = menu, onDismissRequest = { menu = false }) {
                val versionLabel = ui.installedVersionName.ifBlank { "—" }
                DropdownMenuItem(
                    text = { Text("Versão $versionLabel", color = TextSub) },
                    onClick = {},
                    enabled = false,
                )
                if (ui.updateAvailable) {
                    val target = ui.remoteVersionName.ifBlank { ui.remoteVersionCode.toString() }
                    DropdownMenuItem(
                        text = {
                            Text(
                                if (ui.updateBusy) "Baixando $target…" else "Atualizar para $target",
                                color = Accent,
                            )
                        },
                        onClick = {
                            menu = false
                            viewModel.downloadAndInstallUpdate()
                        },
                        enabled = !ui.updateBusy,
                    )
                } else if (ui.remoteVersionCode > 0) {
                    DropdownMenuItem(
                        text = { Text("App atualizado", color = TextSub) },
                        onClick = {},
                        enabled = false,
                    )
                }
                DropdownMenuItem(
                    text = { Text("Sair") },
                    onClick = {
                        menu = false
                        viewModel.logout()
                    },
                )
            }
        }
    }
}

@Composable
private fun BottomTabs(
    ui: UiState,
    modifier: Modifier = Modifier,
    onLibrary: () -> Unit,
    onExplore: () -> Unit,
    onHistory: () -> Unit,
) {
    Row(
        modifier.fillMaxWidth().background(BgElevated).padding(top = 6.dp, bottom = 6.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
    ) {
        TabButton("Biblioteca", Icons.Filled.Bookmark, ui.tab == MainTab.Library && ui.stack.isEmpty() && ui.query.isBlank(), onLibrary)
        TabButton("Explorar", Icons.Filled.Star, ui.tab == MainTab.Explore && ui.stack.isEmpty() && ui.query.isBlank(), onExplore)
        TabButton("Recentes", Icons.Filled.History, ui.tab == MainTab.History && ui.stack.isEmpty() && ui.query.isBlank(), onHistory)
    }
}

@Composable
private fun TabButton(label: String, icon: ImageVector, active: Boolean, onClick: () -> Unit) {
    Column(
        Modifier.width(88.dp).clip(RoundedCornerShape(8.dp)).clickable(onClick = onClick).padding(vertical = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(icon, contentDescription = label, tint = if (active) TextMain else TextSub, modifier = Modifier.size(22.dp))
        Text(label, color = if (active) TextMain else TextSub, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun LibraryScreen(ui: UiState, viewModel: AppViewModel) {
    var creating by remember { mutableStateOf(false) }
    var playlistName by remember { mutableStateOf("") }
    val mine = buildList {
        ui.userPlaylists.forEach { playlist ->
            add(CatalogCard(
                kind = "user",
                id = playlist.id,
                title = playlist.title,
                picture = playlist.tracks.firstOrNull()?.thumbnailUrl.orEmpty(),
                subtitle = "Playlist",
            ))
        }
        ui.savedCollections.forEach { item ->
            add(CatalogCard(item.kind, item.id, item.title, item.picture, item.subtitle))
        }
    }
    LazyColumn(contentPadding = PaddingValues(bottom = 16.dp)) {
        item {
            Text("Biblioteca", color = TextMain, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 16.dp, top = 8.dp))
            Text(
                "${greeting()} · o que combina com o que você ouve.",
                color = TextSub,
                fontSize = 14.sp,
                modifier = Modifier.padding(start = 16.dp, top = 4.dp, bottom = 8.dp),
            )
            Row(
                Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, top = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("Minhas playlists", color = TextMain, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                Text(
                    "Criar",
                    color = TextMain,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .clip(RoundedCornerShape(500.dp))
                        .background(BgHighlight)
                        .clickable { creating = true }
                        .padding(horizontal = 14.dp, vertical = 8.dp),
                )
            }
        }
        item {
            Shelf("", mine, viewModel) { card ->
                if (card.kind == "user") viewModel.openUserPlaylist(card.id) else viewModel.open(card)
            }
        }
        item {
            val downloads by viewModel.downloads.collectAsState()
            val cards = remember(downloads) { downloadedCards(downloads) }
            Shelf("Baixadas", cards, viewModel) { card ->
                if (card.kind == DOWNLOADED_ARTIST) {
                    viewModel.openDownloadedArtist(card.id)
                } else {
                    viewModel.openDownloadedCollection(card.kind, card.id)
                }
            }
        }
        if (ui.home.listenAgain.isNotEmpty()) {
            item {
                Shelf("Ouvir de novo", ui.home.listenAgain, viewModel) { card ->
                    viewModel.setQuery(card.title)
                }
            }
        }
        items(ui.home.shelves) { shelf -> Shelf(shelf.title, shelf.cards, viewModel) }
        item { Shelf("Álbuns para você", ui.home.albumsForYou, viewModel) }
        item { Shelf("Hits de hoje", ui.home.hitsToday, viewModel) }
        item { Shelf("Playlists em destaque para você", ui.home.featuredPlaylists, viewModel) }
        item { Shelf("Novidades", ui.home.newReleases, viewModel) }
        item {
            Text("Músicas salvas", color = TextMain, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 16.dp, top = 18.dp))
            Text(
                if (ui.library.isEmpty()) "Nada salvo ainda." else "${ui.library.size} faixas",
                color = TextSub,
                fontSize = 13.sp,
                modifier = Modifier.padding(start = 16.dp, top = 4.dp, bottom = 8.dp),
            )
        }
        itemsIndexed(ui.library) { index, track ->
            TrackRow(track, saved = true, viewModel = viewModel, onPlay = { viewModel.play(ui.library, index) }) { viewModel.promptSave(track) }
        }
    }
    if (creating) {
        AlertDialog(
            onDismissRequest = { creating = false },
            containerColor = BgElevated,
            title = { Text("Nova playlist", color = TextMain) },
            text = {
                BasicTextField(
                    value = playlistName,
                    onValueChange = { playlistName = it },
                    singleLine = true,
                    textStyle = TextStyle(color = TextMain, fontSize = 16.sp),
                    cursorBrush = SolidColor(TextMain),
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(4.dp)).background(BgHighlight).padding(horizontal = 14.dp, vertical = 12.dp),
                )
            },
            confirmButton = {
                Text(
                    "Criar",
                    color = Accent,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.clickable {
                        viewModel.createPlaylist(playlistName)
                        playlistName = ""
                        creating = false
                    }.padding(8.dp),
                )
            },
            dismissButton = {
                Text("Cancelar", color = TextSub, modifier = Modifier.clickable { creating = false }.padding(8.dp))
            },
        )
    }
}

@Composable
private fun ExploreScreen(ui: UiState, viewModel: AppViewModel) {
    LazyColumn(contentPadding = PaddingValues(bottom = 16.dp)) {
        item { Shelf("Lançamentos", ui.explore.releases, viewModel) }
        item { Shelf("Momentos e gêneros", ui.explore.genres, viewModel) }
        item { Shelf("Playlists", ui.explore.playlists, viewModel) }
        if (ui.explore.trending.isNotEmpty()) {
            item { SectionTitle("Em alta") }
        }
        itemsIndexed(ui.explore.trending) { index, track ->
            TrackRow(track, ui.libraryIds.contains(track.videoId), viewModel, { viewModel.play(ui.explore.trending, index) }) {
                viewModel.promptSave(track)
            }
        }
    }
}

@Composable
private fun HistoryScreen(ui: UiState, viewModel: AppViewModel) {
    LazyColumn {
        item {
            Text("Recentes", color = TextMain, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 16.dp, top = 8.dp))
            Text("O que você ouviu por último.", color = TextSub, fontSize = 14.sp, modifier = Modifier.padding(start = 16.dp, top = 4.dp, bottom = 8.dp))
        }
        itemsIndexed(ui.history) { index, track ->
            TrackRow(track, ui.libraryIds.contains(track.videoId), viewModel, { viewModel.play(ui.history, index) }) {
                viewModel.promptSave(track)
            }
        }
    }
}

@Composable
private fun SearchResults(ui: UiState, viewModel: AppViewModel) {
    val page = ui.search
    LazyColumn {
        if (ui.query.trim().length < 2) {
            item { Text("Digite para buscar.", color = TextSub, modifier = Modifier.padding(16.dp)) }
        } else if (page == null) {
            item { Text("Buscando…", color = TextSub, modifier = Modifier.padding(16.dp)) }
        } else {
            item { Shelf("Artistas", page.artists, viewModel) }
            item { Shelf("Álbuns", page.albums, viewModel) }
            if (page.tracks.isNotEmpty()) item { SectionTitle("Faixas") }
            itemsIndexed(page.tracks) { index, track ->
                TrackRow(track, ui.libraryIds.contains(track.videoId), viewModel, { viewModel.play(page.tracks, index) }) {
                    viewModel.promptSave(track)
                }
            }
        }
    }
}

@Composable
private fun CollectionScreen(page: dev.ruts.rutsfy.data.CollectionPage, ui: UiState, viewModel: AppViewModel) {
    LazyColumn {
        item {
            Row(Modifier.padding(horizontal = 8.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "← Voltar",
                    color = TextMain,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.clip(RoundedCornerShape(500.dp)).background(BgHighlight).clickable(onClick = viewModel::back).padding(horizontal = 14.dp, vertical = 8.dp),
                )
            }
            if (page.cover.isNotBlank()) {
                AsyncImage(
                    model = page.cover,
                    contentDescription = page.title,
                    modifier = Modifier.padding(horizontal = 16.dp).size(160.dp).clip(RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Crop,
                )
            }
            Text(page.title, color = TextMain, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 16.dp, top = 12.dp))
            if (page.subtitle.isNotBlank()) {
                Text(page.subtitle, color = TextSub, modifier = Modifier.padding(start = 16.dp, top = 4.dp))
            }
            val downloadable = page.kind in setOf("album", "playlist", "user") && page.tracks.isNotEmpty()
            Row(Modifier.padding(start = 16.dp, top = 10.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (page.kind == "album" || page.kind == "playlist") {
                    val saved = ui.savedCollections.any { it.kind == page.kind && it.id == page.id }
                    PillButton(if (saved) "Na biblioteca" else "Salvar", active = saved) {
                        viewModel.toggleSavedCollection(page)
                    }
                }
                if (downloadable) {
                    val downloads by viewModel.downloads.collectAsState()
                    val stored = downloads.collection(page.kind, page.id)
                    val done = stored?.tracks?.count(downloads::isDone) ?: 0
                    val total = stored?.tracks?.size ?: 0
                    val label = when {
                        stored == null -> "Baixar"
                        done < total -> "Baixando $done/$total"
                        else -> "Baixado"
                    }
                    PillButton(label, active = stored != null) { viewModel.toggleDownloadCollection(page) }
                }
            }
        }
        item { Shelf("Mais", page.cards, viewModel) }
        if (page.tracks.isNotEmpty()) {
            item {
                Row(
                    Modifier.padding(start = 8.dp, top = 8.dp).clickable { viewModel.play(page.tracks, 0, page.kind, page.id) },
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    PlayCircle(size = 48.dp)
                    Text("Reproduzir", color = TextMain, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 8.dp))
                }
            }
        }
        itemsIndexed(page.tracks) { index, track ->
            TrackRow(track, ui.libraryIds.contains(track.videoId), viewModel, { viewModel.play(page.tracks, index, page.kind, page.id) }) {
                viewModel.promptSave(track)
            }
        }
    }
}

private fun downloadedCards(state: DownloadsState): List<CatalogCard> {
    val collections = state.collections.map { item ->
        val label = when (item.kind) {
            "album" -> "Álbum"
            "playlist", "user" -> "Playlist"
            else -> ""
        }
        CatalogCard(item.kind, item.id, item.title, item.picture, listOf(label, "${item.tracks.size} músicas").filter { it.isNotBlank() }.joinToString(" · "))
    }
    val artists = state.singles
        .groupBy { it.artist.ifBlank { "Outros" } }
        .map { (artist, tracks) ->
            val count = if (tracks.size == 1) "1 música" else "${tracks.size} músicas"
            CatalogCard(DOWNLOADED_ARTIST, artist, artist, tracks.first().thumbnailUrl, count)
        }
    return collections + artists
}

@Composable
private fun PillButton(label: String, active: Boolean, onClick: () -> Unit) {
    Text(
        label,
        color = if (active) Accent else TextMain,
        fontWeight = FontWeight.Bold,
        modifier = Modifier
            .clip(RoundedCornerShape(500.dp))
            .background(BgHighlight)
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 8.dp),
    )
}

@Composable
private fun SectionTitle(title: String) {
    Text(title, color = TextMain, fontWeight = FontWeight.Bold, fontSize = 20.sp, modifier = Modifier.padding(start = 16.dp, top = 18.dp, bottom = 10.dp))
}

@Composable
private fun Shelf(
    title: String,
    cards: List<CatalogCard>,
    viewModel: AppViewModel,
    onCard: (CatalogCard) -> Unit = { viewModel.open(it) },
) {
    if (cards.isEmpty()) return
    if (title.isNotBlank()) SectionTitle(title)
    LazyRow(contentPadding = PaddingValues(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        items(cards, key = { "${it.kind}:${it.id}:${it.title}" }) { card ->
            val round = card.kind == "artist" || card.kind == DOWNLOADED_ARTIST
            Column(Modifier.width(152.dp).clickable { onCard(card) }) {
                AsyncImage(
                    model = card.picture,
                    contentDescription = card.title,
                    modifier = Modifier
                        .size(152.dp)
                        .clip(if (round) CircleShape else RoundedCornerShape(4.dp))
                        .background(BgHighlight),
                    contentScale = ContentScale.Crop,
                )
                Text(card.title, color = TextMain, fontWeight = FontWeight.Bold, fontSize = 14.sp, maxLines = 2, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(top = 8.dp))
                if (card.subtitle.isNotBlank()) {
                    Text(card.subtitle, color = TextMuted, fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
        }
    }
}

@Composable
private fun TrackRow(track: Track, saved: Boolean, viewModel: AppViewModel, onPlay: () -> Unit, onSave: () -> Unit) {
    val now by viewModel.now.collectAsState()
    val downloads by viewModel.downloads.collectAsState()
    val playing = isPlayingTrack(now.track, track)
    val loading = isLoadingTrack(now.loadingKey, track)
    Row(
        Modifier
            .fillMaxWidth()
            .background(if (playing) BgHighlight else Color.Transparent)
            .clickable(onClick = onPlay)
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        CoverThumb(track.thumbnailUrl, loading, downloaded = downloads.isDone(track))
        Column(Modifier.weight(1f).padding(horizontal = 10.dp)) {
            Text(
                track.title,
                color = if (playing) Accent else TextMain,
                fontSize = 14.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            val meta = listOf(track.artist, formatIso(track.duration)).filter { it.isNotBlank() }.joinToString(" · ")
            if (meta.isNotBlank()) {
                Text(meta, color = TextMuted, fontSize = 10.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
        }
        DownloadButton(
            single = downloads.isSingle(track),
            done = downloads.isDone(track),
            pending = downloads.isPending(track),
        ) { viewModel.toggleDownload(track) }
        Spacer(Modifier.width(8.dp))
        SaveButton(saved, onSave)
    }
}

@Composable
private fun DownloadButton(single: Boolean, done: Boolean, pending: Boolean, onClick: () -> Unit) {
    Box(Modifier.size(28.dp).clip(CircleShape).clickable(onClick = onClick), contentAlignment = Alignment.Center) {
        when {
            pending -> CircularProgressIndicator(color = Accent, strokeWidth = 2.dp, modifier = Modifier.size(18.dp))
            single && done -> Icon(Icons.Filled.DownloadDone, contentDescription = "Remover download", tint = Accent, modifier = Modifier.size(22.dp))
            else -> Icon(Icons.Filled.Download, contentDescription = "Baixar", tint = TextSub, modifier = Modifier.size(22.dp))
        }
    }
}

private fun isPlayingTrack(current: Track?, row: Track): Boolean {
    if (current == null) return false
    val videoId = current.videoId
    if (!videoId.isNullOrBlank() && videoId == row.videoId) return true
    val deezerId = current.deezerId
    if (!deezerId.isNullOrBlank() && deezerId == row.deezerId) return true
    return current.key == row.key
}

private fun isLoadingTrack(loadingKey: String?, row: Track): Boolean {
    if (loadingKey.isNullOrBlank()) return false
    return loadingKey == row.key || loadingKey == row.videoId || loadingKey == row.deezerId
}

@Composable
private fun CoverThumb(
    url: String,
    loading: Boolean,
    size: androidx.compose.ui.unit.Dp = 36.dp,
    downloaded: Boolean = false,
) {
    Box(Modifier.size(size), contentAlignment = Alignment.Center) {
        AsyncImage(
            model = url,
            contentDescription = null,
            modifier = Modifier.matchParentSize().clip(RoundedCornerShape(2.dp)).background(BgHighlight),
            contentScale = ContentScale.Crop,
        )
        if (loading) {
            Box(Modifier.matchParentSize().clip(RoundedCornerShape(2.dp)).background(Color.Black.copy(alpha = 0.45f)))
            CircularProgressIndicator(
                color = Color.White,
                strokeWidth = 2.dp,
                modifier = Modifier.size(size * 0.62f),
            )
        }
        if (downloaded) {
            Box(
                Modifier
                    .align(Alignment.BottomEnd)
                    .offset(x = 3.dp, y = 3.dp)
                    .size(14.dp)
                    .clip(CircleShape)
                    .background(BgBase)
                    .padding(1.5.dp)
                    .clip(CircleShape)
                    .background(Accent),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.Filled.Check, contentDescription = "Baixada", tint = Color.White, modifier = Modifier.size(9.dp))
            }
        }
    }
}

@Composable
private fun SaveButton(saved: Boolean, onClick: () -> Unit) {
    Box(
        Modifier
            .size(28.dp)
            .shadow(2.dp, CircleShape)
            .clip(CircleShape)
            .background(if (saved) Accent else Color.White)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            if (saved) Icons.Filled.Check else Icons.Filled.Add,
            contentDescription = if (saved) "Na biblioteca" else "Salvar",
            tint = if (saved) Color.White else Color(0xFF121212),
            modifier = Modifier.size(16.dp),
        )
    }
}

@Composable
private fun MiniPlayer(now: NowPlaying, ui: UiState, viewModel: AppViewModel, onOpen: () -> Unit) {
    val track = now.track ?: return
    val saved = track.videoId != null && track.videoId in ui.libraryIds
    Column(Modifier.fillMaxWidth().background(BgElevated).padding(horizontal = 10.dp, vertical = 6.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Row(Modifier.weight(1f).clickable(onClick = onOpen), verticalAlignment = Alignment.CenterVertically) {
                AsyncImage(
                    model = track.thumbnailUrl,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp).clip(RoundedCornerShape(4.dp)).background(BgHighlight),
                    contentScale = ContentScale.Crop,
                )
                Column(Modifier.padding(start = 10.dp).weight(1f)) {
                    Text(track.title, color = TextMain, fontSize = 13.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Text(now.status.ifBlank { track.artist }, color = TextMuted, fontSize = 10.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
            SaveButton(saved) { viewModel.promptSave(track) }
            Icon(Icons.Filled.SkipPrevious, contentDescription = "Anterior", tint = TextMain, modifier = Modifier.padding(start = 4.dp).size(36.dp).clickable(onClick = viewModel::previous))
            PlayCircle(size = 36.dp, playing = now.playing, enabled = now.status.isBlank(), onClick = viewModel::togglePlay)
            Icon(Icons.Filled.SkipNext, contentDescription = "Próxima", tint = TextMain, modifier = Modifier.size(36.dp).clickable(onClick = viewModel::next))
        }
        PlayerSeek(viewModel, compact = true)
    }
}

@Composable
private fun FullPlayer(now: NowPlaying, ui: UiState, viewModel: AppViewModel, onClose: () -> Unit) {
    val track = now.track ?: return
    val saved = track.videoId != null && track.videoId in ui.libraryIds
    val density = LocalDensity.current
    var dragY by remember { mutableFloatStateOf(0f) }
    val sheetDrag = Modifier.pointerInput(onClose) {
        val threshold = with(density) { 90.dp.toPx() }
        detectVerticalDragGestures(
            onVerticalDrag = { _, dy ->
                dragY = (dragY + dy).coerceAtLeast(0f)
            },
            onDragEnd = {
                if (dragY > threshold) onClose()
                dragY = 0f
            },
            onDragCancel = { dragY = 0f },
        )
    }
    LazyColumn(
        Modifier
            .offset { IntOffset(0, dragY.roundToInt().coerceAtLeast(0)) }
            .fillMaxSize()
            .background(BgBase),
    ) {
        item {
            Column(sheetDrag.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    Modifier
                        .padding(top = 10.dp)
                        .size(width = 36.dp, height = 4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(Color.White.copy(alpha = 0.35f)),
                )
                Box(Modifier.fillMaxWidth().padding(start = 8.dp, bottom = 4.dp), contentAlignment = Alignment.CenterStart) {
                    Icon(
                        Icons.Filled.KeyboardArrowDown,
                        contentDescription = "Minimizar",
                        tint = TextMain,
                        modifier = Modifier.size(32.dp).clickable(onClick = onClose),
                    )
                }
                AsyncImage(
                    model = track.thumbnailUrl,
                    contentDescription = track.title,
                    modifier = Modifier
                        .padding(top = 8.dp)
                        .size(280.dp)
                        .shadow(16.dp, RoundedCornerShape(8.dp))
                        .clip(RoundedCornerShape(8.dp))
                        .background(BgHighlight),
                    contentScale = ContentScale.Crop,
                )
            }
        }
        item {
            Row(
                Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 20.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(track.title, color = TextMain, fontSize = 22.sp, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    if (track.artist.isNotBlank()) {
                        Text(track.artist, color = TextSub, fontSize = 15.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                    if (now.status.isNotBlank()) {
                        Text(now.status, color = TextMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 4.dp))
                    }
                }
                SaveButton(saved) { viewModel.promptSave(track) }
            }
        }
        item {
            Column(Modifier.padding(horizontal = 20.dp)) {
                Spacer(Modifier.height(8.dp))
                PlayerSeek(viewModel, compact = false)
                Row(
                    Modifier.fillMaxWidth().padding(top = 8.dp, bottom = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(Icons.Filled.SkipPrevious, contentDescription = "Anterior", tint = TextMain, modifier = Modifier.size(44.dp).clickable(onClick = viewModel::previous))
                    PlayCircle(size = 60.dp, playing = now.playing, enabled = now.status.isBlank(), onClick = viewModel::togglePlay)
                    Icon(Icons.Filled.SkipNext, contentDescription = "Próxima", tint = TextMain, modifier = Modifier.size(44.dp).clickable(onClick = viewModel::next))
                }
            }
        }
        item {
            Column(Modifier.fillMaxWidth().padding(top = 8.dp)) {
                Box(
                    Modifier
                        .padding(top = 10.dp)
                        .align(Alignment.CenterHorizontally)
                        .size(width = 40.dp, height = 4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(Color.White.copy(alpha = 0.25f)),
                )
                Text(
                    "Sua fila aparece aqui.",
                    color = TextSub,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(start = 16.dp, top = 12.dp, bottom = 8.dp),
                )
            }
        }
        itemsIndexed(now.queue) { index, row ->
            val downloads by viewModel.downloads.collectAsState()
            val current = index == now.index
            val loading = isLoadingTrack(now.loadingKey, row)
            Row(
                Modifier
                    .fillMaxWidth()
                    .background(if (current) BgHighlight else Color.Transparent)
                    .clickable { viewModel.play(now.queue, index, keepContinuation = true) }
                    .padding(horizontal = 12.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                CoverThumb(row.thumbnailUrl, loading, downloaded = downloads.isDone(row))
                Column(Modifier.weight(1f).padding(horizontal = 10.dp)) {
                    Text(
                        row.title,
                        color = if (current) Accent else TextMain,
                        fontSize = 14.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                    val meta = listOf(row.artist, formatIso(row.duration)).filter { it.isNotBlank() }.joinToString(" · ")
                    if (meta.isNotBlank()) {
                        Text(meta, color = TextMuted, fontSize = 10.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                }
            }
        }
    }
}

@Composable
private fun PlayCircle(size: androidx.compose.ui.unit.Dp, playing: Boolean = false, enabled: Boolean = true, onClick: (() -> Unit)? = null) {
    Box(
        Modifier
            .size(size)
            .clip(CircleShape)
            .background(Color.White)
            .then(if (onClick != null && enabled) Modifier.clickable(onClick = onClick) else Modifier),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            if (playing) Icons.Filled.Pause else Icons.Filled.PlayArrow,
            contentDescription = "Tocar",
            tint = Color(0xFF121212),
            modifier = Modifier.size(size * 0.55f),
        )
    }
}

@Composable
private fun PlayerSeek(viewModel: AppViewModel, compact: Boolean) {
    var position by remember { mutableLongStateOf(0L) }
    var duration by remember { mutableLongStateOf(0L) }
    var seeking by remember { mutableStateOf(false) }
    var fraction by remember { mutableFloatStateOf(0f) }
    LaunchedEffect(Unit) {
        while (true) {
            if (!seeking) {
                position = viewModel.positionMs()
                duration = viewModel.durationMs().coerceAtLeast(0L)
            }
            delay(200)
        }
    }
    val progress = if (seeking) {
        fraction
    } else if (duration > 0L) {
        (position.toFloat() / duration.toFloat()).coerceIn(0f, 1f)
    } else {
        0f
    }
    val shown = if (seeking && duration > 0L) (fraction * duration).toLong() else position
    Row(
        Modifier.fillMaxWidth().padding(top = if (compact) 2.dp else 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            formatMs(shown),
            color = TextSub,
            fontSize = 11.sp,
            modifier = Modifier.width(36.dp),
        )
        BoxWithConstraints(
            Modifier
                .weight(1f)
                .height(16.dp)
                .pointerInput(duration) {
                    fun at(x: Float): Float = (x / size.width.coerceAtLeast(1).toFloat()).coerceIn(0f, 1f)
                    detectTapGestures { offset ->
                        val next = at(offset.x)
                        fraction = next
                        if (duration > 0L) viewModel.seekTo((next * duration).toLong())
                    }
                }
                .pointerInput(duration) {
                    detectHorizontalDragGestures(
                        onDragStart = { start ->
                            seeking = true
                            fraction = (start.x / size.width.coerceAtLeast(1).toFloat()).coerceIn(0f, 1f)
                        },
                        onHorizontalDrag = { change, _ ->
                            fraction = (change.position.x / size.width.coerceAtLeast(1).toFloat()).coerceIn(0f, 1f)
                            change.consume()
                        },
                        onDragEnd = {
                            if (duration > 0L) viewModel.seekTo((fraction * duration).toLong())
                            seeking = false
                        },
                        onDragCancel = { seeking = false },
                    )
                },
        ) {
            val thumb = 12.dp
            val travel = (maxWidth - thumb).coerceAtLeast(0.dp)
            Box(
                Modifier
                    .align(Alignment.CenterStart)
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(Color.White.copy(alpha = 0.35f)),
            )
            Box(
                Modifier
                    .align(Alignment.CenterStart)
                    .fillMaxWidth(progress.coerceIn(0f, 1f))
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(Accent),
            )
            Box(
                Modifier
                    .align(Alignment.CenterStart)
                    .offset(x = travel * progress.coerceIn(0f, 1f))
                    .size(thumb)
                    .clip(CircleShape)
                    .background(Accent),
            )
        }
        Text(
            formatMs(duration),
            color = TextSub,
            fontSize = 11.sp,
            modifier = Modifier.width(36.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.End,
        )
    }
}

private fun greeting(): String {
    val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
    return when {
        hour in 5..11 -> "Bom dia"
        hour in 12..17 -> "Boa tarde"
        else -> "Boa noite"
    }
}

private fun formatMs(ms: Long): String {
    if (ms <= 0) return "0:00"
    val total = ms / 1000
    return "%d:%02d".format(total / 60, total % 60)
}

private fun formatIso(duration: String): String {
    if (duration.isBlank()) return ""
    val hours = Regex("(\\d+)H").find(duration)?.groupValues?.get(1)?.toIntOrNull() ?: 0
    val minutes = Regex("(\\d+)M").find(duration)?.groupValues?.get(1)?.toIntOrNull() ?: 0
    val seconds = Regex("(\\d+)S").find(duration)?.groupValues?.get(1)?.toIntOrNull() ?: 0
    return if (hours > 0) "%d:%02d:%02d".format(hours, minutes, seconds) else "%d:%02d".format(minutes, seconds)
}
