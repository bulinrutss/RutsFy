package dev.ruts.rutsfy.data

import android.content.Context
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import org.json.JSONArray
import org.json.JSONObject

/** Guarda o cookie de sessão (`rutsfy_session`) entre aberturas do app. */
class PrefsCookieJar(context: Context) : CookieJar {
    private val prefs = context.getSharedPreferences("rutsfy_cookies", Context.MODE_PRIVATE)
    private val cookies = mutableListOf<Cookie>()

    init {
        val raw = prefs.getString(KEY, null) ?: "[]"
        val arr = runCatching { JSONArray(raw) }.getOrDefault(JSONArray())
        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            runCatching { cookieFrom(obj) }.getOrNull()?.let { cookies.add(it) }
        }
    }

    override fun saveFromResponse(url: HttpUrl, newCookies: List<Cookie>) {
        synchronized(cookies) {
            for (cookie in newCookies) {
                cookies.removeAll { it.name == cookie.name && it.domain == cookie.domain && it.path == cookie.path }
                if (cookie.expiresAt > System.currentTimeMillis()) cookies.add(cookie)
            }
            persist()
        }
    }

    override fun loadForRequest(url: HttpUrl): List<Cookie> {
        synchronized(cookies) {
            val now = System.currentTimeMillis()
            cookies.removeAll { it.expiresAt <= now }
            return cookies.filter { it.matches(url) }
        }
    }

    fun clear() {
        synchronized(cookies) {
            cookies.clear()
            persist()
        }
    }

    private fun persist() {
        val arr = JSONArray()
        cookies.forEach { arr.put(cookieJson(it)) }
        prefs.edit().putString(KEY, arr.toString()).apply()
    }

    private fun cookieJson(cookie: Cookie) = JSONObject()
        .put("name", cookie.name)
        .put("value", cookie.value)
        .put("domain", cookie.domain)
        .put("path", cookie.path)
        .put("expires", cookie.expiresAt)
        .put("secure", cookie.secure)
        .put("hostOnly", cookie.hostOnly)

    private fun cookieFrom(obj: JSONObject): Cookie {
        val builder = Cookie.Builder()
            .name(obj.getString("name"))
            .value(obj.getString("value"))
            .path(obj.optString("path", "/"))
            .expiresAt(obj.optLong("expires"))
        val domain = obj.getString("domain")
        if (obj.optBoolean("hostOnly")) builder.hostOnlyDomain(domain) else builder.domain(domain)
        if (obj.optBoolean("secure")) builder.secure()
        return builder.build()
    }

    private companion object {
        const val KEY = "cookies"
    }
}
