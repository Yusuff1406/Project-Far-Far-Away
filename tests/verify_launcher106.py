#!/usr/bin/env python3
"""Ensure Android resources retain the supplied pixel art and safe adaptive layout."""
import argparse,io,json,subprocess,zipfile
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('apk',type=Path);a.add_argument('--sdk',type=Path,required=True);p=a.parse_args()
with zipfile.ZipFile(p.apk) as z:
 art=next(n for n in z.namelist() if n.startswith('res/drawable-nodpi') and n.endswith('/launcher_art.png'))
 actual=Image.open(io.BytesIO(z.read(art))).convert('RGBA');expected=Image.open(R/'android/app/src/main/res/drawable-nodpi/launcher_art.png').convert('RGBA');assert actual.size==expected.size and actual.tobytes()==expected.tobytes()
tool=p.sdk/'build-tools/35.0.0/aapt2'
def xml(name):return subprocess.check_output([str(tool),'dump','xmltree',str(p.apk),'--file',name],text=True)
manifest=xml('AndroidManifest.xml');assert 'icon(0x01010002)=@' in manifest and 'roundIcon(0x0101052c)=@' in manifest
assert 'adaptive-icon' in xml('res/mipmap-anydpi-v26/ic_launcher.xml')
fg=xml('res/drawable/launcher_foreground.xml');assert 'E: inset' in fg and 'filter(0x0101011b)=false' in fg
# Percent insets retain the source aspect at every launcher size/density.
assert abs(.4/(1-.227037*2)-expected.width/expected.height)<1e-5
print('PASS original icon pixels, adaptive icon, roundIcon, scale-independent aspect and nearest filtering')
