#!/usr/bin/env python3
"""Key stomp regression and render-allocation checks."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
exe=R/'native/build/stage105_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage105_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
