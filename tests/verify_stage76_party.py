#!/usr/bin/env python3
"""Focused Stage76 world checks: hurt deadline, patrols, fixed camera and source HUD."""
from session75_fixtures import *
import numpy as np
runs=[]
l.s2_session_player_event.argtypes=[P,IP]
# Hurt deadline must survive a grounded frame and the used second-jump flag.
for airborne in [False,True]:
 s=Scene(23,{10:(878,1736)})
 try:
  for t in range(50 if airborne else 20):s.step(1 if airborne and t in[20,30]else 0)
  before=s.hero();assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
  h=s.hero();deadline=h[95];assert deadline>0 and h[80]==6
  states=[]
  for t in range(120):
   h=s.step(16 if t>=60 else 0);states.append(h[80])
   if t<20:assert h[95]==deadline,('hurt deadline overwritten',t,h[95],deadline)
  assert h[80]!=6 and h[0]>before[0]+30*256,(airborne,h[80],h[:2])
  runs.append(dict(hurt_airborne=airborne,recovery_deadline=deadline,control_recovered=True))
 finally:s.close()
# Actual knight contact, with no injected damage packet.
s=Scene(23,{10:(878,1736),48:(850,1736)})
try:
 hurt=None;recovered=None;recovery_x=None
 for t in range(100):
  h=s.step(32 if t>=60 else 0)
  if h[80]==6 and hurt is None:hurt=t
  if hurt is not None and h[80]==0 and recovered is None:recovered=t;recovery_x=h[0]
 assert hurt is not None and recovered is not None and h[0]<recovery_x-20*256,(hurt,recovered,h[:2])
 runs.append(dict(physical_knight_contact=True,hurt_frame=hurt,recovery_frame=recovered,left_input_restored=True))
finally:s.close()
# Original marker placements, no artificial limits or changed enemy trajectories.
rows=json.loads((R/'objects/scene_23/objects.json').read_text())['objects'];byid={x['instance_id']:x for x in rows}
for enemy,markers,axis,lo,hi in [(8,[1,22],0,790,940),(31,[29,30],1,1040,1210),(35,[33,34],1,0,150),(89,[81,99],0,10,165)]:
 ids=[10,enemy,*markers];s=Scene(23,{i:tuple(byid[i]['anchor_px'])for i in ids});positions=[];turns=0;last=0
 try:
  for t in range(1500):
   s.step();a=s.actor(enemy);positions.append(a[axis]/256);v=a[5 if axis==0 else 11];direction=(v>0)-(v<0)
   if direction and last and direction!=last:turns+=1
   if direction:last=direction
  assert min(positions)>=lo and max(positions)<=hi and turns>=5,(enemy,min(positions),max(positions),turns)
  runs.append(dict(patrol_actor=enemy,range_px=[min(positions),max(positions)],turns=turns,source_markers=markers))
 finally:s.close()
# Parse actual source sprite mappings and independently render each HUD layer.
raw=(R/'android/app/src/main/assets/session/resources.s2pk').read_bytes();_,_,nb,na=struct.unpack_from('<4s3I',raw);at=16
for _ in range(nb):_,n=struct.unpack_from('<2I',raw,at);at+=8+n
animations={}
for _ in range(na):a,i,n=struct.unpack_from('<3I',raw,at);at+=12;animations[a]=(i,raw[at:at+n].decode());at+=n
l.s2_sprite_render_file.argtypes=[C.c_char_p]+[I]*7+[P,C.c_size_t]
def hud_sprite(addr,frame,x):
 idx,name=animations[addr];out=(C.c_uint8*(38400*4))();assert l.s2_sprite_render_file(str(R/'android/app/src/main/assets/session/sprites'/name).encode(),idx,frame,0,240,160,x,4,out,len(out))==0
 return np.frombuffer(bytes(out),dtype=np.uint8).reshape(160,240,4).copy()
def verify_hud(s,joint):
 checked=0
 for typ,x,big in [(6,4,0x08328308),(3,32,0x08328398)]:
  active=joint or typ==l.s2_session_player_type(s.h);a=hud_sprite(big+(0 if active else 24),0,x);b=hud_sprite(0x083283e0 if typ==6 else 0x083283f8,s.hero(typ)[89],x);mask=b[:,:,3]>0;a[mask]=b[mask];mask=a[:,:,3]>0
  expected=0xff000000|(a[:,:,0].astype(np.uint32)<<16)|(a[:,:,1].astype(np.uint32)<<8)|a[:,:,2];actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],expected[mask]),('HUD',typ,active);checked+=int(mask.sum())
 return checked
s=Scene(placements={73:(85,302),71:(280,304)})
try:
 for _ in range(20):s.step()
 pixels=verify_hud(s,False);start=s.camera();frames=[]
 for t in range(80):s.step(512);frames.append(s.camera())
 assert all(c[1]==start[1]for c in frames),('diagonal pan',start,frames)
 deltas=[c[0]-start[0]for c in frames];assert deltas==sorted(deltas) and frames[-1][2]==0
 pixels+=verify_hud(s,False)
 # Wait for the jumping hero to land, then check midpoint with different heights.
 for _ in range(100):s.step()
 for _ in range(20):s.step(768)
 a,b=s.hero(3),s.hero(6);c=s.camera();assert c[0]==max(0,((a[0]+b[0])//2>>8)-120),(c,a[:2],b[:2]);pixels+=verify_hud(s,True)
 runs.append(dict(camera_fixed_y=True,source_camera_cap_px=5,joint_camera_midpoint=True,source_HUD_pixels=pixels))
finally:s.close()
report=dict(cases=runs,mismatches=0,device_tested=False,scope='Real native source worlds with explicit placement fixtures. Damage is injected through owner event API; patrols use genuine directional markers. HUD compared to independent source sprite rendering. Party camera uses source090A fixed speed cap.')
(R/'docs/stage76_party_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
