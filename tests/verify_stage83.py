#!/usr/bin/env python3
"""Reported failure regressions; real inputs plus explicit owner damage fixtures."""
from session75_fixtures import *
for name,args in [('player_event',[P,IP]),('death_restarts',[P]),('projectile_snapshot',[P,I,IP]),('world_size',[P,IP])]:getattr(l,'s2_session_'+name).argtypes=args
runs=[]
# The key/weapon/fairy are picked up through Select. DD74 must preserve ordinary
# Shrek ownership through hurt; effects5/7 are covered by the existing suite.
for item,mode in[(21,2),(16,1),(51,6)]:
 s=Scene(2,{73:(85,302),71:(160,304),item:(85,302)})
 try:
  for t in range(300):s.step(4 if t==250 else 0)
  h=s.hero();assert h[83]==item and h[81]==mode,(item,h[80:88])
  hp=h[89];assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
  assert s.hero()[89]==hp-1 and s.hero()[83]==item
  states=[]
  for t in range(100):states.append(s.step()[80])
  assert 6 in states and s.hero()[80]!=6 and s.hero()[83]==item
  s.step(4)
  for t in range(50):s.step()
  assert not s.hero()[83]
  runs.append(dict(item=item,mode=mode,hurt_recovers=True,ownership_preserved=True,Select_release=True))
 finally:s.close()
# An inactive companion falling into the void must enter death and restart
# the shared level; the old code left it falling forever in state4.
s=Scene(2);size=(I*2)();assert l.s2_session_world_size(s.h,size)==0;s.close()
for selection in[0,768]:
 s=Scene(2,{73:(85,302),71:(size[0]-8,size[1]-20)})
 try:
  seen=False
  for t in range(220):
   s.step(selection);seen|=s.hero(6)[80]==13
   if l.s2_session_death_restarts(s.h):break
  assert seen and l.s2_session_death_restarts(s.h)>0,(selection,s.hero(6)[80:96])
  runs.append(dict(inactive_companion_fall=True,joint=bool(selection),death_animation=True,shared_restart_frame=t+1))
 finally:s.close()
# Repeated upward cookies at a safe source-floor location, without enemy/HP
# edits. Shots leaving the whole map upwards cannot accumulate indefinitely.
s=Scene(3,{95:(62,285)});out=(I*82)();peak=0;upward=False
try:
 for t in range(2400):
  s.step(66 if t%24==0 else 0)
  n=l.s2_session_projectile_snapshot(s.h,-1,None);peak=max(peak,n)
  for i in range(n):
   assert l.s2_session_projectile_snapshot(s.h,i,out)==0
   upward|=out[0]==161 and out[13]<0
   assert not(out[0]==161 and out[3]+out[33]*128<0 and out[13]<=0 and out[15]<=0),'escaped cookie retained'
 assert upward and 0<peak<8,(peak,upward)
 for t in range(240):s.step()
 assert l.s2_session_projectile_snapshot(s.h,-1,None)==0
 runs.append(dict(upward_fire_frames=2400,peak_live_shots=peak,escaped_shots_reclaimed=True,all_shots_expired=True))
finally:s.close()
report=dict(cases=runs,device_tested=False,scope='Real Select, fixed-floor firing, companion void placements. Damage injected through public owner event API. Omitted partner isolation explicitly disables automatic restart in placement helper. No uninterrupted route or phone certification.')
(R/'docs/stage83_fixes_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
