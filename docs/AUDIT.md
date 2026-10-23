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
