#!/usr/bin/env python3
"""Recording-identified sound86 on completed first dialogue; no closing-input leakage."""
import argparse,ctypes,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def run(path):
 l=ctypes.CDLL(str(path));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_dialogue_active',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,name).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',ROOT/'objects/scene_00/scene.s2ob'];results=[]
 for pattern in ['complete','held_A_at_close','cancel']:
  err=I();h=create(*[str(p).encode()for p in paths],ctypes.byref(err));assert h,err.value;pix=(ctypes.c_uint32*38400)();info=(I*8)();state=(I*320)();closed=None;closedWorld=None
  try:
   for t in range(1,481):
    active=bool(l.s2_session_dialogue_active(h));b=64 if pattern=='cancel'and t==20 else 1 if pattern!='cancel'and active and t>=10 and t%8==2 else 0
    if pattern=='held_A_at_close'and closed is not None and t<closed+90:b=1
    assert l.s2_session_step(h,b,pix,len(pix),info)==0
    if active and not l.s2_session_dialogue_active(h):closed=t;closedWorld=info[0]
    if closed is not None:l.s2_session_snapshot(h,state);assert state[80]not in [2,3,4,7,19,20,21],(pattern,t,'dialogue input became gameplay')
   rows=(I*(256*8))();n=l.s2_session_requests(h,rows,256);assert n>=0;requests=[list(rows[i*8:i*8+8])for i in range(n)if rows[i*8+1]==11];results.append({'pattern':pattern,'closed':closed,'closed_world_tick':closedWorld,'sound_requests':requests})
  finally:l.s2_session_destroy(h)
 return results

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);a=ap.parse_args();current=run(ROOT/'native/build/libshrek_scene.so')
 for row in current:
  assert row['closed'] is not None
  expected=[[row['closed_world_tick'],11,0x08053cf0,256,0,0,0,0]]
  assert row['sound_requests']==expected,row
 report={'native_frames':1440,'current':current,'scope':'Intro completed/cancelled, no new gameplay input after close; held closingA also tested90 frames. Native requests and player states only. User recording identifies sound86 at7.940s. Native owner emits descriptor08053CF0 once at first-dialogue completion, including held closingA; Start skip also emits the completion reaction, as in the new source recordings. Exact original global resume scheduling is not reproduced. Android playback not executed.'}
 if a.baseline:report['stage50_baseline']=run(a.baseline.resolve())
 (ROOT/'docs/dialogue_audio_exit_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
