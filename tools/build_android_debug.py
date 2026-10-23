#!/usr/bin/env python3
"""Build this dependency-free Android app with installed SDK tools, without Gradle."""
import argparse, hashlib, json, os, shutil, subprocess, zipfile
import xml.etree.ElementTree as ET
from optimize_apk_payload import compress_music
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sdk', type=Path, required=True)
    ap.add_argument('--jdk', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT/'dist/ProjectFarFarAway-debug.apk')
    ap.add_argument('--keystore', type=Path, default=ROOT/'android/debug.keystore')
    a = ap.parse_args()
    from prepare_assets import verify_assets
    try: verify_assets()
    except RuntimeError as error: ap.error(str(error)+'\nRun: python3 tools/prepare_assets.py /path/to/original.gba')
    sdk, jdk = a.sdk.resolve(), a.jdk.resolve()
    bt = sdk/'build-tools/35.0.0'
    ndk = sdk/'ndk/28.0.13004108'
    cmake = sdk/'cmake/3.22.1/bin/cmake'
    platform = sdk/'platforms/android-35/android.jar'
    for f in [cmake, platform, jdk/'bin/javac', jdk/'bin/jar', jdk/'bin/keytool',
              *[bt/x for x in ['aapt2','d8','zipalign','apksigner']], ndk/'build/cmake/android.toolchain.cmake']:
        if not f.is_file(): ap.error(f'Missing tool or platform: {f}')
    env = dict(os.environ, JAVA_HOME=str(jdk))
    env['PATH'] = str(jdk/'bin')+os.pathsep+env.get('PATH','')
    def run(*args, capture=False):
        print('Running:', Path(str(args[0])).name, flush=True)
        return subprocess.run([str(x) for x in args], env=env, check=True,
                              capture_output=capture, text=True)
    work = ROOT/'android/build/direct-debug'
    work.mkdir(parents=True, exist_ok=True)
    for name in ['classes','dex']:
        p = work/name
        if p.exists(): shutil.rmtree(p)
        p.mkdir()
    native = work/'native'
    run(cmake, '-S', ROOT/'android/app/src/main/cpp', '-B', native,
        f'-DCMAKE_TOOLCHAIN_FILE={ndk}/build/cmake/android.toolchain.cmake',
        '-DANDROID_ABI=arm64-v8a', '-DANDROID_PLATFORM=android-26',
        '-DANDROID_STL=c++_shared', '-DCMAKE_BUILD_TYPE=Release')
    run(cmake, '--build', native, '-j', '4')
    sources = sorted((ROOT/'android/app/src/main/java').rglob('*.java'))
    run(jdk/'bin/javac', '--release', '17', '-encoding', 'UTF-8', '-classpath', platform,
        '-d', work/'classes', *sources)
    run(jdk/'bin/jar', '--create', '--file', work/'classes.jar', '-C', work/'classes', '.')
    run(bt/'d8', '--lib', platform, '--min-api', '26', '--output', work/'dex', work/'classes.jar')
    tree = ET.parse(ROOT/'android/app/src/main/AndroidManifest.xml')
    manifest = tree.getroot()
    manifest.set('package', 'org.shrek2.research')
    app = manifest.find('application')
    app.set(f'{{{ANDROID}}}extractNativeLibs', 'false')
    tree.write(work/'AndroidManifest.xml', encoding='utf-8', xml_declaration=True)
    run(bt/'aapt2', 'compile', '--dir', ROOT/'android/app/src/main/res', '-o', work/'resources.zip')
    run(bt/'aapt2', 'link', '-o', work/'unsigned.apk', '--manifest', work/'AndroidManifest.xml',
        '-I', platform, work/'resources.zip', '-A', ROOT/'android/app/src/main/assets', '--min-sdk-version', '26',
        '--target-sdk-version', '35', '--version-code', '111',
        '--version-name', '1.0.1', '--debug-mode', '-0', 'wav')
    with zipfile.ZipFile(work/'unsigned.apk', 'a') as z:
        for dex in sorted((work/'dex').glob('*.dex')): z.write(dex, dex.name)
        stripped=work/'stripped';stripped.mkdir(exist_ok=True)
        for source in [native/'libshrek_scene.so',ndk/'toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so']:
            copy=stripped/source.name;shutil.copy2(source,copy)
            run(ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip','--strip-unneeded',copy)
            z.write(copy,'lib/arm64-v8a/'+source.name,compress_type=zipfile.ZIP_STORED)
    optimization=compress_music(work/'unsigned.apk')
    run(bt/'zipalign', '-f', '-P', '16', '4', work/'unsigned.apk', work/'aligned.apk')
    a.keystore.parent.mkdir(parents=True, exist_ok=True)
    if not a.keystore.exists():
        run(jdk/'bin/keytool', '-genkeypair', '-keystore', a.keystore, '-storepass', 'android',
            '-keypass', 'android', '-alias', 'androiddebugkey', '-keyalg', 'RSA', '-keysize', '2048',
            '-validity', '10000', '-dname', 'CN=Android Debug,O=Android,C=US')
    output = a.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staged = work/'signed.apk'
    run(bt/'apksigner', 'sign', '--ks', a.keystore, '--ks-key-alias', 'androiddebugkey',
        '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', staged, work/'aligned.apk')
    signature = run(bt/'apksigner', 'verify', '--verbose', staged, capture=True).stdout
    run(bt/'zipalign', '-c', '-P', '16', '4', staged)
    with zipfile.ZipFile(staged) as z:
        assert z.testzip() is None
        assert 'classes.dex' in z.namelist()
        assets = sorted((ROOT/'android/app/src/main/assets').rglob('*'))
        asset_count = 0
        for f in assets:
            if f.is_file() and not any(part.startswith('.')for part in f.relative_to(ROOT/'android/app/src/main/assets').parts):
                assert z.read('assets/'+f.relative_to(ROOT/'android/app/src/main/assets').as_posix()) == f.read_bytes()
                asset_count += 1
    staged.replace(output)
    report = {'apk': output.name, 'size': output.stat().st_size,
              'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'abi': 'arm64-v8a',
              'min_sdk': 26, 'target_sdk': 35, 'version_code': 111,
              'java_sources_compiled': len(sources), 'assets_verified': asset_count,
              'signature_verification': signature.strip(), 'zip_alignment_kib': 16,
              'build_route': 'JDK17 + SDK35 aapt2/d8/zipalign/apksigner + CMake3.22.1/NDK28',
              'device_tested': False, 'payload_optimization':optimization, 'scope': 'Stage111/v1.0.1: held spring bounce, all physical items on dynamic floors, grounded editor hero replacement, correct pickup names; original invisibility damage rules verified. Includes previous fixes and high-refresh support. Lossless smaller APK; exact ROM gate retained. Host and Java/JNI verification; physical Android not tested.'}
    (ROOT/'docs/android_build_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
