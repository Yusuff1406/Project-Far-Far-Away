#!/usr/bin/env python3
"""Verify publication selection, guards and source syntax without original assets."""
import ast,subprocess,sys,tempfile,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from source_inventory import source_files

def main():
    selected=list(source_files());names={p.relative_to(R).as_posix() for p in selected}
    assert {"README.md","LICENSE","tools/prepare_assets.py","tools/assets_expected.json"}<=names
    forbidden={".gba",".sav",".s2qs",".keystore",".jks",".wav",".png",".gif",".s2pk",".s2lv",".s2sp",".s2rs",".apk",".so",".asm"}
    assert all(p.suffix not in forbidden for p in selected)
    assert all(not (set(p.relative_to(R).parts)&{"assets","extracted","sprites","objects","collision","previews"}) for p in selected)
    for p in selected:
        if p.suffix==".py":ast.parse(p.read_text(),filename=str(p))
    # Wrong ROM fails before creating any resources, even with a valid-size dummy.
    with tempfile.TemporaryDirectory() as td:
        rom=Path(td)/"wrong.gba";rom.write_bytes(bytes(8*1024*1024))
        proc=subprocess.run([sys.executable,str(R/"tools/prepare_assets.py"),str(rom)],capture_output=True,text=True)
        assert proc.returncode!=0 and "No output has been generated" in proc.stderr
        output=Path(td)/"source.zip"
        subprocess.run([sys.executable,str(R/"tools/package_source.py"),"--output",str(output)],check=True)
        with zipfile.ZipFile(output) as z:
            assert len(z.namelist())==len(selected)
            assert not any(Path(n).suffix in forbidden for n in z.namelist())
    print("PASS code-only inventory, syntax, wrong-ROM rejection and publication archive")
if __name__=="__main__":main()
