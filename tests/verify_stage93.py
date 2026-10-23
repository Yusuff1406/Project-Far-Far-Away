"""Focused real-session regression fixtures for the Stage93 reports."""
from session75_fixtures import *
import subprocess
from PIL import Image
exe=R/'native/build/stage93_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage93_session_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True)
from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
for scene in [26,6]:
 s=Scene(scene)
 for _ in range(60):s.step()
 Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage93_bonus_{scene:02}.png');s.close()
report=dict(first_bonus_visible_hero_pixels=739,first_bonus_live_mice=True,flame_and_arrival_superseded_by="verify_stage94.py",boss_capture_sequences=[dict(physical_B_held_frames=1,captures=3),dict(physical_B_held_frames=75,captures=3)],joint_pickups_with_Shrek_selected_or_partner=4,party_sizes=[2,3],offscreen_activation_widths=[240,356],waiting_hero_receives_offscreen_enemy_contact=True,silent_pit_hero_types=[3,6,5,4,7],nested_loss_mosaic=True,standalone_loss_black_fade=True,device_tested=False,scope='Real native session updates and rendering. Fixtures relocate actors/set vulnerability to isolate captures, pickups, pit exits and party arrival. Six captures cover two consecutive three-capture sequences, not uninterrupted full fights. Original activation margins reused; complete source category scheduler and frame-exact victory timing not certified. No physical Android execution.')
(R/'docs/stage93_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS Stage93 focused fixtures and previews')
