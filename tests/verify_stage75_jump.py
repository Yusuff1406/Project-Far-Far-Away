#!/usr/bin/env python3
"""Puss: A-edge second jump, no third/held-repeat, replenishment on landing."""
from session75_fixtures import *
from PIL import Image
l.s2_session_set_puss_double_jump.argtypes=[P,I]
traces={}
for mode in ['single','double','third','held','two_cycles']:
 s=Scene(23,{10:(878,1736)});l.s2_session_set_puss_double_jump(s.h,1);trace=[]
 try:
  for t in range(210):
   press=t==20 or mode in['double','third','two_cycles']and t==30 or mode=='third'and t==40 or mode=='held'and 20<=t<60 or mode=='two_cycles'and t in[130,140]
   h=s.step(1 if press else 0);trace.append(h)
   if mode=='double'and t==50:Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/'previews/stage75_double_jump.png')
  traces[mode]=trace
 finally:s.close()
for t in range(110):
 assert traces['third'][t][:14]==traces['double'][t][:14],('third jump changed physics',t)
 assert traces['held'][t][:14]==traces['single'][t][:14],('held A created another jump',t)
assert traces['double'][30][11]==-1237 and traces['single'][30][11]==-747
assert traces['double'][30][100]&0x10000 and not(traces['double'][109][100]&0x10000)
assert min(h[1]for h in traces['double'][:110])+25*256<min(h[1]for h in traces['single'][:110])
assert traces['two_cycles'][140][11]==-1237 and traces['two_cycles'][140][100]&0x10000
report=dict(native_frames=1050,second_A_restarts_source_jump_row=True,jump_velocity_q8=-1237,one_extra_jump_per_flight=True,held_A_no_repeat=True,third_A_no_boost=True,landing_replenishes=True,mismatches=0,device_tested=False,scope='Real native Puss scene23 physics and source jump animation/parameters. Added A-edge jump count is a native implementation of the requested mechanic; original second-jump timing/animation has not been measured against a Puss recording.')
(R/'docs/stage75_jump_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
