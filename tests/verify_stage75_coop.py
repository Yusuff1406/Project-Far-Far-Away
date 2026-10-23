#!/usr/bin/env python3
"""Physical two-hero fixtures plus the real chapter02 wall route."""
from session75_fixtures import *
from PIL import Image
runs=[]
for both in [False,True]:
 s=Scene(placements={73:(213,302),71:(214,302)if both else(400,302),55:(240,312)})
 try:
  for t in range(100):
   h=s.step((768 if both else 0)|16 if t>=20 else 0)
   a=s.actor(55)
   assert h[0]+h[30]*128<=a[0]-a[30]*128+256,'Shrek passed through solid block'
  moved=(a[0]-241*256)/256;assert moved>100 if both else abs(moved)<1,(both,moved)
  if both:assert s.hero(6)[0]>300*256
  runs.append(dict(kind='block',controlled_heroes=2 if both else 1,moved_px=moved,no_walkthrough=True))
 finally:s.close()
for both in [False,True]:
 # Preserve source tag1 gate26, so the plate must open a real subscribed gate.
 s=Scene(placements={73:(85,301),71:(105,301)if both else(400,302),47:(100,334),49:(1119,271)})
 try:
  for _ in range(100):s.step()
  notices=[x for x in s.requests()if x[1]==1 and x[4:7]==[9,3,1]];assert len(notices)==int(both),(both,notices)
  a=s.actor(47);gate=s.actor(49);assert bool(a[39]&3)==(not both),(both,a[39]);assert bool(gate[39]&3)==(not both),(both,gate[39],gate[47])
  runs.append(dict(kind='pressure_plate',weights=2 if both else 1,notice_count=len(notices),tag=1,source_gate_open=not bool(gate[39]&3)))
 finally:s.close()
s=Scene(placements={73:(85,302),71:(280,304)})
try:
 for _ in range(20):s.step()
 # Holding selection does not cycle. Camera follows the source5 px/frame limit.
 before=s.camera()[0];s.step(512);assert l.s2_session_player_type(s.h)==6;first=s.camera();assert 0<=first[0]-before<=5 and first[2]>16,first
 for _ in range(80):s.step(512)
 end=s.camera();assert end[2]==0 and end[0]>first[0],end
 s.step(256);assert l.s2_session_player_type(s.h)==3
 for _ in range(80):s.step()
 x1=s.hero(3)[0];x2=s.hero(6)[0]
 for _ in range(20):s.step(768|16)
 assert s.hero(3)[0]>x1 and s.hero(6)[0]>x2
 runs.append(dict(kind='L_R',L='Donkey',R='Shrek',camera_first=first,camera_end=end,joint_movement=True))
finally:s.close()
s=Scene()
try:
 for t in range(310):s.step(64 if t in[2,4,6]else 16 if 60<=t<200 else 2 if t==201 else 0)
 assert s.hero(3)[80]==0 and l.s2_session_player_type(s.h)==3
 # Original Shrek crack event11/0 no longer reaches class9 actor handlers.
 notices=[x for x in s.requests()if x[1]==22 and x[4]==11];assert notices
 s.step(512);assert l.s2_session_player_type(s.h)==6
 for _ in range(160):s.step(16)
 s.step(0);s.step(2)
 for _ in range(90):s.step()
 wall=s.actor(68);assert wall[40]&1,('Donkey kick did not break cracked wall',wall[40])
 for _ in range(50):s.step(16)
 assert s.hero(6)[0]>360*256,s.hero(6)[:2]
 Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/'previews/stage75_wall.png')
 runs.append(dict(kind='wall',Shrek_crack_does_not_error=True,Donkey_break=True,passage_open=True))
finally:s.close()
report=dict(cases=runs,mismatches=0,device_tested=False,scope='Real chapter02 source physics/actors/scripts with relocated block/plate/players, actual native button inputs, no direct pose edits. Source pressure notice9/3 tag1 opens gate26; natural unmodified chapter route reproduces the former wall failure. Camera uses the original fixed5px/frame follow cap.')
(R/'docs/stage75_coop_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
