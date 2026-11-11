package dev.ruts.rutsfy

import android.app.Application
import dev.ruts.rutsfy.data.PrefsCookieJar
import dev.ruts.rutsfy.data.RutsApi
import dev.ruts.rutsfy.player.OfflineAudio
import dev.ruts.rutsfy.player.PlaybackCoordinator
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

class RutsFyApp : Application() {
    lateinit var cookies: PrefsCookieJar
        private set
    lateinit var http: OkHttpClient
        private set
    lateinit var api: RutsApi
        private set
    lateinit var offline: OfflineAudio
        private set
    lateinit var player: PlaybackCoordinator
        private set

    override fun onCreate() {
        super.onCreate()
        cookies = PrefsCookieJar(this)
        http = OkHttpClient.Builder()
            .cookieJar(cookies)
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.MINUTES)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
        api = RutsApi(http)
        offline = OfflineAudio(this)
        player = PlaybackCoordinator(this)
    }
}
