#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""All33 original coin slots: overlap fixture, stable IDs, removal and reset."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,types in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_coin_count',[ctypes.c_void_p]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(lib,name).argtypes=types
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));ids=[]
 for i in range(71):
  if struct.unpack_from('<H',raw,16+i*44)[0]==89:ids.append(i+1);struct.pack_into('<HH',raw,18+i*44,35,350)
 assert len(ids)==33
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'overlap.s2ob';p.write_bytes(raw);err=ctypes.c_int32();handles=[create(*paths,str(p).encode(),ctypes.byref(err)) for _ in range(2)];assert all(handles)
  pixels=(ctypes.c_uint32*38400)();wide=(ctypes.c_uint32*(480*160))();info=(ctypes.c_int32*8)();actor=(ctypes.c_int32*216)();states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];timeline=[];images=[];initial={}
  try:
   for id in ids:lib.s2_session_actor_snapshot(handles[0],id,actor);initial[id]=list(actor)
   assert lib.s2_session_set_viewport(handles[1],480,160)==0
   for tick in range(1,121):
    for k,h in enumerate(handles):
     buf=wide if k else pixels;assert lib.s2_session_step(h,0,buf,len(buf),info)==0,(tick,k,list(info));lib.s2_session_snapshot(h,states[k])
    assert list(states[0])==list(states[1]);counts=[lib.s2_session_coin_count(h) for h in handles];assert counts[0]==counts[1];timeline.append(counts[0])
    removed=[]
    for id in ids:
     lib.s2_session_actor_snapshot(handles[0],id,actor);first=list(actor);lib.s2_session_actor_snapshot(handles[1],id,actor);assert first==list(actor),(tick,id)
     if actor[40]&1:removed.append(id)
    if tick%4==0:images.append(Image.frombytes('RGBA',(240,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
   assert timeline[-1]==33 and max(timeline)==33,timeline;assert removed==ids
   rows=(ctypes.c_int32*(256*8))();n=lib.s2_session_requests(handles[0],rows,256);assert n>=0;requests=[list(rows[i*8:i*8+8]) for i in range(n)];sounds=[x for x in requests if x[1]==11];packets=[x for x in requests if x[1]==1];removals=[x[4] for x in requests if x[1]==19]
   assert len(sounds)==33 and all(x[2:4]==[0x08053e7c,256] for x in sounds);assert len(packets)==33 and all(x[4:7]==[2,3,0] for x in packets);assert removals==ids
   assert lib.s2_session_reset(handles[0])==0 and lib.s2_session_coin_count(handles[0])==0 and lib.s2_session_requests(handles[0],None,0)==0
   for id in ids:lib.s2_session_actor_snapshot(handles[0],id,actor);assert list(actor)==initial[id]
   for tick in range(120):assert lib.s2_session_step(handles[0],0,pixels,len(pixels),info)==0
   assert lib.s2_session_coin_count(handles[0])==33
  finally:
   for h in handles:lib.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_coin_overlap_fixture.gif',save_all=True,append_images=images[1:],duration=67,loop=0,optimize=False,disposal=2)
 report={'coin_ids':ids,'fixture_ticks':120,'first_pickup_tick':next(i+1 for i,n in enumerate(timeline) if n),'final_pickup_count':33,'sound_requests':len(sounds),'manager_packets':len(packets),'removed_ids':removals,'wide_actor_frame_comparisons':120*33,'reset_and_replay_verified':True,'mismatches':0,'scope':'Explicit overlap fixture puts all33 coins at35,350. Production files keep original positions. Selected counter, queued global packet, sound and removal tested; Android playback and full manager excluded.'};(ROOT/'docs/session_coin_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
