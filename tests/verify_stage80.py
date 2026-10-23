"""Stage80 chapter owner, controllers and source mechanisms; placement fixtures, not full routes."""
import json,random,ctypes as C
from session75_fixtures import Scene,R,l,I
l.s2_session_level_complete.argtypes=[C.c_void_p]
scenes=[17,4,10,29,24,3,19,22,28,12];results=[]
for scene in scenes:
 s=Scene(scene);rng=random.Random(scene)
 try:
  for t in range(1200):
   b=(64 if t%2 else 0)if l.s2_session_dialogue_active(s.h)else rng.choice([0,0,0,16,32,1,2,17,18,33,34,4,64,66,768,784])
   s.step(b)
  results.append(dict(scene=scene,frames=1200,object_count=len(s.rows)))
 finally:s.close()
 print(results[-1],flush=True)
# Return-zone behavior: script81 unlocks149; own outro34 requires returning.
for returned in [False,True]:
 s=Scene(24,{100:(102,408),5:(103,359),103:((103 if returned else 1000),359)})
 try:
  for t in range(700 if returned else 200):
   s.step(64 if t%2 else 0)
   if l.s2_session_level_complete(s.h):break
  ids=[q[4]for q in s.requests()if q[1]==26];assert 81 in ids and (34 in ids)==returned,(returned,ids,list(s.info));assert bool(l.s2_session_level_complete(s.h))==returned
  results.append(dict(exit149_returned=returned,dialogues=ids))
 finally:s.close()
# All seven crystals unlock150, then its own outro38.
s=Scene(19,{56:(974,1157),66:(960,1111),**{i:(1014,1147)for i in[22,38,41,57,81,84,99]}})
try:
 for t in range(1100):
  s.step((64 if t%2 else 0)if l.s2_session_dialogue_active(s.h)else (2 if t%45==30 else 0))
  if l.s2_session_level_complete(s.h):break
 ids=[q[4]for q in s.requests()if q[1]==26];assert 38 in ids and l.s2_session_level_complete(s.h),(ids,list(s.info))
 for id in[22,38,41,57,81,84,99]:assert s.actor(id)[47]==0x0834aeb0,(id,s.actor(id)[47])
 results.append(dict(exit150_frames=t,dialogues=ids))
finally:s.close()
report=dict(scenarios=results,device_tested=False,full_routes_tested=False)
(R/'docs/stage80_validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Stage80 passed')
