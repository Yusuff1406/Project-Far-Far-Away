#!/usr/bin/env python3
"""More than256 legitimate coin/audio requests must survive a longer session."""
import ctypes,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for n,a in [('player_event',[ctypes.c_void_p,IP]),('requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('audio_since',[ctypes.c_void_p,I,IP,ctypes.c_size_t,IP]),('destroy',[ctypes.c_void_p])]:getattr(l,'s2_session_'+n).argtypes=a
 p=ROOT/'android/app/src/main/assets/session';paths=[p/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',p/'sprites',ROOT/'objects/scene_00/scene.s2ob'];err=I();h=create(*[str(x).encode()for x in paths],ctypes.byref(err));assert h,err.value
 try:
  cursor=I();audio=(I*12)();ids=[]
  for _ in range(300):
   assert l.s2_session_player_event(h,(I*3)(0,32,0))==1;n=l.s2_session_audio_since(h,cursor.value,audio,4,ctypes.byref(cursor));assert n==1;ids.append(audio[0])
  rows=(I*(1024*8))();count=l.s2_session_requests(h,rows,1024);assert count==600 and cursor.value==600 and len(set(ids))==1
 finally:l.s2_session_destroy(h)
 report=dict(accepted_coin_events=300,retained_requests=600,duplicate_sounds=0,mismatches=0,scope='Public owner coin event route, source descriptor and normal audio cursor read after each event. No forced raw queue writes. Ensures new bonus effects do not hit former256-entry history cap. New bounded history4096, not an unbounded world manager.');(ROOT/'docs/request_history_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
