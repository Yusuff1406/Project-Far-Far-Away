"""Integration: original directional parry to ordinary archer death script."""
import json,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory()as d:
 exe=Path(d)/'fixture'
 subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage91_projectile_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
 result=subprocess.run([str(exe)],cwd=R,check=True,capture_output=True,text=True)
 assert 'arrow_hit=1 archer_removed=1'in result.stdout
 (R/'docs/stage91_projectile_validation.json').write_text(json.dumps(dict(arrow_reflected=True,ordinary_archer_hit=True,source_death_script_removed_archer=True,device_tested=False,scope='Source67 projectile, actual event5 reflection and original54 bowman reactions; controlled fixture placements, not a full player-input encounter.'),indent=2)+'\n');print(result.stdout)
