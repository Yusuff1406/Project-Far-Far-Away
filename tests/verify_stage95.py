from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
exe=R/'native/build/stage95_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage95_session_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
(R/'docs/stage95_native_validation.json').write_text(json.dumps(dict(deterministic_save_restore_scenes=30,future_frame_comparison_per_scene=30,editor_presets=26,hero_types=5,corrupt_state_transactional_rejection=True,nested_minigame_restore=True,device_tested=False),indent=2)+'\n')
