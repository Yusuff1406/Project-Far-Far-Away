#!/usr/bin/env python3
"""Check compiled manifest, arm64 ELF alignment and every Java native entry point."""
import argparse, json, re, struct, subprocess, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apk', type=Path)
    ap.add_argument('--sdk', type=Path, required=True)
    ap.add_argument('--previous-apk', type=Path)
    a = ap.parse_args()
    bt = a.sdk/'build-tools/35.0.0'
    readelf = a.sdk/'ndk/28.0.13004108/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
    def run(*args): return subprocess.check_output([str(x) for x in args], text=True)
    badging = run(bt/'aapt', 'dump', 'badging', a.apk)
    assert "package: name='org.shrek2.research' versionCode='111'" in badging
    assert "sdkVersion:'26'" in badging and "targetSdkVersion:'35'" in badging
    assert "launchable-activity: name='org.shrek2.research.RomImportActivity'" in badging
    assert "native-code: 'arm64-v8a'" in badging
    manifest_xml=run(bt/'aapt2','dump','xmltree',a.apk,'--file','AndroidManifest.xml')
    assert 'RomImportActivity' in manifest_xml
    resources=run(bt/'aapt2','dump','resources',a.apk)
    assert 'style/GameTheme' in resources and '(v31)' in resources
    assert '0x01010031=#ff000000' in resources and '0x0101062c=#ff000000' in resources
    assert '0x0101062d=@0x0106000d' in resources # Android transparent splash icon
    assert 'drawable/project_icon' in resources and 'drawable/launcher_art' not in resources # source-only vector icon
    assert "application-label:'Project Far Far Away'" in badging
    assert 'icon(0x01010002)=@' in manifest_xml and 'roundIcon(0x0101052c)=@' in manifest_xml # icon and roundIcon
    expected = []
    for source in sorted((ROOT/'android/app/src/main/java').rglob('*.java')):
        expected += ['Java_org_shrek2_research_'+source.stem+'_'+name
                     for name in re.findall(r'\bnative\s+\S+\s+(\w+)\s*\(', source.read_text())]
    assert expected
    checked = []
    with zipfile.ZipFile(a.apk) as z:
        assert not any(n.lower().endswith(('.gba','.zip')) for n in z.namelist()),'Original ROM/archive must not be bundled'

        for name in ['lib/arm64-v8a/libshrek_scene.so','lib/arm64-v8a/libc++_shared.so']:
            data = z.read(name)
            assert data[:6] == b'\x7fELF\x02\x01'
            assert struct.unpack_from('<H', data, 18)[0] == 183 # AArch64
            offset = struct.unpack_from('<Q', data, 32)[0]
            stride, count = struct.unpack_from('<HH', data, 54)
            loads = []
            for i in range(count):
                h = struct.unpack_from('<IIQQQQQQ', data, offset+i*stride)
                if h[0] == 1:
                    assert h[7] >= 16384 and h[2] % 16384 == h[3] % 16384
                    loads.append(h[7])
            assert loads
            checked.append({'name':name,'load_segment_alignments':loads})
        lib = ROOT/'android/build/direct-debug/stripped/libshrek_scene.so'
        assert z.read('lib/arm64-v8a/libshrek_scene.so') == lib.read_bytes()
        for name in z.namelist():
            if name.endswith('.wav'): assert z.getinfo(name).compress_type == (zipfile.ZIP_STORED if name.startswith('assets/session/audio/') else zipfile.ZIP_DEFLATED)
    symbols = run(readelf, '--dyn-syms', lib)
    for symbol in expected: assert re.search(r'\b'+symbol+r'\s*$', symbols, re.M), symbol
    run(bt/'zipalign', '-c', '-P', '16', '4', a.apk)
    signature = run(bt/'apksigner', 'verify', '--verbose', a.apk)
    assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in signature
    same_signer = None
    if a.previous_apk:
        def digest(apk):
            certs = run(bt/'apksigner', 'verify', '--print-certs', apk)
            return re.search(r'Signer #1 certificate SHA-256 digest: ([0-9a-f]+)',certs).group(1)
        same_signer = digest(a.apk) == digest(a.previous_apk)
        assert same_signer
    result = {'jni_exports_verified':expected,'libraries':checked,'manifest_verified':True,
              'signature_verified':True,'zip_alignment_kib':16,'device_execution':False,
              'previous_apk_signer_matches':same_signer}
    (ROOT/'docs/android_apk_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
