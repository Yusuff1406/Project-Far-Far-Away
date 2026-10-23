#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Damage delivered through owner event API; complete native frame/reset replay."""
import ctypes,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p;lib.s2_session_set_auto_restart.argtypes=[ctypes.c_void_p,I]
 for n,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_health',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_player_event',[ctypes.c_void_p,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(lib,n).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',fixture_scene(ROOT/'objects/scene_00/scene.s2ob')]
 references=None;frames=0;transitions=[]
 for width in [240,480]:
  err=I();h=create(*[str(p).encode()for p in paths],ctypes.byref(err));assert h and err.value==0;lib.s2_session_set_auto_restart(h,0)
  assert lib.s2_session_set_viewport(h,width,160)==0
  try:
   for replay in range(2):
    if replay:assert lib.s2_session_reset(h)==0
    assert lib.s2_session_health(h)==6
    pixels=(ctypes.c_uint32*(width*160))();info=(I*8)();state=(I*320)();trace=[];last=-1
    for tick in range(720):
     if tick in [0,120,240,360,480,600]:
      assert lib.s2_session_player_event(h,(I*3)(1,38,1))==1
      assert lib.s2_session_health(h)==5-tick//120
      assert lib.s2_session_snapshot(h,state)==0
      assert state[80]==6 and state[95]==tick+30 and state[92]==tick+78
      assert lib.s2_session_player_event(h,(I*3)(1,38,1))==0
     assert lib.s2_session_step(h,0,pixels,len(pixels),info)==0,(width,replay,tick,list(info))
     assert lib.s2_session_snapshot(h,state)==0
     trace.append(list(state));frames+=1
     if state[80]!=last:
      if width==240 and replay==0:transitions.append([tick+1,state[80]])
      last=state[80]
    assert lib.s2_session_health(h)==0 and state[80]==13
    if references is None:references=trace
    else:assert trace==references,(width,replay)
  finally:lib.s2_session_destroy(h)
 assert lib.s2_session_health(None)==-1
 report={'native_frame_comparisons':frames,'state_words_per_frame':320,'viewports':[240,480],'replays_per_viewport':2,'phase_transitions':transitions,'mismatches':0,'scope':'Six damage events via owner API, repeated-hit rejection, primary hurt recovery/death, real native physics/render and reset. Damage is explicitly injected through event delivery, not physical enemy contact; full game-over, auxiliary flashing and Android/device excluded.'}
 (ROOT/'docs/session_hurt_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
