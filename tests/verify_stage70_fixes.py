#!/usr/bin/env python3
"""Physical Donkey pickup/release and intro sound. Viewport coverage is separate."""
import ctypes as C,json,struct,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I)
l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,args in [('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('set_viewport',[P,I,I]),('dialogue_active',[P]),('audio_since',[P,I,IP,C.c_size_t,IP]),('player_event',[P,IP]),('dialogue_snapshot',[P,IP])]:getattr(l,'s2_session_'+n).argtypes=args
rom=Path(sys.argv[1]).read_bytes();rows=json.loads((ROOT/'objects/scene_01/objects.json').read_text())['objects'];runs=[]
def create(scene,objects=None,width=240):
 err=I();h=l.s2_session_create_level(*[str(x).encode()for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/f'extracted/scene_{scene:02}/scene.s2lv',ROOT/f'collision/scene_{scene:02}/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',objects or ROOT/f'objects/scene_{scene:02}/scene.s2ob']],C.byref(err));assert h,err.value;l.s2_session_set_viewport(h,width,160);return h
def step(h,b,width=240):
 info=(I*8)();pix=(C.c_uint32*(width*160))();e=l.s2_session_step(h,b,pix,len(pix),info);assert e==0,(e,list(info));s=(I*320)();l.s2_session_snapshot(h,s);return s
with tempfile.TemporaryDirectory()as td:
 f=Path(td)/'objects.s2ob'
 for kind in [14,16]:
  for key in [4,2]:
   for finish in ['B_drop','damage_drop']:
    d=bytearray((ROOT/'objects/scene_01/scene.s2ob').read_bytes());item=next(x for x in rows if x['type']==kind)
    for row in rows:
     if row['type'] in [151,53,57,94,101]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
    struct.pack_into('<HH',d,18,3366,344);struct.pack_into('<HH',d,18+(item['instance_id']-1)*44,3367,344);f.write_bytes(d);h=create(1,f);captured=None
    try:
     for t in range(100):
      s=step(h,key if t==20 else 16 if t>=65 else 0)
      if t<20:assert s[83]==0,'unrequested automatic pickup'
      if s[83]==item['instance_id'] and captured is None:captured=t
     assert captured is not None,(kind,key,finish,list(s[80:104]))
     a=(I*216)();l.s2_session_actor_snapshot(h,item['instance_id'],a);assert abs(a[0]-s[0])<8*256,'held prop does not follow Donkey'
     if finish=='B_drop':s=step(h,2)
     else:assert l.s2_session_player_event(h,(I*3)(1,38,1))==1;s=step(h,0)
     assert s[83]==0,(kind,key,finish,'ownership not released')
     for t in range(80):step(h,0)
     runs.append(dict(type=kind,input='Select'if key==4 else'B',captured_frame=captured,release=finish))
    finally:l.s2_session_destroy(h)
# Completing scene01's source dialogue3 emits its HUD descriptor's sound83 once;
# skipping it must remain silent and closingA cannot become an immediate jump.
for skip in [False,True]:
 h=create(1);closed=None
 try:
  for t in range(1000):
   active=bool(l.s2_session_dialogue_active(h));b=64 if skip and active and t%8==2 else 1 if not skip and active and t%8==2 else 0;s=step(h,b)
   if active and not l.s2_session_dialogue_active(h):
    closed=t;assert s[80]not in [2,3,4,7,16]
   if closed is not None and t>closed+30:break
  assert closed is not None
  audio=(I*(4096*3))();cursor=I();n=l.s2_session_audio_since(h,0,audio,4096,C.byref(cursor));assert n>=0
  ids=[audio[i*3]for i in range(n)];assert ids.count(83)==(0 if skip else 1),(skip,ids)
  assert struct.unpack_from('<3i',rom,0x53d5c)==(83,-100,200)
 finally:l.s2_session_destroy(h)
report=dict(donkey_pickup_runs=runs,donkey_intro_sound=83,intro_skip_silent=True,mismatches=0,device_tested=False,scope='Native physical pickup fixtures relocate hero/props and suppress intro/nearby hostiles. Actual inputs, source target event10 and detach11, movement/follow, B and damage release. Original scene01 dialogue and source HUD sound descriptor. Enemy viewport activation covered in Stage57 presentation; not full chapter/device validation.')
(ROOT/'docs/stage70_fixes_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
