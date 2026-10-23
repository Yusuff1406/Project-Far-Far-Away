#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Physical normal and stomp bounces, using real type18 contact and scripts."""
import ctypes,json,struct,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
 for n,a in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(l,n).argtypes=a
 paths=[str(p).encode()for p in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];results=[];comparisons=0
 for pattern in ['normal','stomp']:
  raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18,123,340);struct.pack_into('<HH',raw,18+69*44,123,280)
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw);err=ctypes.c_int32();hs=[c(*paths,str(p).encode(),ctypes.byref(err))for _ in range(2)];assert all(hs);l.s2_session_set_viewport(hs[1],480,160);bs=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*76800)()];ss=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];info=(ctypes.c_int32*8)();trace=[]
   def held(t):return 3 if pattern=='stomp'and 60<=t<=150 else 0
   try:
    for t in range(1,161):
     for k,h in enumerate(hs):assert l.s2_session_step(h,held(t),bs[k],len(bs[k]),info)==0;l.s2_session_snapshot(h,ss[k])
     assert bytes(ss[0])==bytes(ss[1]);trace.append(list(ss[0]));comparisons+=1
    if pattern=='normal':bounce=next(i for i,s in enumerate(trace)if s[80]==2 and s[11]==-1430)
    else:bounce=next(i for i,s in enumerate(trace)if i and trace[i-1][80]==20 and s[80]==2);assert trace[bounce][11]==-1716
    end=next(i for i in range(bounce+1,len(trace))if trace[i][11]>=0);height=(trace[bounce][1]-min(s[1]for s in trace[bounce:end+1]))/256;assert height>75 if pattern=='normal'else height>110
    results.append({'pattern':pattern,'bounce_tick':bounce+1,'initial_vy_q8':trace[bounce][11],'rise_pixels':height})
    l.s2_session_reset(hs[0])
    for t in range(1,161):assert l.s2_session_step(hs[0],held(t),bs[0],len(bs[0]),info)==0;l.s2_session_snapshot(hs[0],ss[0]);assert list(ss[0])==trace[t-1];comparisons+=1
   finally:
    for h in hs:l.s2_session_destroy(h)
 assert results[1]['rise_pixels']>results[0]['rise_pixels']+25
 report={'scenarios':results,'wide_and_reset_frame_comparisons':comparisons,'forced_actor_events':0,'mismatches':0,'scope':'Relocated real type18 actor1, real script/event28; normal fall versus A+B stomp. Source boost separately checked against original10C08. Production geometry, bonus trigger/minigame and Android device not validated here.'};(ROOT/'docs/session_bounce_height_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
