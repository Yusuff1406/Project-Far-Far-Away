#!/usr/bin/env python3
"""Audio request consumption must be nondestructive and cursor-based."""
import ctypes,hashlib,json,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p
 destroy=lib.s2_session_destroy;destroy.argtypes=[ctypes.c_void_p]
 step=lib.s2_session_step;step.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]
 snapshot=lib.s2_session_snapshot;snapshot.argtypes=[ctypes.c_void_p,IP]
 audio=lib.s2_session_audio_since;audio.argtypes=[ctypes.c_void_p,ctypes.c_int,IP,ctypes.c_size_t,IP]
 reset=lib.s2_session_reset;reset.argtypes=[ctypes.c_void_p]
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']]
 error=ctypes.c_int32();handles=[create(*paths,ctypes.byref(error)) for _ in range(2)];assert all(handles)
 pixels=(ctypes.c_uint32*38400)();info=(ctypes.c_int32*8)();states=[(ctypes.c_int32*320)() for _ in range(2)];rows=(ctypes.c_int32*(256*3))();nextCursor=ctypes.c_int32();cursor=0;emitted=[];comparisons=0
 try:
  for tick in range(1,401):
   held=4 if tick==80 else 16 if 125<=tick<130 else 2 if 130<=tick<=190 else 0
   for i,h in enumerate(handles):assert step(h,held,pixels,len(pixels),info)==0;assert snapshot(h,states[i])==0
   assert list(states[0])==list(states[1]);comparisons+=1
   n=audio(handles[1],cursor,rows,256,ctypes.byref(nextCursor));assert n>=0
   repeated=(ctypes.c_int32*(256*3))();other=ctypes.c_int32();assert audio(handles[1],cursor,repeated,256,ctypes.byref(other))==n and other.value==nextCursor.value and list(repeated[:n*3])==list(rows[:n*3])
   for i in range(n):emitted.append([tick,*rows[i*3:i*3+3]])
   cursor=nextCursor.value
   assert audio(handles[1],cursor,None,0,ctypes.byref(nextCursor))==0
  assert emitted==[[225,1,100,255]] and cursor==5,emitted
  rows[0]=123;nextCursor.value=999
  for c,capacity in [(-1,256),(6,256),(0,0)]:
   assert audio(handles[1],c,rows,capacity,ctypes.byref(nextCursor))==-1 and rows[0]==123 and nextCursor.value==999
  assert reset(handles[1])==0;assert audio(handles[1],0,None,0,ctypes.byref(nextCursor))==0 and nextCursor.value==0
  assert audio(handles[1],cursor,rows,256,ctypes.byref(nextCursor))==-1
 finally:
  for h in handles:destroy(h)
 resources=json.loads((ROOT/'docs/complete_sfx_resources.json').read_text())
 assert [fx['sound_id']for fx in resources['effects']]==list(range(1,104))
 for fx in resources['effects']:
  path=ROOT/'android/app/src/main/assets/session/audio'/fx['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==fx['sha256']
  with wave.open(str(path),'rb') as w:
   assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,fx['sample_rate'],fx['samples'])
   assert hashlib.sha256(w.readframes(w.getnframes())).hexdigest()==fx['pcm_sha256']
 result={'gameplay_frames_compared':comparisons,'audio_requests':emitted,'request_cursor_final':cursor,'duplicate_reads_equal':True,'rejected_cursor_or_capacity_cases':4,'reset_cleared_cursor':True,'wav_assets_verified':len(resources['effects']),'mismatches':0,'scope':'Native request bridge, descriptor ID/priority/unsigned gain and WAV integrity. Android SoundPool, focus and audible output need device testing. No full music driver or exact simultaneous-voice parity.'}
 (ROOT/'docs/session_audio_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
