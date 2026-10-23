#!/usr/bin/env python3
"""Key ownership, B dialogue/attack and Select drop, event-log stress and party-switch regression. No Android device."""
import ctypes as C,json,struct,tempfile,random
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'))
for prefix,items in [('frontend',[('create',[C.c_char_p]*2),('destroy',[P]),('open',[P,I,I]),('step',[P,I]),('snapshot',[P,IP]),('action',[P]),('render',[P,P,C.c_size_t]),('text_boxes',[P,IP,I]),('initials',[P,I,C.c_char_p])]),('session',[('create_level',[C.c_char_p]*5+[IP]),('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('dialogue_snapshot',[P,IP]),('player_event',[P,IP]),('player_type',[P])])]:
 for name,args in items:getattr(l,'s2_'+prefix+'_'+name).argtypes=args
l.s2_frontend_create.restype=P;l.s2_session_create_level.restype=P
pix=(C.c_uint32*38400)();st=(I*9)();info=(I*8)();state=(I*320)();report={'device_tested':False}
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
    if row['type'] in [151,46,53,55,57,59,60,61,62,63,64,65,66,94,101,104] or (76<=row['type']<=85 and row['instance_id']!=key['instance_id']):struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
   struct.pack_into('<H',d,16+(hero['instance_id']-1)*44,typ)
   for row,xy in [(hero,(2137,211)),(key,(2141,207))]+([(npc,(2137,211))]if talk else []):struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,*xy)
   obj=Path(td)/'key.s2ob';obj.write_bytes(d);err=I();h=l.s2_session_create_level(*paths(1,obj),C.byref(err));assert h,err.value
   try:
    for t in range(420):s=step(h,4 if t==250 else 0)
    assert s[83]==key['instance_id'] and s[81]==6,(typ,talk,s[80:88])
    if talk:
     step(h,2);step(h);dlg=(I*80)();l.s2_session_dialogue_snapshot(h,dlg);assert dlg[64] and state[83]==key['instance_id'],(typ,list(dlg),list(state[80:88]));step(h,64);step(h)
    else:
     step(h,2);assert state[83]==key['instance_id']
     for _ in range(90):step(h)
     step(h,4)
     for _ in range(90):step(h)
     assert state[83]==0
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
  original=l.s2_session_player_type(h);step(h,512);changed=l.s2_session_player_type(h);step(h);step(h,256);assert l.s2_session_player_type(h)==original and original!=changed,(sc,original,changed);party.append({'scene':sc,'from':original,'to':changed})
 finally:l.s2_session_destroy(h)
report['experimental_party_switch']=party
(R/'docs/stage74_ownership_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
