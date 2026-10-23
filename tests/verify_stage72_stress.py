#!/usr/bin/env python3
"""Deterministic physical-input smoke runs; no claim of route completion."""
import ctypes as C,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;l=C.CDLL(str(R/'native/build/libshrek_scene.so'));l.s2_session_create_level.argtypes=[C.c_char_p]*5+[C.POINTER(I)];l.s2_session_create_level.restype=P;l.s2_session_step.argtypes=[P,I,P,C.c_size_t,C.POINTER(I)];l.s2_session_destroy.argtypes=[P];l.s2_session_dialogue_snapshot.argtypes=[P,C.POINTER(I)]
results=[]
for scene in [0,1]:
 paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',R/f'objects/scene_{scene:02}/scene.s2ob'];err=I();h=l.s2_session_create_level(*[str(p).encode()for p in paths],C.byref(err));assert h,err.value;pix=(C.c_uint32*38400)();info=(I*8)();dlg=(I*80)();rng=random.Random(72+scene);held=0;duration=0
 try:
  for t in range(2000):
   l.s2_session_dialogue_snapshot(h,dlg)
   if dlg[64]:b=64 if t%2 else 0
   else:
    if duration<=0:held=rng.choice([0,0,16,17,18,32,33,34,1,2,3,4,128]);duration=rng.randrange(1,14)
    duration-=1;b=held
   e=l.s2_session_step(h,b,pix,len(pix),info);assert e==0,(scene,t,b,e,list(info))
  results.append(dict(scene=scene,seed=72+scene,frames=2000,result='pass'))
 finally:l.s2_session_destroy(h)
report=dict(runs=results,device_tested=False,scope='Bounded random inputs on source placements, dialogue skip and death restarts. Does not establish complete-route correctness or exclude all hangs.');(R/'docs/stage72_stress_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
