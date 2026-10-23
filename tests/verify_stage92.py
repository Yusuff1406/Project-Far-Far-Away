from session75_fixtures import *
import subprocess
runs=[]
# Sequential unlock is enforced through the same A and touch launch paths.
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,a in [('snapshot',[P,IP]),('restore',[P,IP]),('progress',[P,IP]),('step',[P,I]),('action',[P]),('destroy',[P]),('touch',[P,I,I])]:getattr(l,'s2_frontend_'+n).argtypes=a
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h
for completed in range(26):
 assert l.s2_frontend_progress(h,(I*7)(1,(1<<completed)-1,0,0,0,0,0))==0
 for chapter in range(25):
  assert l.s2_frontend_restore(h,(I*9)(4,chapter%5,chapter//5,0,0,0,0,0,0))==0
  for _ in range(17):l.s2_frontend_step(h,0)
  l.s2_frontend_action(h)
  state=(I*9)();l.s2_frontend_snapshot(h,state)
  if chapter>completed:
   # Stage96: locked rows cannot be selected; restoration clamps focus.
   assert state[1]<=max(0,min(4,completed-(chapter//5)*5))
   l.s2_frontend_touch(h,150,12+(chapter%5)*22)
   for _ in range(17):l.s2_frontend_step(h,0)
   assert l.s2_frontend_action(h)==0
  else:
   assert state[1]==chapter%5
   if chapter%2:l.s2_frontend_touch(h,150,12+(chapter%5)*22)
   else:l.s2_frontend_step(h,1)
   for _ in range(17):l.s2_frontend_step(h,0)
   assert l.s2_frontend_action(h)>0
 runs.append(dict(kind='sequential_unlock',completed=completed,chapters=25))
l.s2_frontend_destroy(h)
exe=R/'native/build/stage92_fixture';subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage92_session_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True);from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
runs.append(dict(kind='session_fixture',boss_B_captures=3,group_camera_cases=4,inactive_hero_damage_blocked=False))
(R/'docs/stage92_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False),indent=2)+'\n');print('PASS Stage92')
