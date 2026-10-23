#!/usr/bin/env python3
"""Run Stage102 native regressions against an already-built host library."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
(R.parent/'scratch99').mkdir(exist_ok=True)
for name in ['stage102_fixture','stage102_smoke','stage98_frontend_fixture','stage99_damage_fixture']:
    exe=R/'native/build'/name
    subprocess.run(['g++','-std=c++17','-O2',str(R/'tests'/f'{name}.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
    from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
