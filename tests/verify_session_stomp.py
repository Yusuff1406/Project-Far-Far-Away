#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""A+B -> actual stomp -> breakable removal, without actor-event injection."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(lib,name).argtypes=args
 paths=[str(x).encode()for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];results=[];images=[];comparisons=0
 patterns={'together':lambda t:3 if 60<=t<=200 else 0,'short':lambda t:3 if t==60 else 0,'a_first':lambda t:1 if 60<=t<62 else 3 if 62<=t<=200 else 0,'b_first':lambda t:2 if 60<=t<62 else 3 if 62<=t<=200 else 0,'midair':lambda t:3 if 5<=t<=200 else 0}
 for id in (55,56):
  for name,held in patterns.items():
   raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+(id-1)*44,123,340);struct.pack_into('<HH',raw,18+69*44,123,280)
   # Disable NPC68's dialog tag only in this isolated floor fixture.
   struct.pack_into('<I',raw,16+67*44+20,0)
   with tempfile.TemporaryDirectory()as tmp:
    path=Path(tmp)/'fixture.s2ob';path.write_bytes(raw);error=ctypes.c_int32();hs=[create(*paths,str(path).encode(),ctypes.byref(error))for _ in range(2)];assert all(hs);lib.s2_session_set_viewport(hs[1],480,160);buffers=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*76800)()];states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];actors=[(ctypes.c_int32*216)(),(ctypes.c_int32*216)()];info=(ctypes.c_int32*8)();phases=[];removed=[];activation=[];timeline=[]
    try:
     initial=[]
     for h in hs:lib.s2_session_snapshot(h,states[0]);lib.s2_session_actor_snapshot(h,id,actors[0]);initial.append((list(states[0]),list(actors[0])))
     for tick in range(1,241):
      for k,h in enumerate(hs):
       assert lib.s2_session_step(h,held(tick),buffers[k],len(buffers[k]),info)==0,(id,name,tick,k,list(info));lib.s2_session_snapshot(h,states[k]);lib.s2_session_actor_snapshot(h,id,actors[k])
      assert bytes(states[0])==bytes(states[1])and bytes(actors[0])==bytes(actors[1]);comparisons+=1;s,a=states[0],actors[0];timeline.append((list(s),list(a)))
      if not phases or phases[-1][1]!=s[80]:phases.append([tick,s[80]])
      if a[146]:activation.append([tick,a[148],a[147]])
      if a[40]&1 and not removed:removed.append(tick)
      if s[80]==20:assert list(s[41:43])==[10,9]and s[11]==1792
      if id==55 and name=='together'and tick%2==0:images.append(Image.frombytes('RGBA',(240,160),bytes(buffers[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
     assert len(removed)==1 and removed[0]<170,(id,name,phases,removed);assert [p[1]for p in phases].count(19)==1;assert all(x in [p[1]for p in phases]for x in (19,20,21));assert states[0][1]>timeline[40][0][1] and states[0][80]==0
     rows=(ctypes.c_int32*(256*8))();n=lib.s2_session_requests(hs[0],rows,256);assert n>=0;requests=[list(rows[i*8:i*8+8])for i in range(n)];assert len([x for x in requests if x[1]==19 and x[4]==id])==1;assert any(x[1]==11 and x[2]==0x08053fa8 for x in requests);assert any(x[1]==11 and x[2]==0x08053ccc for x in requests);assert len([x for x in requests if x[1]==20])==1
     # Class10/id9 arises from player contact, never from the test's event API.
     assert len([x for x in activation if x[1]==10])==1,activation
     for k,h in enumerate(hs):lib.s2_session_reset(h);lib.s2_session_snapshot(h,states[k]);lib.s2_session_actor_snapshot(h,id,actors[k]);assert (list(states[k]),list(actors[k]))==initial[k]
     for tick in range(1,241):
      assert lib.s2_session_step(hs[0],held(tick),buffers[0],len(buffers[0]),info)==0;lib.s2_session_snapshot(hs[0],states[0]);lib.s2_session_actor_snapshot(hs[0],id,actors[0]);assert (list(states[0]),list(actors[0]))==timeline[tick-1];comparisons+=1
     results.append({'id':id,'pattern':name,'phase_transitions':phases,'break_contact':activation,'removal_tick':removed[0]})
    finally:
     for h in hs:lib.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_stomp_break_fixture.gif',save_all=True,append_images=images[1:],duration=34,loop=0);images[43].save(ROOT/'previews/native_stomp_break_fixture.png');report={'scenarios':results,'wide_and_reset_frame_comparisons':comparisons,'forced_actor_events':0,'mismatches':0,'scope':'Relocated real type10 actors55/56, both source flips, A+B only. NPC68 dialogue tag disabled only in fixture. Production coordinates/tags unchanged. Source phases separately verified; whole original world scheduler and actual Android touch excluded.'};(ROOT/'docs/session_stomp_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
