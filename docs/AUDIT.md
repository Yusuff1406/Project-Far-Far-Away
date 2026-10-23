# v1.0.6 / Stage116 update

This release adds an ARMv7-only API21 package and reduces music/sprite loading memory. Current results are in `audit_summary.json`; historical sections below describe earlier releases.

# v1.0.1 / Stage111 update

Current changes and test results are recorded in `audit_summary.json`. The following audit describes the earlier Stage110 baseline. Current gameplay changes address held springs, physical item floors and editor hero replacement; the 357 original resource checksums are unchanged.

# Source-distribution and build audit

Input: `Project_Far_Far_Away_GitHub_source-1.zip` (2,154 files), SHA-256 `a6f9bd93579ac332b938ca151b715c5e74483f5cb6342c5893b86e0ffadf4e36`.

## Findings in the supplied archive

The archive contains actual C++, Java and Python source. Its direct Android build succeeds with the documented toolchain; native Stage109/110 checks and the real Java/JNI harness also pass. APK manifest, signature, JNI and alignment checks pass. No physical Android execution was performed.

The archive is not asset-free. It includes all357 runtime resource files (music, effects, sprite banks, maps, fonts, frontend images and dialogue/script packages), duplicate development resources, image previews and original icon artwork. Earlier instructions that it was simply ready for source publication did not sufficiently distinguish this embedded content.

## Removed from the public source package

- Everything beneath `android/app/src/main/assets/`.
- `extracted/`, `sprites/`, `collision/`, `objects/` and `previews/`.
- Historical raw assembly dumps, raw resource JSON/hex dumps, screenshots and generated test logs.
- Original raster app icon and its references; replaced with an original FF vector icon.
- SDK/JDK installations, generated APKs, native binaries, signing keys, saves and ROMs.

The source package retains code, extraction logic, addresses/layout metadata, expected hashes and build instructions. Its gameplay C++ files match the supplied Stage110 source. Resource generation recreates all357 expected runtime assets byte for byte from the exact original ROM. No resource bytes or binary-delta asset bundle is included as an alternative payload.

The omission list is a technical inventory of original-game content, not a legal guarantee covering every reconstructed code fragment, name, patent or third-party right.

## Validation limits

The final fresh-tree rebuild results are recorded in `audit_summary.json`. Native simulations and Java/JNI tests are scoped fixtures. They do not prove a complete campaign playthrough, device frame rate, Android input latency or absence of gameplay defects. The GitHub workflow itself has not been executed remotely as part of this audit.


## Stage115 / v1.0.5

The chapter 2-5 final capture retains the original B lift and hand-marker attachment. If the final dialogue interrupts motion20, its remaining frames finish before fading; generic victory state12 and its sound are not entered. Chapter 5-1 joins the existing Fairy scripted endings in fading directly after dialogue. Ordinary level victory remains unchanged.

Controls add an opt-in combined L+R touch button (off by default) and a paused visual layout editor. Dragging moves the actual preview continuously; size and per-button visibility can be changed. Save commits the draft in one preference edit; Reset restores draft defaults; Cancel/Android Back discard the draft. The toolbar can move between top and bottom by tapping its header. Existing individual action assignment and gamepad mapping remain available.

Validation: integrated native final captures for both facings and tap/hold B, exact hand-marker positions during the remaining lift, 17-step black fade without generic victory sound, scripted Gingy/Fairy dialogue endings, and an ordinary-level victory control. Java/JNI host checks exercise optional combined input with a second movement touch, drag/resize drafts, Save/Reset/Cancel, persistence and API21/35 branches. Signed APK structure, original icon pixels and upgrade signer are checked for both packages. These are host tests with explicit Android UI/audio fixtures; no physical Android device or emulator was executed.


## Stage116 / v1.0.6

Built and verified the ARMv7-only APK from the supplied v1.0.5 source. Its app ID and signer match the previous experimental Android 5 APK. All 357 resource checksums match. The APK contains 32-bit ARM libraries only; API21 manifest, all JNI exports, ELF/ZIP alignment, original launcher pixels and v1/v2/v3 signatures were checked. No physical Android device or emulator was run, and no ARMv7 FPS improvement is claimed.

The streaming WAV parser passed 21 real intro/loop pairs with every PCM byte and loop marker compared, fragmented/zero-length reads, reordered chunks, odd unknown chunks and malformed inputs. A generated 12 MiB PCM loop loads with a 32 MiB Java heap; the v1.0.5 parser runs out of heap in the same fixture. This isolates parser memory and does not measure AudioTrack or whole-app RAM.

Cached sprite comparisons cover 11,316 cases across 33 packaged banks, all mirror modes, selected sequence frames, palette overrides and extreme anchors, with zero pixel differences against v1.0.5. Removing packed pixel copies eliminates 3,864,096 retained payload bytes summed across all banks; the number simultaneously loaded varies by scene. Mirrored rendering also removes per-pixel 64-bit coordinate work. Host Stage115 ending checks and Stage110 shoulder/input/state regressions were rerun. The subsequent common release also rebuilds and verifies the main API26 APK and experimental API21 APK, each containing ARMv7 and ARM64. Both share these optimizations and versionCode116, and each signer matches its corresponding v1.0.5 APK. No physical device performance was measured.
