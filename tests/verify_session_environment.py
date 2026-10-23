#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Physical integration fixtures for original source actors27/44; no Android execution."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,types in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_actor_event',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(lib,name).argtypes=types
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];scenarios=[]
 for id,xy,playerStart in [(27,(35,365),(35,350)),(44,(123,340),(123,280))]:
  raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+(id-1)*44,*xy);struct.pack_into('<HH',raw,18+69*44,*playerStart)
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw);err=ctypes.c_int32();handles=[create(*paths,str(p).encode(),ctypes.byref(err)) for _ in range(2)];assert all(handles)
   states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];actors=[(ctypes.c_int32*216)(),(ctypes.c_int32*216)()];buffers=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*(480*160))()];info=(ctypes.c_int32*8)();bounces=[];activations=[];trace=[];frames=[]
   try:
    initial=[]
    for h in handles:lib.s2_session_snapshot(h,states[0]);lib.s2_session_actor_snapshot(h,id,actors[0]);initial.append((list(states[0]),list(actors[0])))
    assert lib.s2_session_set_viewport(handles[1],480,160)==0
    for tick in range(1,241):
     held=1 if id==27 and tick in (1,60,120) else 4 if id==44 and tick==80 else 0
     for k,h in enumerate(handles):
      if id==44 and tick==120:assert lib.s2_session_actor_event(h,id,(ctypes.c_int32*3)(1,2,1))==1
      assert lib.s2_session_step(h,held,buffers[k],len(buffers[k]),info)==0,(id,tick,k,list(info));assert lib.s2_session_snapshot(h,states[k])==0;assert lib.s2_session_actor_snapshot(h,id,actors[k])==0
     assert list(states[0])==list(states[1]) and list(actors[0])==list(actors[1]);s=states[0];a=actors[0];assert a[25]==63
     if s[11]==-1430 and s[80]==2:bounces.append(tick)
     if a[146]:activations.append(tick)
     if id==44 and tick>=40:assert s[64]==1 and s[1]==82944 and s[83]==0
     if id==44 and tick>120:assert s[0]-a[0]==-1280
     trace.append((list(s),list(a)))
     if tick%4==0:frames.append(Image.frombytes('RGBA',(240,160),bytes(buffers[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
    requests=(ctypes.c_int32*(256*8))();n=lib.s2_session_requests(handles[0],requests,256);assert n>=0;rows=[list(requests[i*8:i*8+8]) for i in range(n)];sounds=[x for x in rows if x[1]==11 and x[2]==0x08053fc0]
    if id==27:
     assert len(bounces)>=2 and activations,(bounces,activations);assert all(any(x[0] in (t,t+1) for x in sounds) for t in bounces) and all(x[2:4]==[0x08053fc0,256] for x in sounds);assert not any(r[0][102] for r in trace)
    else:
     assert not sounds and not bounces and not activations;assert trace[79][0][80]==8 and trace[119][1][5]==1280;assert trace[-1][1][5]==0 and trace[-1][0][0]>trace[118][0][0]
    for k,h in enumerate(handles):
     assert lib.s2_session_reset(h)==0;lib.s2_session_snapshot(h,states[k]);lib.s2_session_actor_snapshot(h,id,actors[k]);assert (list(states[k]),list(actors[k]))==initial[k];assert lib.s2_session_requests(h,None,0)==0
    # Re-run the exact control/event stream after reset and compare every player/object word.
    for tick in range(1,241):
     if id==44 and tick==120:assert lib.s2_session_actor_event(handles[0],id,(ctypes.c_int32*3)(1,2,1))==1
     held=1 if id==27 and tick in (1,60,120) else 4 if id==44 and tick==80 else 0
     assert lib.s2_session_step(handles[0],held,buffers[0],len(buffers[0]),info)==0;lib.s2_session_snapshot(handles[0],states[0]);lib.s2_session_actor_snapshot(handles[0],id,actors[0]);assert (list(states[0]),list(actors[0]))==trace[tick-1]
   finally:
    for h in handles:lib.s2_session_destroy(h)
  prefix='native_mushroom_fixture' if id==27 else 'native_support_object_fixture';frames[0].save(ROOT/'previews'/f'{prefix}.gif',save_all=True,append_images=frames[1:],duration=67,loop=0);frames[30].save(ROOT/'previews'/f'{prefix}.png');scenarios.append({'actor_id':id,'fixture_object_anchor':xy,'fixture_player_anchor':playerStart,'bounces':bounces,'sounds':sounds,'wide_frames_compared':240,'reset_replay_frames':240,'grab12_refused':id==44,'scripted_push_event2_tick':120 if id==44 else None})
 report={'scenarios':scenarios,'wide_comparisons':480,'reset_replay_comparisons':480,'mismatches':0,'scope':'Explicit relocated fixtures. Mushroom A on frame1 avoids the newly restored automatic pickup and exercises regular bounce. Production source positions unchanged. Object44 push is delivered by test API, not an exposed Shrek button. Carry12 is refused; full world scheduler and Android execution excluded.'};(ROOT/'docs/session_environment_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
