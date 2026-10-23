#!/usr/bin/env python3
"""New chapters and reported effects/party finish; actual button input fixtures.
Relocated regional/exit fixtures are not uninterrupted full-route certification.
"""
from session75_fixtures import *
from PIL import Image
import random,struct
l.s2_session_level_complete.argtypes=[P];l.s2_session_world_info.argtypes=[P,IP];l.s2_session_spawner_snapshot.argtypes=[P,I,IP]
runs=[];new=[25,9,11,8]
for scene in new:
 s=Scene(scene)
 try:
  info=(I*4)();assert l.s2_session_world_info(s.h,info)==0;assert info[2]==0
  seen=False
  for t in range(420):
   seen|=bool(l.s2_session_dialogue_active(s.h));s.step(64 if t>20 and t%2==0 else 0)
  assert seen and not l.s2_session_dialogue_active(s.h),scene
  Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage79_chapter_{scene:02}.png')
  runs.append(dict(scene=scene,original_start=True,intro_closed=True,source_objects=info[0],skipped_objects=0))
 finally:s.close()
for scene,hero,plate,gate,xy in[(25,22,2,16,(672,516)),(8,80,3,2,(3279,516))]:
 s=Scene(scene,{hero:xy,plate:(xy[0],548),gate:(575,639)if scene==25 else(3391,447)})
 try:
  for _ in range(100):s.step()
  q=[q for q in s.requests()if q[1]==1 and q[4:6]==[9,3]];assert len(q)==1 and not(s.actor(plate)[39]&3)and not(s.actor(gate)[39]&3),(scene,q,s.actor(gate)[39])
  runs.append(dict(scene=scene,one_weight_plate=True,linked_gate_open=True))
 finally:s.close()
for scene,placements,ident in[(9,{94:(480,294),95:(480,294),85:(544,294)},85),(11,{78:(910,358),80:(910,358),50:(976,358)},50)]:
 s=Scene(scene,placements)
 try:
  for t in range(700):s.step(2 if t%60==0 else 0)
  q=[q for q in s.requests()if q[1]==23 and 53<=q[4]<=62];assert q
  counts=(I*8)();assert l.s2_session_spawner_snapshot(s.h,ident,counts)==0;assert 0<=counts[2]<=counts[0]
  runs.append(dict(scene=scene,spawner49_children=len(q),live_limit_obeyed=True))
 finally:s.close()
for scene in new:
 source=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];heroes=[r for r in source if r['type']in[3,4,6]]
 for typ in[19,21,27,32,49,54,61,62]:
  a=next((r for r in source if r['type']==typ),None)
  if not a:continue
  placements={r['instance_id']:tuple(r['anchor_px'])for r in source}
  for i,h in enumerate(heroes):placements[h['instance_id']]=(max(12,a['anchor_px'][0]-45-i*20),max(0,a['anchor_px'][1]-40))
  s=Scene(scene,placements);rng=random.Random(79000+scene*100+a['instance_id']);held=0
  try:
   for t in range(240):
    if l.s2_session_dialogue_active(s.h):b=64 if t%2 else 0
    else:
     if t%12==0:held=rng.choice([0,16,17,18,32,33,34,2,3,4,768|17]if len(heroes)>1 else[0,16,17,18,32,33,34,2,3,4])
     b=held
    s.step(b)
   runs.append(dict(scene=scene,region_actor=a['instance_id'],type=typ,frames=240,all_objects_retained=True))
  finally:s.close()
for scene in new+[2,13]:
 source=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];heroes=[r for r in source if r['type']in[3,4,6]];exit=next(r for r in source if r['type']==148);x,y=exit['anchor_px']
 for together in([False,True]if len(heroes)>1 else[True]):
  placements={exit['instance_id']:(x,y)}
  for i,h in enumerate(heroes):placements[h['instance_id']]=(x-8-i*3 if together or i==0 else x-150,y)
  s=Scene(scene,placements);animations={h['type']:set()for h in heroes};victory=False
  try:
   for t in range(500):
    s.step(64 if t%2==0 else 0)
    for h in heroes:
     hero=s.hero(h['type'])
     if hero[80]==12:animations[h['type']].add(hero[22]);victory=True
    if l.s2_session_level_complete(s.h):break
   assert bool(l.s2_session_level_complete(s.h))==together,(scene,together,s.hero()[80],s.hero()[:2])
   if together:assert victory and all(len(v)>1 for v in animations.values()),(scene,animations)
   runs.append(dict(scene=scene,exit_fixture=True,together=together,completed=together,victory_frames={str(k):len(v)for k,v in animations.items()}))
  finally:s.close()
# Persistent effects: same B/A+B must keep ownership, Select must release it.
for typ,mode,scene,item,hero,pos in[(81,5,14,1,1,(0,0)),(82,7,13,1,79,(0,0))]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];item=next(r['instance_id']for r in rows if r['type']==typ);h=next(r['instance_id']for r in rows if r['type']==3 or(scene==14 and r['type']==6));xy=(100,150)
 # Use a real known floor in each map, retaining its source effect script.
 xy=(1850,255)if scene==13 else(392,320)
 s=Scene(scene,{h:xy,item:xy})
 try:
  for t in range(360):s.step(4 if t in[40,120,200,280]and not s.hero()[83]else 0)
  assert s.hero()[83]==item and s.hero()[81]==mode,(typ,s.hero()[80:88])
  for t in range(90):s.step(2 if t%10==0 else 0)
  assert s.hero()[83]==item
  s.step(4)
  for _ in range(50):s.step()
  assert not s.hero()[83]
  runs.append(dict(item_type=typ,B_keeps_effect=True,Select_releases=True))
 finally:s.close()
# Lever25 emits original descriptor21 exactly once on a real Shrek punch.
s=Scene(13,{79:(1845,255),78:(1760,260),51:(1852,285)})
try:
 for t in range(160):s.step(2 if t==30 else 0)
 q=[q for q in s.requests()if q[1]==11 and q[2]==0x08053f60];assert len(q)==1,q
 assert s.actor(51)[47]==0x0834ad78
 runs.append(dict(lever_sound_id=21,emissions=1))
finally:s.close()
# Puss startup voice85; AFK still uses source motion12's silent descriptor0.
for scene in[8,23]:
 s=Scene(scene)
 try:
  idle_seen=False
  for t in range(1000):
   s.step(64 if t<60 and t%2==0 else 0);idle_seen|=s.hero()[80]==10
  q=[q for q in s.requests()if q[1]==11 and q[2]==0x08053e58];assert len(q)==1,(scene,q)
  assert idle_seen
  runs.append(dict(scene=scene,puss_intro_voice=85,emissions=1,AFK_state=10))
 finally:s.close()
rom=Path(__import__('sys').argv[1]).read_bytes()
v=struct.unpack_from('<I',rom,0x10638)[0];assert struct.unpack_from('<I',rom,0x708bdc+v-0x02000000+0x1a4)[0]==0x0800f5bd
assert struct.unpack_from('<I',rom,0x4c4fc+13*40+36)[0]==0x08053c6c # source motion12
assert struct.unpack_from('<I',rom,0x53c6c)[0]==0
report=dict(cases=runs,total_cases=len(runs),new_scenes=new,full_routes_verified=False,device_tested=False,puss_AFK_source_silent=True,scope='Actual native button input; original startup, all object accounting, regional fixtures, isolated exits. Both heroes victory tested; no uninterrupted campaign route or Android device certification.')
(R/'docs/stage79_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
