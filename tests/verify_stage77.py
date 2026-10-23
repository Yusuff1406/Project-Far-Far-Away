#!/usr/bin/env python3
"""Actual party inputs plus source090A camera and F48C transition comparisons."""
from session75_fixtures import *
import random
from verify_generic_runtime import Original,Rom
from unicorn.arm_const import UC_ARM_REG_R6,UC_ARM_REG_PC
rom=Rom(__import__('sys').argv[1]);o=Original(rom);rng=random.Random(77)
l.s2_camera_follow_step.argtypes=[IP,IP]
for case in range(5000):
 current=[rng.randrange(-1000000,1000000)for _ in range(2)];target=[rng.randrange(-1000000,1000000)for _ in range(2)];p=0x02007000;o.u.mem_write(p+16,struct.pack('<4i',*current,*target));o.u.reg_write(UC_ARM_REG_R6,p);o.u.emu_start(0x0800090b,0x08000962,count=1000);assert o.u.reg_read(UC_ARM_REG_PC)==0x08000962
 a=(I*2)(*current);assert l.s2_camera_follow_step(a,(I*2)(*target))==0;assert list(a)==list(struct.unpack('<2i',o.u.mem_read(p+16,8))),(case,list(a))
runs=[]
# Source transient -> looping idle, then physical selection wakes immediately.
for selected,inactive,row in [(256,6,0x0832ffd4),(512,3,0x0834f364)]:
 s=Scene(placements={73:(85,302),71:(112,304)})
 try:
  trace=[]
  for t in range(220):
   s.step(selected);h=s.hero(inactive);trace.append(h)
  assert any(h[80]==11 for h in trace) and any(h[80]==9 for h in trace)
  loop=[h for h in trace if h[80]==9];assert all(h[47]==row for h in loop) and len({h[22]for h in loop})>=10
  other=512 if selected==256 else 256;s.step(other);assert s.hero(inactive)[80]==0
  runs.append(dict(inactive_type=inactive,loop_animation=hex(row),sequence_frames=len({h[22]for h in loop}),reactivated=True))
 finally:s.close()
# Source HUD activation sound: only newly activated hero, no held-input repeat.
for selected,sound in [(256,83),(512,86)]:
 s=Scene(placements={73:(85,302),71:(112,304)})
 try:
  for _ in range(80):s.step(selected)
  before=len(s.requests());s.step(768);new=s.requests()[before:];audio=[q for q in new if q[1]==11];ids=[struct.unpack_from('<i',rom.data,q[2]-0x08000000)[0]for q in audio];assert ids==[sound],(selected,ids)
  before=len(s.requests())
  for _ in range(80):s.step(768)
  assert not any(q[1]==11 and struct.unpack_from('<i',rom.data,q[2]-0x08000000)[0]==sound for q in s.requests()[before:]),'repeated activation while held'
  before=len(s.requests());s.step(512 if selected==256 else 256)
  assert not any(q[1]==11 and struct.unpack_from('<i',rom.data,q[2]-0x08000000)[0]in[83,86]for q in s.requests()[before:]),'already-active joint hero voiced again'
  runs.append(dict(from_type=3 if selected==256 else 6,newly_active_sound=sound,no_held_repeat=True,no_repeat_joint_to_single=True))
 finally:s.close()
# Different distances: source cap5 px/frame, no fixed-duration jump/cut.
for gap in [40,195,300]:
 s=Scene(placements={73:(85,302),71:(85+gap,304)})
 try:
  for _ in range(60):s.step()
  prev=s.camera();trace=[]
  for t in range(100):
   s.step(512);c=s.camera();assert abs(c[0]-prev[0])<=5 and abs(c[1]-prev[1])<=7,(gap,t,prev,c);trace.append(c);prev=c
  assert c[2]==0;assert c[0]==max(0,(s.hero(6)[0]>>8)-120)
  runs.append(dict(camera_gap_px=gap,max_step_px=max(abs(b[0]-a[0])for a,b in zip(trace,trace[1:])),settled=True))
 finally:s.close()
report=dict(source_camera_cases=5000,cases=runs,mismatches=0,device_tested=False,scope='Source camera090A..0960 executed directly in Unicorn; native party scenes with physical L/R/L+R. Activation descriptors traced through original HUD initializers10CD8/CD0C and edge handlerF60C. Original waiting transitionF48C -> F5EC/motion11. No Android execution or full campaign certification.')
(R/'docs/stage77_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
