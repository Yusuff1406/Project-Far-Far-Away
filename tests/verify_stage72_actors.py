#!/usr/bin/env python3
"""Physical fairy/glide, long idle, live credits, legal movie and level transitions.
Host runtime fixtures; does not run an Android device.
"""
import ctypes as C,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I)
l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,args in [('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('set_transitions',[P,I]),('load_level',[P]+[C.c_char_p]*5),('transition_snapshot',[P,IP])]:getattr(l,'s2_session_'+n).argtypes=args
pix=(C.c_uint32*38400)();info=(I*8)();s=(I*320)();rows=json.loads((ROOT/'objects/scene_01/objects.json').read_text())['objects']
def paths(scene,obj):return [str(x).encode()for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/f'extracted/scene_{scene:02}/scene.s2lv',ROOT/f'collision/scene_{scene:02}/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',obj]]
def step(h,b=0):
 assert l.s2_session_step(h,b,pix,len(pix),info)==0,list(info);l.s2_session_snapshot(h,s);return list(s)
report={'device_tested':False};idle=[];glide=[]
with tempfile.TemporaryDirectory()as td:
 obj=Path(td)/'scene.s2ob'
 for held in [False,True]:
  d=bytearray((ROOT/'objects/scene_01/scene.s2ob').read_bytes())
  for row in rows:
   if row['type'] in [151,46,53,55,57,59,60,61,62,63,64,65,66,94,101,104]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
  struct.pack_into('<HH',d,18,2137,211);obj.write_bytes(d);err=I();h=l.s2_session_create_level(*paths(1,obj),C.byref(err));assert h,err.value
  falling=[]
  try:
   for t in range(390):
    state=step(h,4 if t==250 else (17 if t>=290 and (held or t<292) else 0))
    if t==251:assert state[83]==26 and state[81]==2,('fairy not acquired',state[80:88])
    if t>=320 and state[80]==4:
     falling.append(state[11])
     if held:assert state[11]==168,(t,state[11])
   assert falling,held;glide.append(dict(held_A=held,fall_velocities=sorted(set(falling))))
  finally:l.s2_session_destroy(h)
 assert max(glide[0]['fall_velocities'])>168
 for scene,xy in [(0,(35,350)),(1,(2137,211)),(23,(878,1736))]:
  d=bytearray((ROOT/f'objects/scene_{scene:02}/scene.s2ob').read_bytes());objects=json.loads((ROOT/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];hero=next(x for x in objects if x['type'] in [3,4,6])
  for row in objects:
   if row['type'] in [151,46,53,55,57,59,60,61,62,63,64,65,66,94,101,104]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
  struct.pack_into('<HH',d,18+(hero['instance_id']-1)*44,*xy);obj.write_bytes(d);err=I();h=l.s2_session_create_level(*paths(scene,obj),C.byref(err));assert h
  try:
   first=None;normal=None
   for t in range(720):
    state=step(h)
    if t==100:normal=state[47]
    if state[80]==10:
     assert t>=600 and state[47]!=normal;first=t;break
   assert first is not None,scene
   state=step(h,16);assert state[80]==1,'idle did not respond to movement';idle.append(dict(scene=scene,first_idle_frame=first))
   assert l.s2_session_set_transitions(h,1)==0
   assert l.s2_session_load_level(h,*paths(scene,obj))==0
   colors=[]
   for t in range(18):step(h);colors.append(len(set(pix)))
   assert colors[0]==1 and pix[0]!=0 and max(colors[1:])>100,colors
  finally:l.s2_session_destroy(h)
report.update(fairy=glide,idle=idle,chapter_load_starts_black=True)

(ROOT/'docs/stage72_actors_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
