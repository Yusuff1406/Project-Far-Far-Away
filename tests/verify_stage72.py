#!/usr/bin/env python3
"""Stage72 real native frontend/scene regression fixtures. No Android device."""
import ctypes as C,json,struct,tempfile,random
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'))
for prefix,items in [('frontend',[('create',[C.c_char_p]*2),('destroy',[P]),('open',[P,I,I]),('step',[P,I]),('snapshot',[P,IP]),('action',[P]),('render',[P,P,C.c_size_t]),('text_boxes',[P,IP,I]),('initials',[P,I,C.c_char_p])]),('session',[('create_level',[C.c_char_p]*5+[IP]),('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('dialogue_snapshot',[P,IP]),('player_event',[P,IP]),('player_type',[P])])]:
 for name,args in items:getattr(l,'s2_'+prefix+'_'+name).argtypes=args
l.s2_frontend_create.restype=P;l.s2_session_create_level.restype=P
pix=(C.c_uint32*38400)();st=(I*9)();info=(I*8)();state=(I*320)();report={'device_tested':False}
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h

def frames(n,b=0):
 for _ in range(n):assert l.s2_frontend_step(h,b)==0

def press(b):frames(1,b);frames(40)
def snap():l.s2_frontend_snapshot(h,st);return list(st)
def shot(name):
 assert l.s2_frontend_render(h,pix,len(pix))==0
 Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/f'previews/stage72_{name}.png')
try:
 l.s2_frontend_open(h,5,0);press(1);assert l.s2_frontend_action(h)==2
 l.s2_frontend_open(h,5,1);press(1);assert l.s2_frontend_action(h)==3
 l.s2_frontend_open(h,2,0);press(1);assert snap()[0]==13;assert l.s2_frontend_action(h)==0
 press(1);press(16);press(1);press(16);press(1);assert snap()[1]==31;shot('initials');press(1);assert snap()[0]==12;assert l.s2_frontend_action(h)==7
 name=C.create_string_buffer(4);assert l.s2_frontend_initials(h,0,name)==0;assert name.value==b'ABC';frames(100);shot('caption')
 l.s2_frontend_open(h,8,0);boxes=(I*800)();shot('credits_entry');assert l.s2_frontend_text_boxes(h,boxes,100)==0
 frames(200);shot('credits');assert l.s2_frontend_text_boxes(h,boxes,100)>0
 press(2);assert snap()[0]==8
 frames(20,1);shot('credits_fast');press(8);assert snap()[0]==1
 l.s2_frontend_open(h,11,0);shot('legal_hold');first=bytes(pix);frames(120);l.s2_frontend_render(h,pix,len(pix));assert bytes(pix)==first;frames(45);l.s2_frontend_render(h,pix,len(pix));assert bytes(pix)!=first
 l.s2_frontend_open(h,4,0);shot('chapter_footer');l.s2_frontend_open(h,3,0);shot('candle')
 l.s2_frontend_open(h,9,0);press(1);assert snap()[0]==6 and snap()[1]==0;shot('erase');press(1);assert snap()[0]==9;assert l.s2_frontend_action(h)==0
 press(1);press(128);press(1);assert l.s2_frontend_action(h)==6
 report['frontend']={'resume':True,'quit_level':True,'initials':'ABC','erase_cancel_default':True,'credits_start_exit_A_held':True,'legal_visible_hold':True}
finally:l.s2_frontend_destroy(h)
def paths(scene,obj=None):return [str(x).encode()for x in [R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',obj or R/f'objects/scene_{scene:02}/scene.s2ob']]
def step(h,b=0):
 e=l.s2_session_step(h,b,pix,len(pix),info);assert e==0,(e,list(info));l.s2_session_snapshot(h,state);return list(state)
with tempfile.TemporaryDirectory()as td:
 rows=json.loads((R/'objects/scene_01/objects.json').read_text())['objects'];key=next(x for x in rows if x['type']==76);hero=next(x for x in rows if x['type']==6);npc=next(x for x in rows if x['type']==94)
 fixtures=[]
 for typ in [3,6]:
  for talk in [False,True]:
   d=bytearray((R/'objects/scene_01/scene.s2ob').read_bytes())
   for row in rows:
    if row['type'] in [151,46,53,55,57,59,60,61,62,63,64,65,66,94,101,104]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
   struct.pack_into('<H',d,16+(hero['instance_id']-1)*44,typ)
   for row,xy in [(hero,(2137,211)),(key,(2141,207))]+([(npc,(2137,211))]if talk else []):struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,*xy)
   obj=Path(td)/'key.s2ob';obj.write_bytes(d);err=I();h=l.s2_session_create_level(*paths(1,obj),C.byref(err));assert h,err.value
   try:
    for t in range(420):s=step(h,4 if t in [250,300] else 0)
    assert s[83]==key['instance_id'] and s[81]==6,(typ,talk,s[80:88])
    if talk:
     step(h,2);step(h);dlg=(I*80)();l.s2_session_dialogue_snapshot(h,dlg);assert dlg[64] and state[83]==key['instance_id'],(typ,list(dlg),list(state[80:88]));step(h,64);step(h)
    else:
     step(h,2);assert state[83]==0
     for _ in range(4200):assert l.s2_session_player_event(h,(I*3)(0,32,0))>=0
     step(h)
    fixtures.append({'hero':typ,'talk_with_key':talk,'result':'pass'})
   finally:l.s2_session_destroy(h)
 report['key_fixtures']=fixtures
party=[]
for sc in [2,13]:
 err=I();h=l.s2_session_create_level(*paths(sc),C.byref(err));assert h,(sc,err.value)
 try:
  for _ in range(60):step(h,64 if _%2 else 0)
  original=l.s2_session_player_type(h);step(h,256);changed=l.s2_session_player_type(h);step(h);step(h,512);assert l.s2_session_player_type(h)==original and original!=changed,(sc,original,changed);party.append({'scene':sc,'from':original,'to':changed})
 finally:l.s2_session_destroy(h)
report['experimental_party_switch']=party
(R/'docs/stage72_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
