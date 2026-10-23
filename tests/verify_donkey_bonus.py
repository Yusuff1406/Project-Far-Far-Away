#!/usr/bin/env python3
"""Real scene07 without added floors: tracking, score, loss, results and reset."""
import ctypes as C,json,struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
lib.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];lib.s2_session_create_level.restype=P
for n,args in [('destroy',[P]),('reset',[P]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('coin_count',[P]),('minigame_state',[P]),('set_bonus_results',[P,I]),('set_viewport',[P,I,I]),('audio_since',[P,I,IP,C.c_size_t,IP])]:getattr(lib,'s2_session_'+n).argtypes=args
paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_07/scene.s2lv',ROOT/'collision/scene_07/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',ROOT/'objects/scene_07/scene.s2ob'];err=I();h=lib.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert h and not err.value
state=(I*320)();board=(I*216)();info=(I*8)();pix=(C.c_uint32*38400)();frames=0;bounce=0;lastVy=0;scores=[]
def step(buttons):
 global frames,bounce,lastVy
 assert lib.s2_session_step(h,buttons,pix,len(pix),info)==0,(frames,buttons,list(info));lib.s2_session_snapshot(h,state);lib.s2_session_actor_snapshot(h,2,board);frames+=1
 if state[11]<0 and lastVy>0:bounce+=1
 lastVy=state[11]
try:
 initial=(I*320)();lib.s2_session_snapshot(h,initial)
 # Tracking input uses the source board center; this is an automated player,
 # never a native teleport or modification of either actor's physics.
 for t in range(1000):
  lib.s2_session_snapshot(h,state);lib.s2_session_actor_snapshot(h,2,board)
  dx=board[0]-state[0];held=(16 if dx>2*256 else 32 if dx<-2*256 else 0)
  step(held);scores.append(lib.s2_session_coin_count(h))
  if t==400:
   Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/donkey_bonus66.png')
  assert lib.s2_session_minigame_state(h)==1,(t,lib.s2_session_coin_count(h),list(info),list(board[:14]))
 assert scores==sorted(scores) and scores[-1]>=15 and bounce>=15,(scores[-1],bounce)
 trackedScore=scores[-1]
 # Leave the board using actual input. Loss queues global0/24 immediately,
 # without inserting a primary death animation or its effect.
 lib.s2_session_set_bonus_results(h,1)
 for t in range(400):
  step(16)
  if lib.s2_session_minigame_state(h)==2:break
 assert lib.s2_session_minigame_state(h)==2 and state[80]!=13, "Donkey must fail without inserted death animation"
 step(0);frozen=list(state)
 for t in range(12):step(0);assert list(state)==frozen
 sounds=(I*(4096*3))();next_=I();n=lib.s2_session_audio_since(h,0,sounds,4096,C.byref(next_));assert n>0;soundIds=sorted(set(sounds[i*3]for i in range(n)));assert 14 not in soundIds,'inserted Donkey death sound'
 assert lib.s2_session_reset(h)==0;lib.s2_session_snapshot(h,state);assert list(state)==list(initial)
 # Native widescreen child uses unchanged geometry with a wider presentation.
 lib.s2_session_set_viewport(h,384,160);wide=(C.c_uint32*(384*160))();assert lib.s2_session_step(h,0,wide,len(wide),info)==0
finally:lib.s2_session_destroy(h)
report=dict(native_frames=frames,tracked_score=trackedScore,bounces=bounce,monotonic_score=True,original_scene07_no_floor_added=True,physical_loss_and_immediate_packet=True,results_freeze=True,reset_exact=True,widescreen=True,sound_ids=soundIds,device_tested=False,scope='Actual source scene07 spawn, collision and sprites. Automated directional tracking for1000 frames; actual input then leaves platform. No actor state injection. Parent entry/return and rewards covered separately.')
(ROOT/'docs/donkey_bonus_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
