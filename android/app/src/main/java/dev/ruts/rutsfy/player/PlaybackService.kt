package dev.ruts.rutsfy.player

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.media.app.NotificationCompat.MediaStyle
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.common.ForwardingPlayer
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultDataSource
import androidx.media3.datasource.okhttp.OkHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.session.MediaSession
import androidx.media3.session.MediaSessionService
import dev.ruts.rutsfy.MainActivity
import dev.ruts.rutsfy.R
import dev.ruts.rutsfy.RutsFyApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class PlaybackService : MediaSessionService() {
    private var exo: ExoPlayer? = null
    private var session: MediaSession? = null
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val artwork = mutableMapOf<String, Bitmap>()
    private val artworkMiss = mutableSetOf<String>()
    private var artworkJob = 0

    override fun onCreate() {
        super.onCreate()
        ensureChannel()
        val app = application as RutsFyApp
        val dataSource = DefaultDataSource.Factory(this, OkHttpDataSource.Factory(app.http))
        val player = ExoPlayer.Builder(this)
            .setMediaSourceFactory(DefaultMediaSourceFactory(dataSource))
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(C.USAGE_MEDIA)
                    .setContentType(C.AUDIO_CONTENT_TYPE_MUSIC)
                    .build(),
                true,
            )
            .setHandleAudioBecomingNoisy(true)
            .setWakeMode(C.WAKE_MODE_LOCAL)
            .build()
        exo = player
        app.player.bind(player)
        val transport = Transport(player, app.player)
        val openApp = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        session = MediaSession.Builder(this, transport).setSessionActivity(openApp).build()
        player.addListener(
            object : Player.Listener {
                override fun onEvents(player: Player, events: Player.Events) {
                    if (events.containsAny(
                            Player.EVENT_IS_PLAYING_CHANGED,
                            Player.EVENT_PLAYBACK_STATE_CHANGED,
                            Player.EVENT_MEDIA_ITEM_TRANSITION,
                            Player.EVENT_MEDIA_METADATA_CHANGED,
                        )
                    ) {
                        publishNotification(startInForegroundRequired = player.playWhenReady)
                    }
                }
            },
        )
    }

    override fun onGetSession(controllerInfo: MediaSession.ControllerInfo): MediaSession? = session

    override fun onUpdateNotification(session: MediaSession, startInForegroundRequired: Boolean) {
        publishNotification(startInForegroundRequired)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val controls = (application as RutsFyApp).player
        when (intent?.action) {
            ACTION_PREV -> controls.previous()
            ACTION_NEXT -> controls.next()
            ACTION_TOGGLE -> session?.player?.let { if (it.isPlaying) it.pause() else it.play() }
        }
        return super.onStartCommand(intent, flags, startId)
    }

    override fun onTaskRemoved(rootIntent: Intent?) {
        val player = exo
        val active = player != null && player.mediaItemCount > 0 &&
            player.playbackState != Player.STATE_IDLE &&
            player.playbackState != Player.STATE_ENDED
        if (!active) stopSelf()
    }

    override fun onDestroy() {
        scope.cancel()
        session?.run {
            player.release()
            release()
        }
        session = null
        exo = null
        super.onDestroy()
    }

    private fun publishNotification(startInForegroundRequired: Boolean) {
        val mediaSession = session ?: return
        val player = mediaSession.player
        val active = player.mediaItemCount > 0 &&
            player.playbackState != Player.STATE_IDLE &&
            player.playbackState != Player.STATE_ENDED
        if (!active && !startInForegroundRequired) {
            ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
            return
        }
        val notification = buildNotification(player, mediaSession)
        ServiceCompat.startForeground(
            this,
            NOTIFICATION_ID,
            notification,
            ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK,
        )
        refreshArtwork(player)
    }

    private fun buildNotification(player: Player, mediaSession: MediaSession): Notification {
        val meta = player.mediaMetadata
        val title = meta.title?.toString().orEmpty().ifBlank { "RutsFy" }
        val artist = meta.artist?.toString().orEmpty().ifBlank { "RutsFy" }
        val artKey = meta.artworkUri?.toString()
        val playing = player.isPlaying
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_stat_music)
            .setContentTitle(title)
            .setContentText(artist)
            .setLargeIcon(artKey?.let { artwork[it] })
            .setContentIntent(mediaSession.sessionActivity)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setOnlyAlertOnce(true)
            .setOngoing(playing)
            .setShowWhen(false)
            .addAction(controlAction(ACTION_PREV, android.R.drawable.ic_media_previous, "Anterior", 1))
            .addAction(
                controlAction(
                    ACTION_TOGGLE,
                    if (playing) android.R.drawable.ic_media_pause else android.R.drawable.ic_media_play,
                    if (playing) "Pausar" else "Reproduzir",
                    2,
                ),
            )
            .addAction(controlAction(ACTION_NEXT, android.R.drawable.ic_media_next, "Próxima", 3))
            .setStyle(
                MediaStyle()
                    .setMediaSession(mediaSession.sessionCompatToken)
                    .setShowActionsInCompactView(0, 1, 2),
            )
            .build()
    }

    private fun controlAction(action: String, icon: Int, label: String, request: Int): NotificationCompat.Action {
        val intent = Intent(this, PlaybackService::class.java).setAction(action)
        val pending = PendingIntent.getService(
            this,
            request,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        return NotificationCompat.Action(icon, label, pending)
    }

    private fun refreshArtwork(player: Player) {
        val uri = player.mediaMetadata.artworkUri ?: return
        val key = uri.toString()
        if (artwork.containsKey(key) || key in artworkMiss) return
        artworkMiss.add(key)
        val token = ++artworkJob
        val http = (application as RutsFyApp).http
        scope.launch {
            val bitmap = withContext(Dispatchers.IO) { fetchArtwork(http, uri) } ?: return@launch
            if (token != artworkJob) return@launch
            artwork[key] = bitmap
            val current = session?.player ?: return@launch
            if (current.mediaMetadata.artworkUri?.toString() == key) {
                publishNotification(startInForegroundRequired = current.playWhenReady)
            }
        }
    }

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT < 26) return
        val manager = getSystemService(NotificationManager::class.java)
        val channel = NotificationChannel(CHANNEL_ID, "Reprodução", NotificationManager.IMPORTANCE_DEFAULT).apply {
            description = "Player do RutsFy"
            setSound(null, null)
            enableVibration(false)
            lockscreenVisibility = Notification.VISIBILITY_PUBLIC
        }
        manager.createNotificationChannel(channel)
    }

    private class Transport(
        player: ExoPlayer,
        private val controls: PlaybackCoordinator,
    ) : ForwardingPlayer(player) {
        override fun getAvailableCommands(): Player.Commands {
            return super.getAvailableCommands().buildUpon()
                .add(COMMAND_SEEK_TO_NEXT_MEDIA_ITEM)
                .add(COMMAND_SEEK_TO_PREVIOUS_MEDIA_ITEM)
                .build()
        }

        override fun isCommandAvailable(command: Int): Boolean {
            return command == COMMAND_SEEK_TO_NEXT_MEDIA_ITEM ||
                command == COMMAND_SEEK_TO_PREVIOUS_MEDIA_ITEM ||
                super.isCommandAvailable(command)
        }

        override fun seekToNext() = controls.next()

        override fun seekToPrevious() = controls.previous()

        override fun seekToNextMediaItem() = controls.next()

        override fun seekToPreviousMediaItem() = controls.previous()

        override fun hasNextMediaItem(): Boolean = controls.canNext()

        override fun hasPreviousMediaItem(): Boolean = controls.canPrevious()
    }

    private companion object {
        const val CHANNEL_ID = "rutsfy_playback"
        const val NOTIFICATION_ID = 41
        const val ACTION_PREV = "dev.ruts.rutsfy.PREV"
        const val ACTION_NEXT = "dev.ruts.rutsfy.NEXT"
        const val ACTION_TOGGLE = "dev.ruts.rutsfy.TOGGLE"

        fun fetchArtwork(http: okhttp3.OkHttpClient, uri: Uri): Bitmap? {
            return runCatching {
                val request = okhttp3.Request.Builder().url(uri.toString()).build()
                http.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) return null
                    val raw = BitmapFactory.decodeStream(response.body?.byteStream()) ?: return null
                    if (raw.width <= 320 && raw.height <= 320) raw
                    else Bitmap.createScaledBitmap(raw, 320, 320, true)
                }
            }.getOrNull()
        }
    }
}
