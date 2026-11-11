#!/usr/bin/env python3
"""Build RutsFy APK (Gradle) e publica em backend/static/app/. Opcional: deploy Oracle."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
SDK = ROOT / ".android-sdk"
LOCAL_PROPS = ANDROID / "local.properties"
PUBLISH_APK = ROOT / "backend" / "static" / "app" / "rutsfy.apk"
PUBLISH_META = ROOT / "backend" / "static" / "app" / "version.json"


def find_java_home() -> Path | None:
    env = os.environ.get("JAVA_HOME", "").strip()
    if env:
        p = Path(env)
        if (p / "bin" / "java.exe").is_file() or (p / "bin" / "java").is_file():
            return p
    for pattern in [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Android" / "Android Studio" / "jbr",
    ]:
        if not pattern.is_dir():
            continue
        if pattern.name == "Microsoft":
            hits = sorted(pattern.glob("jdk-17*"), reverse=True)
            for hit in hits:
                if (hit / "bin" / "java.exe").is_file():
                    return hit
        elif (pattern / "bin" / "java.exe").is_file():
            return pattern
    return None


def ensure_local_properties() -> None:
    if LOCAL_PROPS.is_file():
        text = LOCAL_PROPS.read_text(encoding="utf-8")
        if "sdk.dir=" in text and SDK.is_dir():
            return
    sdk_dir = SDK.as_posix()
    LOCAL_PROPS.write_text(
        f"## Gerado por build_android_apk.py\nsdk.dir={sdk_dir}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build APK RutsFy")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Roda scripts/setup_android_build.ps1 antes do Gradle",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy Oracle após build (python scripts/deploy_oracle.py)",
    )
    args = parser.parse_args()

    if args.setup or not SDK.is_dir():
        setup = ROOT / "scripts" / "setup_android_build.ps1"
        if not setup.is_file():
            print("Falta scripts/setup_android_build.ps1", file=sys.stderr)
            raise SystemExit(2)
        print("[build] setup Android SDK/JDK…")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(setup),
            ],
            cwd=ROOT,
            check=True,
        )

    java = find_java_home()
    if not java:
        print(
            "JAVA_HOME não encontrado. Rode: powershell -File scripts/setup_android_build.ps1",
            file=sys.stderr,
        )
        raise SystemExit(2)

    ensure_local_properties()
    env = os.environ.copy()
    env["JAVA_HOME"] = str(java)
    env["PATH"] = str(java / "bin") + os.pathsep + env.get("PATH", "")

    gradlew = ANDROID / ("gradlew.bat" if os.name == "nt" else "gradlew")
    if not gradlew.is_file():
        print(f"Falta {gradlew}", file=sys.stderr)
        raise SystemExit(2)

    print("[build] assembleDebug…")
    subprocess.run(
        [str(gradlew), "assembleDebug", "--no-daemon"],
        cwd=ANDROID,
        env=env,
        check=True,
    )

    if not PUBLISH_APK.is_file():
        print("APK não encontrado em backend/static/app/", file=sys.stderr)
        raise SystemExit(1)
    meta = PUBLISH_META.read_text(encoding="utf-8") if PUBLISH_META.is_file() else "?"
    print(f"[ok] {PUBLISH_APK} ({PUBLISH_APK.stat().st_size // 1024} KB)")
    print(f"[ok] {PUBLISH_META}: {meta.strip()}")

    if args.deploy:
        deploy = ROOT / "scripts" / "deploy_oracle.py"
        print("[deploy] Oracle…")
        subprocess.run([sys.executable, str(deploy)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
