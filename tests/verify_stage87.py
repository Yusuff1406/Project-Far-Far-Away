#!/usr/bin/env python3
"""Source sound data, real input sessions, camera audio flags and party palettes."""
import argparse,hashlib,wave
import numpy as np
from session75_fixtures import *
ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Path(args.rom).read_bytes()
l.s2_session_player_event.argtypes=[P,IP]
runs=[]
# The package must retain the ROM's actor-specific sound descriptors.
for scene in [1,2,13,14,21]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];donkey=next(r for r in rows if r['type']==6)
 placements={r['instance_id']:donkey['anchor_px']for r in rows if r['type']in range(3,8)}
 s=Scene(scene,placements);l.s2_session_set_auto_restart(s.h,0)
 try:
  if l.s2_session_player_type(s.h)!=6:s.step(512)
  assert l.s2_session_player_type(s.h)==6
  for _ in range(70):s.step()
  start=len(s.requests());s.step(1)
  for _ in range(45):s.step()
  sound_ids=lambda:[struct.unpack_from('<i',rom,q[2]-0x08000000)[0]for q in s.requests()[start:]if q[1]==11]
  jump=sound_ids();assert jump==[55],(scene,'jump',jump)
  for _ in range(40):s.step()
  start=len(s.requests());assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
  for _ in range(30):s.step()
  hurt=sound_ids();assert hurt==[18],(scene,'hurt',hurt)
  runs.append(dict(scene=scene,Donkey_jump=jump,Donkey_hurt=hurt,damage_via_owner_API=True))
 finally:s.close()
# Conditional actor sound/query66 must not treat distant flyers as visible.
for x,expected in [(100,1),(500,0)]:
 s=Scene(2,{73:(85,302),33:(x,260)})
 try:
  s.step();assert s.actor(33)[56]==expected,(x,s.actor(33)[56])
  runs.append(dict(flying_enemy_x=x,camera_visibility=expected))
 finally:s.close()
# Re-synthesize the reported effects with the original offline GAX routines.
import sys
sys.path.insert(0,str(R/'tools'))
from extract_session_sfx import GaxOracle
for sound in [55,18]:
 pcm,_=GaxOracle(rom,31537).render(sound)
 with wave.open(str(R/f'android/app/src/main/assets/session/audio/sfx_{sound}.wav'),'rb')as w:asset=w.readframes(w.getnframes())
 assert pcm==asset
 runs.append(dict(original_PCM_id=sound,sha256=hashlib.sha256(pcm).hexdigest(),matches_shipped_asset=True))
# Independently composite the red palette for an injured INACTIVE partner.
raw=(R/'android/app/src/main/assets/session/resources.s2pk').read_bytes();_,_,nb,na=struct.unpack_from('<4s3I',raw);at=16
for _ in range(nb):_,n=struct.unpack_from('<2I',raw,at);at+=8+n
animations={}
for _ in range(na):a,i,n=struct.unpack_from('<3I',raw,at);at+=12;animations[a]=(i,raw[at:at+n].decode());at+=n
l.s2_sprite_bank_create.argtypes=[C.c_char_p];l.s2_sprite_bank_create.restype=P;l.s2_sprite_bank_destroy.argtypes=[P]
l.s2_actor_anchor_q8.argtypes=[IP,IP,I,I,IP]
l.s2_sprite_composite_bank_palette.argtypes=[P]+[I]*7+[P,C.c_size_t,I]
def sprite(pose,palette,camera):
 state=(I*320)(*pose);anchor=(I*2)();l.s2_actor_anchor_q8(C.cast(C.byref(state,72*4),IP),state,state[18],state[38],anchor)
 idx,name=animations[state[47]];bank=l.s2_sprite_bank_create(str(R/'android/app/src/main/assets/session/sprites'/name).encode());assert bank
 out=(C.c_uint32*38400)()
 try:assert l.s2_sprite_composite_bank_palette(bank,idx,state[22],state[18],240,160,(anchor[0]>>8)-camera[0],(anchor[1]>>8)-camera[1],out,len(out),palette)==0
 finally:l.s2_sprite_bank_destroy(bank)
 return np.frombuffer(bytes(out),dtype=np.uint32).reshape(160,240)
for damaged in [3,6]:
 s=Scene(2,{73:(85,302),71:(160,304)})
 try:
  for _ in range(70):s.step()
  if damaged==6:s.step(512)
  assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
  s.step(512 if damaged==3 else 256);assert l.s2_session_player_type(s.h)!=damaged
  target=s.hero(damaged);camera=s.camera();normal=sprite(target,-1,camera);red_index=animations[0x0834f43c if damaged==3 else 0x08330034][0];red=sprite(target,red_index,camera);active=sprite(s.hero(),-1,camera)
  mask=(red!=0)&(normal!=red)&(active==0);mask[:40]=False
  assert mask.sum()>10
  actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],red[mask]),(damaged,int((actual[mask]!=red[mask]).sum()))
  runs.append(dict(inactive_damage_hero=damaged,red_palette_pixels=int(mask.sum())))
 finally:s.close()
# The source clover (type80) overlaps the hero in foreground, before pickup.
rows=json.loads((R/'objects/scene_13/objects.json').read_text())['objects'];placements={r['instance_id']:(1850,255)if r['type']in[3,80]else(1950,255)for r in rows if r['type']in[3,6,80]}
s=Scene(13,placements)
try:
 s.step();item=s.actor(next(r['instance_id']for r in rows if r['type']==80));camera=s.camera();front=sprite(item,-1,camera);hero=sprite(s.hero(),-1,camera);partner=sprite(s.hero(6),-1,camera);mask=(front!=0)&(hero!=0)&(front!=hero)&(partner==0);mask[:40]=False
 assert mask.sum()>5
 actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],front[mask])
 runs.append(dict(source_clover_type=80,foreground_pixels=int(mask.sum())))
finally:s.close()
# The untouched flying pumpkin script must receive physical Shrek punches.
s=Scene(2,{73:(85,302),24:(105,300)})
try:
 hit=False
 for t in range(120):
  s.step(18 if t%24==0 else 16 if t<20 else 0);a=s.actor(24);hit|=a[148]==3
 assert hit and s.actor(24)[40]&1
 runs.append(dict(physical_flying_pumpkin_punch=True,death_and_removal=True,frames=120))
finally:s.close()
# Cat uses the source constructor packet [2,3,0], including real flyer contact.
for dx in [-20,20]:
 s=Scene(23,{10:(878,1736),8:(878+dx,1726)});l.s2_session_set_auto_restart(s.h,0)
 try:
  hit=False
  for t in range(180):
   s.step((34 if dx<0 else 18)if t%24==0 else 0);hit|=s.actor(8)[148]==2
  assert hit and s.actor(8)[40]&1,(dx,s.actor(8)[144:150])
  runs.append(dict(Cat_physical_flyer_hit=True,side=dx,source_damage_class=2,enemy_removed=True,frames=180))
 finally:s.close()
report=dict(cases=runs,mismatches=0,device_tested=False,scope='Explicit source-object placements; real jump/selection/attack inputs and independent sprite palette masks. Damage injected through public owner API, automatic restart disabled only for sound isolation. GAX runs offline for two effects. Not full routes or Android device playback.')
(R/'docs/stage87_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
