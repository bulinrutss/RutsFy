plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

val appVersionCode = rootProject.file("version.properties").readLines()
    .firstOrNull { it.startsWith("versionCode=") }
    ?.substringAfter("=")
    ?.trim()
    ?.toInt()
    ?: 2

android {
    namespace = "dev.ruts.rutsfy"
    compileSdk = 35

    defaultConfig {
        applicationId = "dev.ruts.rutsfy"
        minSdk = 26
        targetSdk = 35
        versionCode = appVersionCode
        versionName = "1.0.$appVersionCode"
        buildConfigField("String", "API_ORIGIN", "\"https://ruts.dev\"")
        buildConfigField("String", "API_PREFIX", "\"/rutsfy\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

android.applicationVariants.configureEach {
    outputs.configureEach {
        (this as com.android.build.gradle.internal.api.BaseVariantOutputImpl).outputFileName = "rutsfy.apk"
    }
}

val publishedVersionCode = appVersionCode
tasks.matching { it.name == "assembleDebug" || it.name == "assembleRelease" }.configureEach {
    doLast {
        val variant = if (name.endsWith("Release")) "release" else "debug"
        val outputDir = layout.buildDirectory.get().asFile.resolve("outputs/apk/$variant")
        val apk = outputDir.resolve("rutsfy.apk").takeIf { it.isFile }
            ?: outputDir.resolve("app-$variant.apk")
        if (!apk.isFile) return@doLast
        val metadata = apk.parentFile.resolve("output-metadata.json").readText()
        val baked = Regex(""""versionCode"\s*:\s*(\d+)""").find(metadata)?.groupValues?.get(1)?.toInt()
            ?: publishedVersionCode
        val publishDir = rootProject.projectDir.parentFile.resolve("backend/static/app")
        publishDir.mkdirs()
        apk.copyTo(publishDir.resolve("rutsfy.apk"), overwrite = true)
        publishDir.resolve("version.json").writeText(
            """{"versionCode":$baked,"versionName":"1.0.$baked"}""",
        )
        val next = baked + 1
        val props = rootProject.file("version.properties")
        val current = props.readLines().firstOrNull { it.startsWith("versionCode=") }
            ?.substringAfter("=")?.trim()?.toInt() ?: next
        if (current <= baked) props.writeText("versionCode=$next\n")
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("io.coil-kt:coil-compose:2.7.0")
    implementation("androidx.media3:media3-exoplayer:1.4.1")
    implementation("androidx.media3:media3-session:1.4.1")
    implementation("androidx.media3:media3-datasource-okhttp:1.4.1")
    implementation("androidx.media:media:1.7.0")
    debugImplementation("androidx.compose.ui:ui-tooling")
}
