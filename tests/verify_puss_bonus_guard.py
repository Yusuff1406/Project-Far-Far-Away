#!/usr/bin/env python3
"""Physical Puss leprechaun conversation never enters another hero's bonus."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;IP=C.POINTER(I);P=C.c_void_p;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('destroy',[P]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('minigame_state',[P]),('player_type',[P])]:getattr(l,'s2_session_'+n).argtypes=a
rows=json.loads((ROOT/'objects/scene_23/objects.json').read_text())['objects'];raw=bytearray((ROOT/'objects/scene_23/scene.s2ob').read_bytes());hero=next(r for r in rows if r['type']==4);npc=next(r for r in rows if r['type']==94)
# Explicit fixture: put the original leprechaun near the source start;
# move the intro, other NPC and hostile actors out of the interaction area.
for r in rows:
 if r['type']==94:x,y=873,1721
 elif r['type']==151 or 53<=r['type']<=62 or 91<=r['type']<=111:x,y=12000,0
 else:continue
 struct.pack_into('<HH',raw,18+(r['instance_id']-1)*44,x,y)
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'objects.s2ob';p.write_bytes(raw);err=I();h=l.s2_session_create_level(*[str(x).encode()for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_23/scene.s2lv',ROOT/'collision/scene_23/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',p]],C.byref(err));assert h,err.value
 pix=(C.c_uint32*38400)();info=(I*8)();seen=False
 try:
  for tick in range(500):
   held=2 if tick==40 else 64 if tick>60 and tick%2==0 else 0
   e=l.s2_session_step(h,held,pix,len(pix),info);assert e==0,(tick,e,list(info))
   state=l.s2_session_minigame_state(h);assert state not in [1,2],('wrong bonus',tick,state)
   if state==3:seen=True;break
  assert seen,'Puss bonus request not reached'
  assert l.s2_session_step(h,0,pix,len(pix),info)==0
  assert l.s2_session_step(h,1,pix,len(pix),info)==0
  assert l.s2_session_minigame_state(h)==0 and l.s2_session_player_type(h)==4
 finally:l.s2_session_destroy(h)
report=dict(source_scene=23,source_dialogue=npc['word8_actor_tag'],unavailable_screen_reached=True,returned_to_puss=True,wrong_hero_bonus_started=False,mismatches=0,scope='Physical interaction fixture with relocated NPC/intro/hostiles; source Puss mini-game remains unported.')
(ROOT/'docs/puss_bonus_guard_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
