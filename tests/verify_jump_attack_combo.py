#!/usr/bin/env python3
"""Compatibility test of the older general-player fixture; production stomp is tested separately."""
import ctypes,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p
 for name,types in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t])]:getattr(lib,name).argtypes=types
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];err=ctypes.c_int32();hs=[create(*paths,ctypes.byref(err)) for _ in range(2)];assert all(hs);states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];bufs=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*38400)()];info=(ctypes.c_int32*8)();images=[];airTicks=[];compared=0
 try:
  for replay in range(2):
   if replay:
    for h in hs:assert lib.s2_session_reset(h)==0
   for tick in range(1,181):
    for k,h in enumerate(hs):
     held=(3 if tick<=30 else 0) if k==0 else (1 if tick==1 else 3 if 2<=tick<=30 else 0)
     assert lib.s2_session_step(h,held,bufs[k],len(bufs[k]),info)==0,(tick,k,list(info));lib.s2_session_snapshot(h,states[k])
    assert bytes(states[0])==bytes(states[1]) and bytes(bufs[0])==bytes(bufs[1]),(tick,'manual input differs');compared+=1
    if states[0][80]==16:airTicks.append([replay,tick,hex(states[0][47])])
    if replay==0 and tick%3==0:images.append(Image.frombytes('RGBA',(240,160),bytes(bufs[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
   assert states[0][80] in (0,1,5)
  assert airTicks and all(row[2]=='0x834f304' for row in airTicks)
  # Midair combo skips an extra jump, as the ordinary attack does.
  for h in hs:lib.s2_session_reset(h)
  for tick in range(1,121):
   for k,h in enumerate(hs):
    held=1 if tick==1 else 3 if tick==5 else 0;assert lib.s2_session_step(h,held,bufs[k],len(bufs[k]),info)==0;lib.s2_session_snapshot(h,states[k])
   assert bytes(states[0])==bytes(states[1]) and bytes(bufs[0])==bytes(bufs[1]);compared+=1
  # Walking A+B preserves direction and equals jump, then attack.
  for h in hs:lib.s2_session_reset(h)
  for tick in range(1,181):
   for k,h in enumerate(hs):
    held=16|(3 if 41<=tick<=60 else 0)
    if k==1 and tick==41:held=17
    assert lib.s2_session_step(h,held,bufs[k],len(bufs[k]),info)==0;lib.s2_session_snapshot(h,states[k])
   assert bytes(states[0])==bytes(states[1]) and bytes(bufs[0])==bytes(bufs[1]);compared+=1
 finally:
  for h in hs:lib.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_legacy_air_attack_combo.gif',save_all=True,append_images=images[1:],duration=50,loop=0)
 report={'manual_input_frame_comparisons':compared,'air_attack_frames':len(airTicks),'first_air_attack_tick':airTicks[0][1],'animation':'0x0834F304','reset_replay_verified':True,'mismatches':0,'scope':'Legacy general-player fixture. Simultaneous A+B equals ordinary source jump/air attack inputs; held A+B does not retrigger, midair skips jump. Full enemy damage/projectiles and Android touch execution excluded.'};(ROOT/'docs/legacy_air_attack_combo_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
