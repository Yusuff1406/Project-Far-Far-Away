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
    ap.add_argument('--legacy',action='store_true')
    ap.add_argument('--launcher-art',type=Path)
    ap.add_argument('--armv7',action='store_true')
    a = ap.parse_args()
    if a.armv7:a.legacy=True
    package='org.shrek2.research.legacy' if a.legacy else 'org.shrek2.research'
    min_api=21 if a.legacy else 26
    abis=['armeabi-v7a'] if a.armv7 else ['armeabi-v7a','arm64-v8a']
    work=ROOT/('android/build/direct-armv7' if a.armv7 else 'android/build/direct-legacy' if a.legacy else 'android/build/direct-debug')
    bt = a.sdk/'build-tools/35.0.0'
    readelf = a.sdk/'ndk/28.0.13004108/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
    def run(*args): return subprocess.check_output([str(x) for x in args], text=True)
    badging = run(bt/'aapt', 'dump', 'badging', a.apk)
    assert f"package: name='{package}' versionCode='116'" in badging
    assert f"sdkVersion:'{min_api}'" in badging and "targetSdkVersion:'35'" in badging
    assert "launchable-activity: name='org.shrek2.research.RomImportActivity'" in badging
    assert set(re.findall(r"'([^']+)'",re.search(r'^native-code: (.*)$',badging,re.M).group(1)))==set(abis)
    manifest_xml=run(bt/'aapt2','dump','xmltree',a.apk,'--file','AndroidManifest.xml')
    assert 'RomImportActivity' in manifest_xml
    resources=run(bt/'aapt2','dump','resources',a.apk)
    assert 'style/GameTheme' in resources and '(v31)' in resources
    assert '0x01010031=#ff000000' in resources and '0x0101062c=#ff000000' in resources
    assert '0x0101062d=@0x0106000d' in resources # Android transparent splash icon
    assert 'drawable/project_icon' in resources
    if a.launcher_art:assert 'drawable/launcher_art' in resources
    assert "application-label:'Project Far Far Away" in badging
    assert 'icon(0x01010002)=@' in manifest_xml and 'roundIcon(0x0101052c)=@' in manifest_xml # icon and roundIcon
    expected = []
    for source in sorted((ROOT/'android/app/src/main/java').rglob('*.java')):
        expected += ['Java_org_shrek2_research_'+source.stem+'_'+name
                     for name in re.findall(r'\bnative\s+\S+\s+(\w+)\s*\(', source.read_text())]
    assert expected
    checked = []
    with zipfile.ZipFile(a.apk) as z:
        assert not any(n.lower().endswith(('.gba','.zip')) for n in z.namelist()),'Original ROM/archive must not be bundled'

        for abi in abis:
            for filename in ['libshrek_scene.so','libc++_shared.so']:
                name='lib/'+abi+'/'+filename;data=z.read(name)
                bits=32 if abi=='armeabi-v7a' else 64
                assert data[:6]==b'\x7fELF'+bytes([1 if bits==32 else 2,1])
                assert struct.unpack_from('<H',data,18)[0]==(40 if bits==32 else 183)
                if bits==64:offset=struct.unpack_from('<Q',data,32)[0];stride,count=struct.unpack_from('<HH',data,54)
                else:offset=struct.unpack_from('<I',data,28)[0];stride,count=struct.unpack_from('<HH',data,42)
                loads=[]
                for i in range(count):
                    h=struct.unpack_from('<IIQQQQQQ' if bits==64 else '<8I',data,offset+i*stride)
                    if h[0]==1:
                        align=h[7];fileoff=h[2] if bits==64 else h[1];address=h[3] if bits==64 else h[2]
                        page=4096 if bits==32 else 16384
                        assert align>=page and fileoff%page==address%page;loads.append(align)
                assert loads
                checked.append({'name':name,'load_segment_alignments':loads})
            lib=work/'stripped'/abi/'libshrek_scene.so'
            assert z.read('lib/'+abi+'/libshrek_scene.so')==lib.read_bytes()
            symbols=run(readelf,'--dyn-syms',lib)
            for symbol in expected:assert re.search(r'\b'+symbol+r'\s*$',symbols,re.M),symbol
        if a.launcher_art:
            import io
            from PIL import Image
            def pixels(data):
                im=Image.open(io.BytesIO(data)).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);return im.size,bg.tobytes()
            assert pixels(z.read('res/drawable-nodpi-v4/launcher_art.png'))==pixels(a.launcher_art.read_bytes())
        for name in z.namelist():
            if name.endswith('.wav'): assert z.getinfo(name).compress_type == (zipfile.ZIP_STORED if name.startswith('assets/session/audio/') else zipfile.ZIP_DEFLATED)
    run(bt/'zipalign', '-c', '-P', '16', '4', a.apk)
    signature = run(bt/'apksigner', 'verify', '--verbose', a.apk)
    assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in signature
    if a.legacy:assert 'Verified using v1 scheme (JAR signing): true' in signature
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
    (ROOT/('docs/android_legacy_apk_validation.json' if a.legacy else 'docs/android_apk_validation.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
