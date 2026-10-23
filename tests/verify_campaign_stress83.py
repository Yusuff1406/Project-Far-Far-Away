#!/usr/bin/env python3
"""Deterministic ordinary-input runs on all30 source scenes, not full routes."""
import random
from session75_fixtures import *
runs=[]
for scene in [0,1,2,13,17,25,14,9,11,5,8,4,10,23,21,29,24,3,19,22,20,28,12,15,16,26,7,6,18,27]:
 s=Scene(scene);rng=random.Random(8300+scene);b=0
 try:
  for t in range(1600):
   if l.s2_session_dialogue_active(s.h):b=64 if t%2 else 0
   elif t%11==0:b=rng.choice([0,16,17,18,32,33,34,1,2,3,4,128,64,768|17,512,256])
   s.step(b)
  runs.append(dict(scene=scene,seed=8300+scene,frames=1600,passed=True))
  print(scene,'PASS',flush=True)
 finally:s.close()
report=dict(runs=runs,total_frames=sum(r['frames']for r in runs),device_tested=False,scope='All30 unmodified source placements, deterministic held-button sequences, dialogue skip, native automatic death restart. Does not establish full-route correctness, all enemy encounters or absence of all hangs.')
(R/'docs/campaign_stress83_validation.json').write_text(json.dumps(report,indent=2)+'\n')
