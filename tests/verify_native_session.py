#!/usr/bin/env python3
"""Compare owned session state with the Stage21 separately scheduled harness."""
import ctypes,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p
 destroy=lib.s2_session_destroy;destroy.argtypes=[ctypes.c_void_p];destroy.restype=None
 reset=lib.s2_session_reset;reset.argtypes=[ctypes.c_void_p]
 step=lib.s2_session_step;step.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]
 snapshot=lib.s2_session_snapshot;snapshot.argtypes=[ctypes.c_void_p,IP]
 package=ROOT/'android/app/src/main/assets/session/resources.s2pk'
 paths=[str(x).encode() for x in [package,ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']]
 trace=json.loads((ROOT/'tests/fixtures/shrek_session_trace.json').read_text());assert len(trace)==360
 error=ctypes.c_int32();handle=create(*paths,ctypes.byref(error));assert handle and error.value==0
 pixels=(ctypes.c_uint32*(240*160))();info=(ctypes.c_int32*8)();state=(ctypes.c_int32*320)();frames=0
 try:
  for replay in range(2):
   if replay:assert reset(handle)==0
   assert snapshot(handle,state)==0;before=list(state);assert step(handle,8,pixels,len(pixels),info)==-4;assert snapshot(handle,state)==0 and list(state)==before
   for tick,expected in enumerate(trace,1):
    held=4 if tick in [80,240] else 16 if 125<=tick<160 else 1 if tick in [170,300] else 0
    assert step(handle,held,pixels,len(pixels),info)==0,(tick,list(info));assert snapshot(handle,state)==0
    assert list(state)==expected,(replay,tick,[(i,state[i],expected[i]) for i in range(320) if state[i]!=expected[i]])
    assert info[0]==tick and info[1]==state[80] and info[3]==state[83];assert all((p>>24)==255 for p in pixels);assert len(set(pixels))>100;frames+=1
 finally:destroy(handle)
 invalid=0;raw=package.read_bytes()
 with tempfile.TemporaryDirectory() as tmp:
  for data in [b'',b'NOPE'+raw[4:],raw[:16],raw[:-1],raw[:8]+(20001).to_bytes(4,'little')+raw[12:]]:
   p=Path(tmp)/'bad.s2pk';p.write_bytes(data);h=create(str(p).encode(),*paths[1:],ctypes.byref(error));assert not h and error.value==-2;invalid+=1
 result={'session_frames_compared':frames,'state_words_per_frame':320,'deterministic_replays':2,'opaque_pixels_verified_per_frame':38400,'malformed_package_refusals':invalid,'unsupported_button_refusals':2,'mismatches':0,'scope':'Owned C++ session compared against Stage21 separately scheduled Python/native harness; full frame state includes player, carry/status/book, item, VM and reactions. Rendering executes with extracted sprites and follow camera. ROM comparison applies separately to Stage21 player tests. No JNI/Java/Android device execution or PCM.'}
 (ROOT/'docs/native_session_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
