# Reproducible local build

Run commands from the repository root. The audited environment is Linux x86-64 / Python 3.12 / JDK 17. Install a C++17-capable `g++` for host tests. Android SDK tools must have their executable permissions intact.

## Dependencies

`requirements-audit.txt` pins the Python package versions used in this audit. `requirements.txt` contains the earlier version ranges; those ranges are not a certification of every possible combination.

Install Android SDK platform 35, Build Tools 35.0.0, NDK 28.0.13004108 and CMake 3.22.1. The direct builder expects these locations beneath the SDK root:

```text
platforms/android-35/android.jar
build-tools/35.0.0/aapt2
build-tools/35.0.0/d8
build-tools/35.0.0/zipalign
build-tools/35.0.0/apksigner
ndk/28.0.13004108/build/cmake/android.toolchain.cmake
cmake/3.22.1/bin/cmake
```

The JDK root must contain `bin/javac`, `bin/jar` and `bin/keytool`. A JRE alone is insufficient. The build script has Linux x86-64 NDK tool paths and has not been validated on Windows/macOS.

## Local resource generation

Run `python3 tools/prepare_assets.py /path/to/original.gba --jobs 2`. This performs map, collision, sprite, object, script-resource, font, frontend and audio extraction in dependency order. Offline extraction uses Unicorn to evaluate selected original initialization/audio routines; the installed Android application does not run a general-purpose GBA emulator.

Previously hidden dependencies fixed by this audit:

- Collision extraction no longer requires pre-existing scene preview PNGs.
- Pickup-manager parameters are extracted directly from the ROM; a retained JSON is no longer required.
- Runtime map/collision/object copies, campaign metadata, all frontend resources, complete SFX, epilogue music and the two unused tracks are included in the preparation command.
- APK builds reject missing or changed expected resources before compiling.

Generated data stays in ignored `extracted/`, `collision/`, `objects/`, `sprites/`, `previews/`, `docs/` outputs and `android/app/src/main/assets/`. Keep it local. Do not copy those folders into a public source commit. The source archive command uses an independent allowlist.

## APK and verification

Run the direct builder described in README. Then:

```bash
python3 tests/verify_android_apk.py dist/ProjectFarFarAway-debug.apk --sdk /absolute/path/to/android-sdk
```

The verifier checks compiled manifest settings, native ARM64 ELF alignment, JNI entry points, signature and ZIP alignment. It does not install or launch the app.

The builder generates `android/debug.keystore` locally if absent. Never commit a signing key. The package/application ID remains `org.shrek2.research` for compatibility; changing the visible app label does not change that ID.

## Tests

Run the source-only test before resource preparation, then native build and data-dependent tests after preparation as shown in README. Some historical tests still require other generated research reports; the documented audit test set is the verified developer route, not a claim that every old script is a standalone supported test.

To remove local game data, delete only the generated directories listed above. Preserve `docs/BUILD.md`, `docs/AUDIT.md` and `docs/audit_summary.json` if cleaning documentation outputs.

## Experimental Android 5 build and launcher artwork

Use the same SDK/NDK/JDK setup and prepared assets for both variants:

```bash
python3 tools/build_android_debug.py --legacy --sdk /absolute/path/to/android-sdk --jdk /absolute/path/to/jdk-17 --output dist/ProjectFarFarAway-Android5-experimental.apk
```

`--legacy` builds API21 ARMv7 + ARM64 with a separate app ID, API21-compatible file/audio/display paths, native library extraction and v1 signing for old Android installers. The main APK uses API26+ and now also contains both ARMv7 and ARM64. The two apps keep separate ROM imports and saved data.

Supply `--launcher-art /path/to/your-icon.png` to either build to use your own launcher PNG. The builder stages this in its private resource copy; it never adds the PNG to public source. Release APKs use the maintainer's previous artwork, while the source default is the original FF vector placeholder.

Verify either APK with `tests/verify_android_apk.py`; pass `--legacy` for the experimental variant and the same `--launcher-art` file to verify the packaged icon pixels. ARM64 uses 16 KiB ELF alignment; the ARMv7 shared C++ runtime uses its supported 4 KiB alignment. ZIP alignment is 16 KiB for both.

`tests/verify_unified_activity75.py --api 21 --jdk /path/to/jdk --rom /path/to/original.gba` exercises the actual Java/JNI engine with API21 UI/audio stubs, including ROM import, static music loading, menu, editor, control and pacing behavior. These are host tests, not Android device execution.

Stage113 writes quick-state format 113 (the same field layout as 108). Loading format 108 zero-quota chapters subtracts the historical 40-coin baseline, preserving editor additions. Formats 95/97/99 remain readable. The original boss differential test covers 23 source-routine cases; the Stage113 integration test runs B capture/release without trainer immunity in all three rounds.


## v1.0.6 ARMv7 package

```bash
python3 tools/build_android_debug.py --armv7 --sdk /absolute/path/to/android-sdk --jdk /absolute/path/to/jdk-17 --keystore /private/path/to/debug.keystore --output dist/ProjectFarFarAway_v1.0.6_ARMv7.apk
python3 tests/verify_android_apk.py dist/ProjectFarFarAway_v1.0.6_ARMv7.apk --armv7 --sdk /absolute/path/to/android-sdk --previous-apk /path/to/previous-Android5.apk
```

This builds only `armeabi-v7a`, minSdk21, versionCode116, with package `org.shrek2.research.legacy`. Retain the previous private signing key to upgrade the Android 5 app and preserve its data. It is separate from the main `org.shrek2.research` app. The default and `--legacy` build routes remain available. Gradle defines equivalent `modern`, `legacy` and `armv7` device flavors; the direct ARMv7 route was verified for this release, while the Gradle routes were not executed.

Music parsing reads bounded WAV chunks directly, preserving PCM and loop points while avoiding ByteArrayOutputStream growth and whole-file copies. Sprite banks retain decoded pixels only. Mirrored composition clips once per piece and uses row pointers in its inner loop. These changes do not alter saved-state layouts or simulation rules. The exact original resource verification remains in place.

The focused parser check needs no ROM or Android stubs:

```bash
mkdir -p native/build/music116
javac -d native/build/music116 android/app/src/main/java/org/shrek2/research/MusicPcm.java tests/java/org/shrek2/research/MusicMemory116Test.java
java -Xmx32m -cp native/build/music116 org.shrek2.research.MusicMemory116Test
java -Xmx128m -cp native/build/music116 org.shrek2.research.MusicMemory116Test android/app/src/main/assets
```

`tests/compare_sprites116.py --baseline /path/to/v1.0.5-sprites.so --candidate /path/to/v1.0.6-sprites.so` compares cached rendering after compiling each version's `native/sprite_renderer.cpp` with `g++ -O2 -std=c++17 -shared -fPIC`. The comparison uses prepared runtime assets.


## Common v1.0.6 release

The default build includes both `armeabi-v7a` and `arm64-v8a` with the main app ID `org.shrek2.research` and minSdk26. `--legacy` includes the same architectures and optimizations with minSdk21 and `org.shrek2.research.legacy`. Both have versionCode116. Each package can update its corresponding v1.0.5 APK when signed with the same private key. One source tree builds all variants; no separate branch or source archive is needed per architecture. The optional `--armv7` route remains available for a smaller 32-bit-only legacy package.

```bash
python3 tools/build_android_debug.py --sdk /path/to/android-sdk --jdk /path/to/jdk-17 --keystore /private/path/to/debug.keystore --output dist/ProjectFarFarAway_v1.0.6.apk
python3 tools/build_android_debug.py --legacy --sdk /path/to/android-sdk --jdk /path/to/jdk-17 --keystore /private/path/to/debug.keystore --output dist/ProjectFarFarAway_v1.0.6_Android5_experimental.apk
```

The direct main and legacy APK routes were both built and checked for this common release. Gradle flavor definitions are included but were not executed here. No physical device or emulator was tested.
