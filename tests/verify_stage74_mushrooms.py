#!/usr/bin/env python3
"""Actual input/physics: Donkey kicks mushrooms; does not capture them as props."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP])]:getattr(l,'s2_session_'+n).argtypes=a
rows=json.loads((R/'objects/scene_01/objects.json').read_text())['objects'];pix=(C.c_uint32*38400)();info=(I*8)();state=(I*320)();actor=(I*216)();runs=[]
with tempfile.TemporaryDirectory()as td:
 for typ in [14,16]:
  for position in ['side','aligned','above']:
   for button in [2,4]:
    d=bytearray((R/'objects/scene_01/scene.s2ob').read_bytes());item=next(r for r in rows if r['type']==typ)
    for row in rows:
     if row['type'] in [151,53,57,94,101]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
    hero=(3366,310 if position=='above'else 344);xy=(3352 if position=='side'else 3367,344)
    struct.pack_into('<HH',d,18,*hero);struct.pack_into('<HH',d,18+(item['instance_id']-1)*44,*xy);p=Path(td)/'objects.s2ob';p.write_bytes(d);err=I()
    paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/'extracted/scene_01/scene.s2lv',R/'collision/scene_01/scene.s2cl',R/'android/app/src/main/assets/session/sprites',p];h=l.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert h,err.value
    try:
     before=after=None;action=None
     for t in range(110):
      e=l.s2_session_step(h,button if t==20 else 0,pix,len(pix),info);assert e==0,(typ,position,button,t,e)
      l.s2_session_snapshot(h,state);l.s2_session_actor_snapshot(h,item['instance_id'],actor)
      assert state[83]==0 and state[102]==0,(typ,position,button,t,'unexpected carried/lifted platform')
      if t==19:before=actor[0]
      if t==20:action=state[80];assert button!=2 or action!=8,'B incorrectly routed through Select grab'
      if t==109:after=actor[0]
     movement=abs(after-before)/256
     if position=='side':assert movement>30 if button==2 else movement<1,(typ,button,movement)
     runs.append(dict(type=typ,position=position,input='B'if button==2 else'Select',action=action,displacement_px=movement,carried=False))
    finally:l.s2_session_destroy(h)
report=dict(runs=runs,mismatches=0,device_tested=False,scope='Relocated real scene01 mushroom/stump and Donkey; source collision, animations, kick events and target scripts. Side, aligned and above spawns; 110 frames per input. Key/fairy ownership regression is checked separately.')
(R/'docs/stage74_mushrooms_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
