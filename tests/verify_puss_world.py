#!/usr/bin/env python3
"""New worlds14/21: real frames plus explicitly relocated region/exit fixtures."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;IP=C.POINTER(I);P=C.c_void_p;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('destroy',[P]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('snapshot',[P,IP]),('scene_id',[P]),('player_type',[P]),('health',[P]),('level_complete',[P]),('world_info',[P,IP]),('requests',[P,IP,C.c_size_t]),('set_auto_restart',[P,I]),('set_viewport',[P,I,I]),('projectile_snapshot',[P,I,IP]),('audio_since',[P,I,IP,C.c_size_t,IP]),('load_level',[P]+[C.c_char_p]*5)]:getattr(l,'s2_session_'+n).argtypes=a
frames=0;sounds=set();projectileKinds=set();states=set();runs=[];width=240;pix=(C.c_uint32*38400)();info=(I*8)();state=(I*320)();meta=(I*4)();projectile=(I*82)()
def step(h,b):
 global frames
 e=l.s2_session_step(h,b,pix,len(pix),info);assert e==0,(frames,b,e,list(info));l.s2_session_snapshot(h,state);states.add(state[80]);frames+=1
 for i in range(l.s2_session_projectile_snapshot(h,-1,None)):
  assert l.s2_session_projectile_snapshot(h,i,projectile)==0;projectileKinds.add(projectile[0])
def audio(h):
 raw=(I*(4096*3))();next_=I();n=l.s2_session_audio_since(h,0,raw,4096,C.byref(next_));assert n>=0;sounds.update(raw[i*3]for i in range(n))
with tempfile.TemporaryDirectory()as td:
 folder=Path(td)
 for sc in [23]:
  rows=json.loads((ROOT/f'objects/scene_{sc:02}/objects.json').read_text())['objects'];hero=next(x for x in rows if x['type']==4);raw=(ROOT/f'objects/scene_{sc:02}/scene.s2ob').read_bytes();base=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/f'extracted/scene_{sc:02}/scene.s2lv',ROOT/f'collision/scene_{sc:02}/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']
  def create(path):
   err=I();h=l.s2_session_create_level(*[str(x).encode()for x in base+[path]],C.byref(err));assert h and not err.value,(sc,err.value);assert l.s2_session_scene_id(h)==sc and l.s2_session_player_type(h)==4;l.s2_session_world_info(h,meta);assert meta[0]==len(rows)and meta[1]==len(rows)-1;return h
  def fixture(x,y,clear=False):
   d=bytearray(raw);struct.pack_into('<HH',d,18+(hero['instance_id']-1)*44,max(1,x),y)
   for row in rows:
    if row['type']==151 or(clear and 53<=row['type']<=60):struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,12000,0)
   p=folder/f'scene_{sc}.s2ob';p.write_bytes(d);return p
  h=create(ROOT/f'objects/scene_{sc:02}/scene.s2ob')
  try:
   for t in range(720):
    step(h,64 if t<20 and t%2==0 else 16|(1 if t%96==0 else 0)|(2 if t%96==40 else 0))
    if t==150:Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/f'previews/puss_world_{sc:02}_68.png')
   audio(h)
  finally:l.s2_session_destroy(h)
  kinds=sorted(set(x['type']for x in rows if x['type']<91))
  for kind in kinds:
   row=next(x for x in rows if x['type']==kind);x,y=row['anchor_px'];h=create(fixture(x-30,y))
   try:
    for t in range(240):step(h,16|(1 if t%72==0 else 0)|(2 if t%72==30 else 0))
    audio(h)
   finally:l.s2_session_destroy(h)
  # Isolated exit contact: retain original exit and terrain, relocate player;
  # suppress the intro and hostiles to certify this transition separately.
  exit_=next(x for x in rows if x['type']==148);h=create(fixture(*exit_['anchor_px'],clear=True))
  try:
   for t in range(500):
    step(h,64 if t%2==0 else 0)
    if l.s2_session_level_complete(h):break
   assert l.s2_session_level_complete(h),(sc,list(info));audio(h)
  finally:l.s2_session_destroy(h)
  # Actual spell receive + terminal recovery, no health decrement substitution.
  h=create(fixture(*hero['anchor_px'],clear=True))
  try:
   event=l.s2_session_player_event;event.argtypes=[P,IP];before=l.s2_session_health(h);assert event(h,(I*3)(1,41,1))==1
   for t in range(160):step(h,0)
   assert l.s2_session_health(h)==before and state[80]!=15;audio(h)
  finally:l.s2_session_destroy(h)
  runs.append(dict(scene=sc,object_rows=len(rows),region_types=kinds,exit_source_dialogue=exit_['word8_actor_tag'],isolated_exit_complete=True))
assert projectileKinds and 15 in states,(projectileKinds,states)
report=dict(native_frames=frames,runs=runs,projectile_types=sorted(projectileKinds),player_states=sorted(states),sound_ids=sorted(sounds),mismatches=0,device_tested=False,scope='Puss scene23 start replay720 frames each plus240-frame region fixtures for every primary type below91. Player/intro relocation and hostile suppression only in explicit fixtures; no complete-route claim. Original exit script and spell defeat/restart validated.')
(ROOT/'docs/puss_world_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
