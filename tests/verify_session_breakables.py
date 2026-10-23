#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Physical fixture: original type10 supports player, original event9 removes it."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,types in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_actor_event',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int])]:getattr(lib,name).argtypes=types
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+54*44,123,340);struct.pack_into('<HH',raw,18+69*44,123,280);err=ctypes.c_int32();trace=[];images=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'surface.s2ob';p.write_bytes(raw);handles=[create(*paths,str(p).encode(),ctypes.byref(err)) for _ in range(2)];assert all(handles),err.value
  pixelBuffers=[(ctypes.c_uint32*38400)(),(ctypes.c_uint32*(480*160))()];info=(ctypes.c_int32*8)();states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()];actors=[(ctypes.c_int32*216)(),(ctypes.c_int32*216)()];assert lib.s2_session_set_viewport(handles[1],480,160)==0
  initial=None
  try:
   lib.s2_session_actor_snapshot(handles[0],55,actors[0]);initial=list(actors[0]);assert lib.s2_session_actor_event(handles[0],999,(ctypes.c_int32*3)(1,9,0))==-2
   for tick in range(1,201):
    if tick in (60,120):
     event=(ctypes.c_int32*3)(1,13 if tick==60 else 9,1)
     for h in handles:assert lib.s2_session_actor_event(h,55,event)==1
    for k,h in enumerate(handles):
     assert lib.s2_session_step(h,0,pixelBuffers[k],len(pixelBuffers[k]),info)==0,(tick,k,list(info));lib.s2_session_snapshot(h,states[k]);lib.s2_session_actor_snapshot(h,55,actors[k])
    assert list(states[0])==list(states[1]) and list(actors[0])==list(actors[1]);trace.append([tick,states[0][1],states[0][64],actors[0][40]&1])
    if tick%4==0:images.append(Image.frombytes('RGBA',(240,160),bytes(pixelBuffers[0]),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
   assert all(row[2]>0 and row[3]==0 for row in trace[40:119]),trace[40:119]
   standing=trace[80][1];assert len({row[1] for row in trace[40:119]})==1
   removal=next(row[0] for row in trace if row[3]);assert removal>120 and states[0][1]>standing and states[0][64]==0,(removal,standing,states[0][1],states[0][64])
   rows=(ctypes.c_int32*(256*8))();n=lib.s2_session_requests(handles[0],rows,256);requests=[list(rows[i*8:i*8+8]) for i in range(n)];sounds=[row for row in requests if row[1]==11 and row[2]==0x08053fa8];assert len(sounds)==1 and sounds[0][2]==0x08053fa8;assert [row[4] for row in requests if row[1]==19]==[55]
   assert lib.s2_session_actor_event(handles[0],55,(ctypes.c_int32*3)(1,9,1))==0
   assert lib.s2_session_reset(handles[0])==0;lib.s2_session_actor_snapshot(handles[0],55,actors[0]);assert list(actors[0])==initial;assert lib.s2_session_requests(handles[0],None,0)==0
   for tick in range(80):assert lib.s2_session_step(handles[0],0,pixelBuffers[0],len(pixelBuffers[0]),info)==0
   lib.s2_session_snapshot(handles[0],states[0]);assert states[0][64]>0 and states[0][1]==standing
  finally:
   for h in handles:lib.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_breakable_surface_fixture.gif',save_all=True,append_images=images[1:],duration=67,loop=0)
 report={'fixture_ticks':200,'original_actor_id':55,'regular_hit13_preserved_object':True,'event9_tick':120,'removal_tick':removal,'supported_player_y_q8':standing,'fall_after_removal_verified':True,'sound_requests':sounds,'wide_gameplay_comparisons':200,'reset_restored_support':True,'mismatches':0,'scope':'Explicit fixture moves object55 to123,340 and player start to123,280. Event9 delivered by test API, not exposed Shrek controls. Production layout unchanged; full original scheduler excluded.'};(ROOT/'docs/session_breakable_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
