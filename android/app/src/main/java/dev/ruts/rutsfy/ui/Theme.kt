package dev.ruts.rutsfy.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val BgBase = Color(0xFF121212)
val BgElevated = Color(0xFF181818)
val BgHighlight = Color(0xFF282828)
val TextMain = Color(0xFFFFFFFF)
val TextSub = Color(0xFFB3B3B3)
val TextMuted = Color(0xFF6A6A6A)
val Accent = Color(0xFF3B82F6)

private val Colors = darkColorScheme(
    primary = Accent,
    onPrimary = Color.White,
    background = BgBase,
    onBackground = TextMain,
    surface = BgElevated,
    onSurface = TextMain,
    surfaceVariant = BgHighlight,
    onSurfaceVariant = TextSub,
)

@Composable
fun RutsTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = Colors, content = content)
}
