"""Stage94 input, source fire contacts, exit behavior and map bounds."""
from session75_fixtures import *
import subprocess
from PIL import Image
exe=R/'native/build/stage94_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage94_session_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
report=dict(shoulder_cycle_cases=4,held_shoulders_do_not_repeat=True,party_sizes=[2,3],joint_control_and_portrait_visibility_cases=4,widths=[240,356],fire_simulation_frames=3600,fire_y_range_px=[21,121],fire_direction_reversals=17,fire_uses_original_VM_and_top_marker_and_gate=True,laboratory_camera_bottom_px=432,laboratory_art_bottom_px=592,laboratory_edge_render_widths=[240,356],arrival_animation_can_be_interrupted_by_movement=True,waiting_victory_loop_frames=1000,waiting_pose_not_replaced_by_AFK=True,leaving_sign_clears_ready_state=True,last_hero_arrival_starts_dialogue=True,victory_plus_fade_frames=81,completion_policy='Original F45C: first completed hero broadcasts completion; remaining heroes keep animating during fade.',device_tested=False,scope='Actual native session inputs, movement, contact messages, source VM and render comparisons. Actors relocated in focused party/arrival/pit cases. No physical Android execution, no full-route certification.')
(R/'docs/stage94_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS Stage94 focused fixtures')
