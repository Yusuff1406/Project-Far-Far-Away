#!/usr/bin/env python3
"""Source death scripts may request coins, health, shield or carryable items."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;IP=C.POINTER(I);P=C.c_void_p;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('destroy',[P]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('actor_event',[P,I,IP]),('actor_snapshot',[P,I,IP]),('set_auto_restart',[P,I]),('requests',[P,IP,C.c_size_t])]:getattr(l,'s2_session_'+n).argtypes=a
results=[];pix=(C.c_uint32*38400)();info=(I*8)();actor=(I*216)()
with tempfile.TemporaryDirectory()as td:
 for scene,enemy,drop in [(14,59,77),(14,59,83),(14,59,84),(14,59,90),(21,53,82)]:
  rows=json.loads((ROOT/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];target=next(x for x in rows if x['type']==enemy and x['secondary_type_s16']==drop);hero=next(x for x in rows if x['type']==6);d=bytearray((ROOT/f'objects/scene_{scene:02}/scene.s2ob').read_bytes());x,y=target['anchor_px'];struct.pack_into('<HH',d,18+(hero['instance_id']-1)*44,x-24,y)
  for row in rows:
   if row['type']==151 or(53<=row['type']<=60 and row['instance_id']!=target['instance_id']):struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,12000,0)
  p=Path(td)/'objects.s2ob';p.write_bytes(d);err=I();paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/f'extracted/scene_{scene:02}/scene.s2lv',ROOT/f'collision/scene_{scene:02}/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',p];h=l.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert h,err.value;l.s2_session_set_auto_restart(h,0)
  try:
   hits=0
   for t in range(600):
    l.s2_session_actor_snapshot(h,target['instance_id'],actor)
    if t in [20,100,180,260]and actor[52]>0 and not(actor[40]&1):assert l.s2_session_actor_event(h,target['instance_id'],(I*3)(3,2,1))==1;hits+=1
    assert l.s2_session_step(h,0,pix,len(pix),info)==0,(scene,drop,t,list(info))
   data=(I*(4096*8))();n=l.s2_session_requests(h,data,4096);assert n>=0;births=[list(data[i*8:i*8+8])for i in range(n)if data[i*8+1]==24];assert any(x[4]==drop for x in births),(scene,drop,hits,list(actor[39:54]),births)
   results.append(dict(scene=scene,enemy_type=enemy,secondary_type=drop,hits=hits,spawn_requests=births))
  finally:l.s2_session_destroy(h)
report=dict(runs=results,mismatches=0,scope='Relocated player and other hostiles suppressed; actual source death scripts activated using original Donkey event3/2 until health reaches0. Checks factory request and owned creation of77/82/83/84/90. Does not certify all Donkey carry/power-up actions.')
(ROOT/'docs/world_drops_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
