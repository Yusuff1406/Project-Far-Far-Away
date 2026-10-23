#!/usr/bin/env python3
from session75_fixtures import *
from PIL import Image
l.s2_session_level_complete.argtypes=[P];l.s2_session_player_event.argtypes=[P,IP]
runs=[]
# Inactive pose13, immediate return to ordinary idle on selection.
s=Scene(placements={73:(85,302),71:(112,304)})
try:
 for _ in range(30):s.step()
 assert s.hero(6)[80]==11 and s.hero(6)[47]==0x832ffbc,s.hero(6)[80:88]
 s.step(512);assert s.hero(6)[80]==0
 for _ in range(30):s.step()
 assert s.hero(3)[80]==9 and s.hero(3)[47]==0x834f364
 s.step(256);assert s.hero(3)[80]==0
 runs.append(dict(inactive_poses=True,reactivation=True))
finally:s.close()
for selection in [256,512,768]:
 s=Scene(placements={73:(3230,182),71:(3231,182),1:(3237,182)})
 try:
  for t in range(420):
   s.step(selection|(64 if t%2==0 else 0))
   if l.s2_session_level_complete(s.h):break
  assert l.s2_session_level_complete(s.h),(selection,list(s.info),s.hero()[80])
  runs.append(dict(exit_selection=selection,complete_frame=t))
 finally:s.close()
# Actual Shrek subclass wall reaction: source listener10F20, motion25.
s=Scene()
try:
 seen=False
 for t in range(310):
  h=s.step(64 if t in[2,4,6]else 16 if 60<=t<200 else 2 if t==201 else 0)
  if h[80]==22:
   assert h[47]==0x0834f49c;seen=True
 assert seen and h[80]==0
 runs.append(dict(Shrek_wall_reaction_motion25=True,returns_to_idle=True))
finally:s.close()
# Real fairy pickup followed by B and A+B; no injected carry mode.
s=Scene(placements={73:(85,302),71:(400,302),21:(85,302)})
try:
 for t in range(320):s.step(4 if t==250 else 0)
 assert s.hero()[83]==21 and s.hero()[81]==2,s.hero()[80:88]
 s.step(2);assert s.hero()[83]==21
 for _ in range(60):s.step()
 states=set()
 for t in range(110):
  h=s.step(3 if t==0 else 1 if t<50 else 0);states.add(h[80]);assert h[83]==21,('fairy dropped',t,h[80:88])
 assert states.intersection({19,20,21}),states
 runs.append(dict(fairy_B_kept=True,fairy_combo_states=sorted(states)))
finally:s.close()
# Apple's original global9/0 must actually activate enemy death scripts.
s=Scene(placements={73:(85,302),71:(400,302),16:(85,302),33:(500,260)})
try:
 for t in range(320):s.step(4 if t==250 else 0)
 assert s.hero()[83]==16 and s.hero()[81]==1,s.hero()[80:88]
 for t in range(150):s.step(2 if t<100 else 16)
 notices=[x for x in s.requests()if x[1]==1 and x[4:7]==[9,0,0]]
 assert notices,'apple did not activate'
 for _ in range(150):s.step(16)
 enemy=s.actor(33);assert enemy[40]&1,('apple did not defeat enemy',enemy[40],enemy[47])
 runs.append(dict(apple_notice_count=len(notices),enemy_defeated=True))
finally:s.close()
# A resting block retains configured gentle start rather than terminal speed.
s=Scene(placements={73:(2900,206),71:(2901,206),4:(2951,216)})
try:
 for _ in range(120):s.step()
 a=s.actor(4);assert a[14] and a[11]==256,('resting block',a[14],a[11],a[:2])
 prev=a;edge=None
 for t in range(180):
  s.step(768|16);a=s.actor(4)
  if prev[14]and not a[14]:edge=(t,a[11],a[1]-prev[1]);break
  prev=a
 assert edge is not None and edge[1]<500,('no smooth ledge fall',edge,a[:2])
 runs.append(dict(block_ledge_frame=edge[0],initial_fall_velocity_q8=edge[1],initial_fall_delta_q8=edge[2]))
finally:s.close()
report=dict(cases=runs,mismatches=0,device_tested=False,scope='Real source scene02 objects/terrain in isolated placement fixtures. Physical selection, Select pickup, B and A+B, exit dialogues and completion; source apple broadcast and enemy death. No direct player pose or carry-state writes.')
(R/'docs/stage76_additions_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
