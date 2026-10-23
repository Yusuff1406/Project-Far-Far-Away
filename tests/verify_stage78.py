#!/usr/bin/env python3
"""Genuine Select/carry/switch inputs and all-party exit gate; no pose writes."""
from session75_fixtures import *
l.s2_session_level_complete.argtypes=[P]
runs=[]
for actor,mode in [(21,2),(16,1),(51,6)]:
 s=Scene(placements={73:(85,302),71:(160,304),actor:(85,302)})
 try:
  for t in range(380):
   h=s.hero();s.step(4 if t in[200,250,300,350]and not h[83]else 0)
  h=s.hero();assert h[83]==actor and h[81]==mode,(actor,h[80:88])
  s.step(512);assert l.s2_session_player_type(s.h)==6
  for _ in range(45):s.step(16)
  shrek,donkey=s.hero(3),s.hero(6);item=s.actor(actor)
  assert shrek[83]==actor and shrek[81]==mode and donkey[83]==0
  assert abs(item[0]-shrek[0])<256 and abs(item[0]-donkey[0])>20*256
  s.step(256);assert l.s2_session_player_type(s.h)==3 and s.hero()[83]==actor
  for _ in range(20):s.step()
  s.step(4)
  for _ in range(60):s.step()
  assert s.hero(3)[83]==0 and s.hero(6)[83]==0
  runs.append(dict(item=actor,mode=mode,switch_keeps_owner=True,item_follows_inactive_owner=True,return_and_select_release=True))
 finally:s.close()
# Switch immediately after capture, before the mode handshake finishes.
s=Scene(placements={73:(85,302),71:(160,304),21:(85,302)})
try:
 for t in range(251):s.step(4 if t==250 else 0)
 assert s.hero()[83]==21
 s.step(512);assert l.s2_session_player_type(s.h)==6
 for _ in range(90):s.step()
 assert s.hero(3)[83]==21 and s.hero(3)[81]==2 and s.hero(6)[83]==0
 runs.append(dict(pending_capture_switch=True,handshake_reaches_original_owner=True))
finally:s.close()
# Shrek can be left holding a lifted mushroom, including its lift animation.
for switch_tick in [2,80]:
 s=Scene(placements={73:(85,302),71:(160,304),62:(85,314)})
 try:
  for t in range(switch_tick):s.step(2 if t==1 else 0)
  assert s.hero()[102]==62
  s.step(512);assert l.s2_session_player_type(s.h)==6
  for _ in range(90):s.step(16)
  h=s.hero(3);a=s.actor(62);assert h[102]==62 and a[0]==h[0] and a[1]<h[1]
  s.step(256);assert s.hero()[102]==62;s.step(0);s.step(2)
  for _ in range(80):s.step()
  assert s.hero(3)[102]==0
  runs.append(dict(lifted_mushroom=True,switch_during_lift=switch_tick==2,inactive_owner_keeps_lift=True,return_and_B_release=True))
 finally:s.close()
# Both heroes keep separate objects across repeated selection and joint control.
s=Scene(placements={73:(85,302),71:(160,304),21:(85,302),51:(160,304)})
try:
 for t in range(320):s.step(4 if t==250 else 0)
 s.step(512)
 for t in range(90):s.step(4 if t==10 else 0)
 assert s.hero(3)[83]==21 and s.hero(6)[83]==51
 for selection in [256,512,768,256,512]:
  for _ in range(20):s.step(selection)
  assert s.hero(3)[83]==21 and s.hero(6)[83]==51
 runs.append(dict(two_distinct_items=True,repeated_switches_and_joint_preserve_owners=True))
finally:s.close()
# Only one hero at the sign: neither the final conversation nor finish may start.
for selection,near in [(256,3),(512,6),(768,3)]:
 placements={73:(3230,182)if near==3 else(3130,182),71:(3231,182)if near==6 else(3130,182),1:(3237,182)}
 s=Scene(placements=placements)
 try:
  for t in range(180):
   s.step(selection|(64 if t%2==0 else 0));assert not l.s2_session_dialogue_active(s.h)and not l.s2_session_level_complete(s.h),(selection,t)
  assert not(s.actor(1)[40]&1),'exit consumed by first hero'
  # Bring the lagging hero to the sign using real movement.
  lagging=512 if near==3 else 256
  for t in range(110):
   s.step(lagging|16)
   if l.s2_session_dialogue_active(s.h):break
  assert l.s2_session_dialogue_active(s.h),(selection,s.hero(3)[:2],s.hero(6)[:2])
  for t in range(420):
   s.step(64 if t%2==0 else 0)
   if l.s2_session_level_complete(s.h):break
  assert l.s2_session_level_complete(s.h)
  runs.append(dict(first_at_exit=near,initial_selection=selection,first_hero_does_not_consume_exit=True,second_arrival_finishes=True))
 finally:s.close()
# A grounded hero holding a lifted object also counts as standing at the exit.
s=Scene(placements={73:(3230,222),71:(3130,182),62:(3230,234),1:(3237,182)})
try:
 for t in range(80):s.step(2 if t==1 else 0)
 assert s.hero(3)[102]==62 and not l.s2_session_dialogue_active(s.h)
 s.step(512)
 for t in range(120):
  s.step(16)
  if l.s2_session_dialogue_active(s.h):break
 assert l.s2_session_dialogue_active(s.h),('lifted object blocked exit',s.hero(3)[80])
 for t in range(420):
  s.step(64 if t%2==0 else 0)
  if l.s2_session_level_complete(s.h):break
 assert l.s2_session_level_complete(s.h)
 runs.append(dict(grounded_lifted_object_at_exit=True,second_arrival_finishes=True))
finally:s.close()
# Already together: either individual selection and L+R can finish.
for selection in [256,512,768]:
 s=Scene(placements={73:(3230,182),71:(3231,182),1:(3237,182)})
 try:
  for t in range(420):
   s.step(selection|(64 if t%2==0 else 0))
   if l.s2_session_level_complete(s.h):break
  assert l.s2_session_level_complete(s.h),(selection,list(s.info))
  runs.append(dict(both_at_exit=True,selection=selection,complete=True))
 finally:s.close()
# The other paired chapter must require both heroes too.
for together in [False,True]:
 s=Scene(13,{79:(3768,175),78:(3769,175)if together else(3630,175),2:(3775,175)})
 try:
  for t in range(420):
   s.step(64 if t%2==0 else 0)
   if not together:assert not l.s2_session_level_complete(s.h) and not l.s2_session_dialogue_active(s.h)
   if l.s2_session_level_complete(s.h):break
  assert bool(l.s2_session_level_complete(s.h))==together
  runs.append(dict(scene=13,both_at_exit=together,completion=together))
 finally:s.close()
report=dict(cases=runs,mismatches=0,device_tested=False,scope='Source scenes02/13 terrain and actors with explicit placement fixtures; genuine Select, B, L/R/L+R and movement. Fairy/apple/key and lifted mushroom ownership, pending pickup, distinct items for both heroes, grounded all-party exit gate, lone-hero rejection and completion after both arrive. No player state injection, Android execution or full campaign certification.')
(R/'docs/stage78_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
