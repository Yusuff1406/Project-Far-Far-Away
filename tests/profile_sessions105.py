#!/usr/bin/env python3
"""Paired host CPU timings, excludes Android/JNI/Canvas. No phone FPS claims."""
import ctypes as C,csv,statistics,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
libs=[C.CDLL(str(Path(p).resolve())) for p in sys.argv[1:3]];assert len(libs)==2
I=C.c_int;P=C.c_void_p
for l in libs:
 l.s2_session_create_level.argtypes=[C.c_char_p]*5+[C.POINTER(I)];l.s2_session_create_level.restype=P
 l.s2_session_destroy.argtypes=[P];l.s2_session_set_viewport.argtypes=[P,I,I];l.s2_session_update.argtypes=[P,I,P,C.c_size_t,P,I];l.s2_session_present.argtypes=[P,I,P,C.c_size_t];l.s2_session_debug_edit.argtypes=[P,I,I,I,I]
w=csv.writer(sys.stdout);w.writerow(['scene','width','samples','before_p50_us','after_p50_us','before_p95_us','after_p95_us'])
def pct(v,p):return sorted(v)[int((len(v)-1)*p)]
for scene in range(30):
 for width in [240,356,640]:
  paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',R/f'objects/scene_{scene:02}/scene.s2ob']
  hs=[l.s2_session_create_level(*[str(p).encode() for p in paths],C.byref(I())) for l in libs];assert all(hs)
  for l,h in zip(libs,hs):assert not l.s2_session_set_viewport(h,width,160);assert not l.s2_session_debug_edit(h,6,1,0,0)
  pixels=[(C.c_uint32*(width*160))() for _ in libs];info=[(I*8)() for _ in libs];values=[[],[]]
  for t in range(240):
   buttons=(64 if t%8==2 else 0)|(16 if t>40 else 0)|(1 if t%29==25 else 0)
   for k in ([0,1] if t%2 else [1,0]):
    l=libs[k];h=hs[k];start=time.thread_time_ns();e=l.s2_session_update(h,buttons,pixels[k],width*160,info[k],1)
    if not e:e=l.s2_session_present(h,128,pixels[k],width*160)
    duration=(time.thread_time_ns()-start)/1000;assert not e
    if t>=40:values[k].append(duration)
  w.writerow([scene,width,len(values[0]),pct(values[0],.5),pct(values[1],.5),pct(values[0],.95),pct(values[1],.95)]);sys.stdout.flush()
  for l,h in zip(libs,hs):l.s2_session_destroy(h)
