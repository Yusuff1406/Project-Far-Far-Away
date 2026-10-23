#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Real type14 pickup by normal player contact, carrying and B release."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(lib,name).argtypes=args
 paths=[str(x).encode()for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];results=[];comparisons=0;images=[];mushroomImages=[]
 for id,name,xy,first in [(44,'close',(35,358),2),(44,'close_held',(35,358),2),(44,'no_input',(35,358),0),(44,'out_of_range',(85,358),2),(44,'held_approach',(85,358),2),(27,'mushroom',(35,358),2),(27,'mushroom_no_input',(35,358),0),(27,'select_lift',(35,358),4)]:
  raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+(id-1)*44,*xy)
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw);err=ctypes.c_int32();hs=[create(*paths,str(p).encode(),ctypes.byref(err))for _ in range(2)];assert all(hs);assert lib.s2_session_set_viewport(hs[1],480,160)==0;bs=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*76800)()];ss=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];aa=[(ctypes.c_int32*216)(),(ctypes.c_int32*216)()];info=(ctypes.c_int32*8)();trace=[];phases=[]
   def held(t):
    if name=='close_held' and t<=80:return 2
    if name=='held_approach':return 2|(16 if t<100 else 0)
    return 0 if name in ('no_input','mushroom_no_input')else first if t==1 else 16 if 95<=t<105 else 2 if t==115 else 0
   try:
    for t in range(1,161):
     for k,h in enumerate(hs):
      assert lib.s2_session_step(h,held(t),bs[k],len(bs[k]),info)==0,(name,t,k,list(info));lib.s2_session_snapshot(h,ss[k]);lib.s2_session_actor_snapshot(h,id,aa[k])
     assert bytes(ss[0])==bytes(ss[1])and bytes(aa[0])==bytes(aa[1]);comparisons+=1;trace.append((list(ss[0]),list(aa[0])))
     if not phases or phases[-1][1]!=ss[0][80]:phases.append([t,ss[0][80]])
     if name=='close'and t%2==0:images.append(Image.frombytes('RGBA',(240,160),bytes(bs[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
     if name=='mushroom'and t%2==0:mushroomImages.append(Image.frombytes('RGBA',(240,160),bytes(bs[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
    rows=(ctypes.c_int32*(256*8))();n=lib.s2_session_requests(hs[0],rows,256);requests=[list(rows[i*8:i*8+8])for i in range(n)]
    if name in ('close','close_held','mushroom','select_lift'):
     assert all(x in [p[1]for p in phases]for x in (16,17,18)),phases;assert trace[109][0][102]==id and trace[114][0][102]==0;assert trace[114][0][80]==0
     assert trace[99][1][0]==trace[99][0][0]and trace[99][1][1]<trace[99][0][1];assert trace[115][1][11]==256;assert trace[-1][1][1]>trace[114][1][1]
     assert any(x[1]==11 and x[2]==0x08053cfc for x in requests);assert len([x for x in requests if x[1]==21 and x[4:6]==[id,11]])==1
    else:assert not any(x[0][102]for x in trace)and not any(x[1]==21 for x in requests)
    assert lib.s2_session_reset(hs[0])==0
    for t in range(1,161):
     assert lib.s2_session_step(hs[0],held(t),bs[0],len(bs[0]),info)==0;lib.s2_session_snapshot(hs[0],ss[0]);lib.s2_session_actor_snapshot(hs[0],id,aa[0]);assert (list(ss[0]),list(aa[0]))==trace[t-1];comparisons+=1
    results.append({'actor_id':id,'pattern':name,'object_anchor':xy,'phases':phases,'requests':requests})
   finally:
    for h in hs:lib.s2_session_destroy(h)
 mushroomImages[0].save(ROOT/'previews/native_mushroom_lift_fixture.gif',save_all=True,append_images=mushroomImages[1:],duration=34,loop=0);mushroomImages[39].save(ROOT/'previews/native_mushroom_lift_fixture.png')
 images[0].save(ROOT/'previews/native_lift_fixture.gif',save_all=True,append_images=images[1:],duration=34,loop=0);images[39].save(ROOT/'previews/native_lift_fixture.png');report={'scenarios':results,'wide_and_reset_frame_comparisons':comparisons,'forced_actor_events':0,'mismatches':0,'scope':'Relocated original type14 ID44 and type16 ID27; contextual B press required; no-input proximity refuses pickup, walking, B drop and restored script gravity. Production anchors unchanged. Native rendering; Android device execution excluded.'};(ROOT/'docs/session_lift_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
