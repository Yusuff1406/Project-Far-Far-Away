from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
exe=R/'native/build/stage112_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage112_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
subprocess.run([str(exe)],cwd=R,check=True)
