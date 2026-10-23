#!/usr/bin/env python3
"""Chapter01 native region/contact fixtures, not a complete-route playthrough."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;IP=C.POINTER(I);P=C.c_void_p;lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
lib.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];lib.s2_session_create_level.restype=P
for name,args in [('destroy',[P]),('scene_id',[P]),('player_type',[P]),('unported_markers',[P]),('health',[P]),('coin_count',[P]),('level_complete',[P]),('minigame_state',[P]),('death_restarts',[P]),('reset',[P]),('snapshot',[P,IP]),('dialogue_snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('actor_event',[P,I,IP]),('player_event',[P,IP]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('load_level',[P]+[C.c_char_p]*5),('audio_since',[P,I,IP,C.c_size_t,IP])]:getattr(lib,'s2_session_'+name).argtypes=args
source=json.loads((ROOT/'objects/scene_01/objects.json').read_text())['objects'];raw=(ROOT/'objects/scene_01/scene.s2ob').read_bytes();pix=(C.c_uint32*38400)();info=(I*8)();state=(I*320)();actor=(I*216)();dialog=(I*80)();frames=0;sounds=set();coins=0;changed=set();states=set();deaths=0
base=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_01/scene.s2lv',ROOT/'collision/scene_01/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']
def create(path):
 err=I();h=lib.s2_session_create_level(*[str(x).encode()for x in base],str(path).encode(),C.byref(err));assert h and err.value==0,(path,err.value);assert lib.s2_session_player_type(h)==6 and lib.s2_session_scene_id(h)==1;return h
def step(h,b):
 global frames
 e=lib.s2_session_step(h,b,pix,len(pix),info);assert e==0,(frames,b,e,list(info));lib.s2_session_snapshot(h,state);frames+=1;states.add(state[80]);assert 0x0832fed0<=state[47]<=0x08330100,(hex(state[47]),list(info))
def audio(h):
 rows=(I*(4096*3))();next=I();n=lib.s2_session_audio_since(h,0,rows,4096,C.byref(next));assert n>=0;sounds.update(rows[i*3]for i in range(n))
def fixture(path,x,y):
 d=bytearray(raw);struct.pack_into('<HH',d,18,x,y);struct.pack_into('<HH',d,18+44,6000,0);path.write_bytes(d);return path
h=create(ROOT/'objects/scene_01/scene.s2ob')
try:
 assert lib.s2_session_unported_markers(h)==0 and lib.s2_session_health(h)==4
 for t in range(720):
  step(h,64 if t<4 and t%2==0 else 32|(1 if t%96==0 else 0)|(2 if t%96==40 else 0))
  if t==150:
   actual=Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA');expected=Image.new('RGBA',(240,160))
   draw=lib.s2_sprite_render_file;draw.argtypes=[C.c_char_p]+[C.c_int]*7+[P,C.c_size_t]
   for animation,frame in [(4,0),(13,4)]:
    layer=(C.c_uint8*(240*160*4))();assert draw(str(ROOT/'sprites/bank_328294/bank.s2sp').encode(),animation,frame,0,240,160,4,4,layer,len(layer))==0;expected.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(layer)))
   assert all(actual.getpixel((x,y))==expected.getpixel((x,y))for y in range(40)for x in range(40)if expected.getpixel((x,y))[3]),'Donkey HUD portrait'
   actual.resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/donkey_chapter65.png')
 audio(h);initial=(I*320)();lib.s2_session_reset(h);lib.s2_session_snapshot(h,initial);lib.s2_session_reset(h);lib.s2_session_snapshot(h,state);assert list(initial)==list(state)
 before=list(state);bad=base+[ROOT/'missing.s2ob'];assert lib.s2_session_load_level(h,*[str(x).encode()for x in bad])<0;lib.s2_session_snapshot(h,state);assert list(state)==before
 originalHandle=h;first=[base[0],ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',base[3],ROOT/'objects/scene_00/scene.s2ob'];assert lib.s2_session_load_level(h,*[str(x).encode()for x in first])==0;assert h==originalHandle and lib.s2_session_player_type(h)==3
 assert lib.s2_session_load_level(h,*[str(x).encode()for x in base+[ROOT/'objects/scene_01/scene.s2ob']])==0;assert h==originalHandle and lib.s2_session_player_type(h)==6
finally:lib.s2_session_destroy(h)
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'scene.s2ob'
 for kind in [9,22,38,62,76,78,102,108,109,111,115,125,53,57,89,94,101]:
  row=next(x for x in source if x['type']==kind);x,y=row['anchor_px'];h=create(fixture(p,max(8,x-24),y))
  try:
   lib.s2_session_actor_snapshot(h,row['instance_id'],actor);before=list(actor)
   for tick in range(180):step(h,16 if tick<30 else (2 if tick%36==0 else 0))
   lib.s2_session_actor_snapshot(h,row['instance_id'],actor)
   if list(actor)!=before:changed.add(kind)
   coins+=lib.s2_session_coin_count(h);deaths+=lib.s2_session_death_restarts(h);audio(h)

  finally:lib.s2_session_destroy(h)
 assert coins>0
 h=create(fixture(p,3366,344))
 try:
  for tick in range(30):step(h,0)
  before=lib.s2_session_health(h);assert lib.s2_session_player_event(h,(I*3)(1,38,1))==1;assert lib.s2_session_health(h)==before-1;assert lib.s2_session_player_event(h,(I*3)(1,38,1))==0
  for tick in range(100):step(h,0)
  assert state[80]!=6;audio(h)
 finally:lib.s2_session_destroy(h)
 h=create(fixture(p,31,231))
 try:
  for tick in range(300):
   step(h,64 if tick%2==0 else 0)
   if lib.s2_session_level_complete(h):break
  assert lib.s2_session_level_complete(h)and state[80]==12;audio(h)
 finally:lib.s2_session_destroy(h)
 # Relocate the leprechaun beside the hero for a physical B-talk fixture.
 d=bytearray(fixture(p,3366,344).read_bytes());npc=next(x for x in source if x['type']==94);struct.pack_into('<HH',d,18+(npc['instance_id']-1)*44,3371,329);p.write_bytes(d);h=create(p)
 try:
  for tick in range(800):
   step(h,2 if tick==20 else 1 if tick>=40 and tick%12==4 else 0)
   if lib.s2_session_minigame_state(h)==1:break
  lib.s2_session_dialogue_snapshot(h,dialog);assert lib.s2_session_minigame_state(h)==1,('bonus entry',list(info),list(dialog[64:80]))
  frozen=list(state[:80])
  for tick in range(8):step(h,0);assert list(state[:80])==frozen
  for tick in range(600):
   step(h,16)
   if lib.s2_session_minigame_state(h)==0:break
  assert lib.s2_session_minigame_state(h)==0
 finally:lib.s2_session_destroy(h)

report=dict(native_frames=frames,region_fixtures=17,changed_types=sorted(changed),fixture_coins=coins,fixture_deaths=deaths,states=sorted(states),sound_ids=sorted(sounds),same_native_owner_on_chapter_change=True,donkey_hud_source_pixels=True,failed_load_atomic=True,damage_and_immunity=True,exit_zone_dialogue_and_victory=True,ignored_original_marker_events=3,bonus_entry_and_return=True,mismatches=0,device_tested=False,scope='Original chapter01 resources with relocated-player fixtures and a relocated leprechaun physical B-talk fixture. Does not certify full-route completion: complete route remains unverified; invisible marker events33..36 are ignored by original Donkey receiver.')
(ROOT/'docs/donkey_chapter_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
