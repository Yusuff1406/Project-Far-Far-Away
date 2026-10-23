#!/usr/bin/env python3
"""Compare public engine state, audio and pixels before/after renderer-only changes."""
import ctypes as C,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=R.parent
libs=[C.CDLL(str(Path(p).resolve())) for p in sys.argv[1:]]
assert len(libs)==2
I=C.c_int;P=C.c_void_p
for l in libs:
 l.s2_session_create_level.argtypes=[C.c_char_p]*5+[C.POINTER(I)];l.s2_session_create_level.restype=P
 l.s2_session_destroy.argtypes=[P]
 l.s2_session_set_viewport.argtypes=[P,I,I]
 l.s2_session_update.argtypes=[P,I,C.c_void_p,C.c_size_t,C.c_void_p,I]
 l.s2_session_present.argtypes=[P,I,C.c_void_p,C.c_size_t]
 l.s2_session_snapshot.argtypes=[P,C.c_void_p]
 l.s2_session_audio_since.argtypes=[P,I,C.c_void_p,C.c_size_t,C.c_void_p]
 l.s2_session_debug_edit.argtypes=[P,I,I,I,I]
 l.s2_session_save_state.argtypes=[P,C.c_char_p]
frames=0
for scene in range(30):
 for width in [240,356,640]:
  paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',R/f'objects/scene_{scene:02}/scene.s2ob']
  hs=[l.s2_session_create_level(*[str(p).encode() for p in paths],C.byref(I())) for l in libs];assert all(hs)
  for l,h in zip(libs,hs):assert not l.s2_session_set_viewport(h,width,160);assert not l.s2_session_debug_edit(h,6,1,0,0)
  pixels=[(C.c_uint32*(width*160))() for _ in libs];state=[(I*320)() for _ in libs];info=[(I*8)() for _ in libs];cursors=[0,0]
  for t in range(100):
   buttons=(64 if t%8==2 else 0)|(16 if t>40 else 0)|(1 if t%29==25 else 0)
   sounds=[]
   for k,(l,h) in enumerate(zip(libs,hs)):
    assert not l.s2_session_update(h,buttons,pixels[k],width*160,info[k],1)
    assert not l.s2_session_snapshot(h,state[k])
    audio=(I*3072)();nxt=I();n=l.s2_session_audio_since(h,cursors[k],audio,1024,C.byref(nxt));assert n>=0;cursors[k]=nxt.value;sounds.append(list(audio[:3*n]))
   assert bytes(state[0])==bytes(state[1]) and bytes(info[0])==bytes(info[1]) and sounds[0]==sounds[1],(scene,width,t,'state/audio')
   for alpha in ([0,128,256] if t%11==0 else [128]):
    for l,h,p in zip(libs,hs,pixels):assert not l.s2_session_present(h,alpha,p,width*160)
    assert bytes(pixels[0])==bytes(pixels[1]),(scene,width,t,alpha,'pixels')
    frames+=1
  for l,h in zip(libs,hs):l.s2_session_destroy(h)
  print('PASS',scene,width,flush=True)
print('PASS',frames,'display frames; 9000 updates, 30 scenes x3 widths; state/audio and pixels exact')
