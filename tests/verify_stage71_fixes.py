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
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,args in [('open',[P,I,I]),('step',[P,I]),('snapshot',[P,IP]),('presentation',[P,IP]),('render',[P,P,C.c_size_t]),('text_boxes',[P,IP,I]),('destroy',[P]),('action',[P])]:getattr(l,'s2_frontend_'+n).argtypes=args
h=l.s2_frontend_create(str(ROOT/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(ROOT/'sprites/bank_328294/bank.s2sp').encode());assert h
try:
 l.s2_frontend_open(h,11,0);frames=[]
 for t in range(200):
  l.s2_frontend_render(h,pix,len(pix));frames.append(bytes(pix));l.s2_frontend_step(h,0)
 assert len(set(frames[:121]))==1 and frames[160]!=frames[0]
 for _ in range(210):l.s2_frontend_step(h,0)
 st=(I*9)();l.s2_frontend_snapshot(h,st);assert st[0]==11 and st[1]==0,'legal movie truncated'
 l.s2_frontend_open(h,8,0)
 for t in range(100):
  l.s2_frontend_render(h,pix,len(pix));boxes=(I*800)();assert l.s2_frontend_text_boxes(h,boxes,100)>0,('blank credits',t)
  l.s2_frontend_step(h,0)
 Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/stage71_credits_live.png')
 l.s2_frontend_open(h,3,0)
 for _ in range(36):l.s2_frontend_step(h,0)
 l.s2_frontend_render(h,pix,len(pix));Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/stage71_candle_white.png')
 for t in range(78):
  l.s2_frontend_render(h,pix,len(pix));neutral=0
  for y in range(51,67):
   for x in range(203,217):
    v=pix[y*240+x];rgb=[(v>>shift)&255 for shift in [16,8,0]]
    if min(rgb)>230 and max(rgb)-min(rgb)<8:neutral+=1
  assert neutral>3,('white candle',t,neutral)
  l.s2_frontend_step(h,0)
 report['white_candle_frames_checked']=78
 l.s2_frontend_open(h,5,0);l.s2_frontend_step(h,1);present=(I*8)();l.s2_frontend_presentation(h,present);assert present[2]==0
 l.s2_frontend_step(h,0);l.s2_frontend_step(h,2);l.s2_frontend_presentation(h,present);assert present[2]==0
 l.s2_frontend_step(h,0);l.s2_frontend_step(h,8);assert l.s2_frontend_action(h)==2
finally:l.s2_frontend_destroy(h)
report.update(legal_hold_ticks=120,legal_full_movie=True,credits_visible_from_entry=True,pause_no_internal_fade=True,mismatches=0)
(ROOT/'docs/stage71_fixes_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
