#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Full frames/state versus a host library built from the Stage33 checkpoint."""
import argparse,ctypes,json,tempfile,struct,time,statistics,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('reference_library');ap.add_argument('--legacy-only',action='store_true',help='Current scene has new types; compare only the legacy scene against Stage33');a=ap.parse_args();libs=[ctypes.CDLL(a.reference_library),ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))]
 for lib in libs:
  for name,types in [('s2_session_create',[ctypes.c_char_p]*4+[IP]),('s2_session_create_level',[ctypes.c_char_p]*5+[IP]),('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t])]:getattr(lib,name).argtypes=types
  lib.s2_session_create.restype=lib.s2_session_create_level.restype=ctypes.c_void_p
 libs[0].s2_session_banana_count.argtypes=libs[1].s2_session_coin_count.argtypes=[ctypes.c_void_p]
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];objects=fixture_scene(ROOT/'objects/scene_00/scene.s2ob');ids=[x['instance_id'] for x in json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'] if x['type'] in (18,89)];pixels=cases=actorcases=0;timings=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'coins.s2ob';raw=bytearray(objects.read_bytes())
  for i in range(71):
   if struct.unpack_from('<H',raw,16+i*44)[0]==89:struct.pack_into('<HH',raw,18+i*44,35,350)
  p.write_bytes(raw)
  for scenario,length,obj in ([('legacy',360,None)] if a.legacy_only else [('legacy',360,None),('original_world',360,objects),('coin_fixture',120,p)]):
   err=ctypes.c_int32();handles=[lib.s2_session_create(*paths,ctypes.byref(err)) if obj is None else lib.s2_session_create_level(*paths,str(obj).encode(),ctypes.byref(err)) for lib in libs];assert all(handles)
   try:
    for tick in range(1,length+1):
     width=[240,373,480,640][(tick//30)%4];bufs=[(ctypes.c_uint32*(width*160))() for _ in libs];infos=[(ctypes.c_int32*8)(),(ctypes.c_int32*8)()];states=[(ctypes.c_int32*320)(),(ctypes.c_int32*320)()]
     held=(4 if tick in (80,240) else 16 if 125<=tick<160 else 1 if tick in (170,300) else 0) if scenario=='legacy' else 32 if scenario=='original_world' and tick<280 else 0
     for k,lib in enumerate(libs):assert lib.s2_session_set_viewport(handles[k],width,160)==0;assert lib.s2_session_step(handles[k],held,bufs[k],len(bufs[k]),infos[k])==0,(scenario,tick,k);lib.s2_session_snapshot(handles[k],states[k])
     assert bytes(bufs[0])==bytes(bufs[1]),(scenario,tick,'pixels');assert list(infos[0])==list(infos[1]);assert list(states[0])==list(states[1]);pixels+=width*160;cases+=1
     if obj is not None:
      assert libs[0].s2_session_banana_count(handles[0])==libs[1].s2_session_coin_count(handles[1])
      for id in ids:
       actors=[(ctypes.c_int32*216)(),(ctypes.c_int32*216)()]
       for k,lib in enumerate(libs):assert lib.s2_session_actor_snapshot(handles[k],id,actors[k])==0
       assert bytes(actors[0])==bytes(actors[1]);actorcases+=1
    queues=[(ctypes.c_int32*(256*8))(),(ctypes.c_int32*(256*8))()];counts=[lib.s2_session_requests(handles[k],queues[k],256) for k,lib in enumerate(libs)];assert counts[0]==counts[1]>=0 and bytes(queues[0])==bytes(queues[1])
    if scenario=='original_world':
     for run in range(5):
      times=[]
      for k,lib in enumerate(libs):
       assert lib.s2_session_reset(handles[k])==0;assert lib.s2_session_set_viewport(handles[k],373,160)==0;buf=(ctypes.c_uint32*(373*160))();info=(ctypes.c_int32*8)();start=time.perf_counter()
       for tick in range(30):assert lib.s2_session_step(handles[k],0,buf,len(buf),info)==0
       times.append(time.perf_counter()-start)
      timings.append(times)
   finally:
    for k,lib in enumerate(libs):lib.s2_session_destroy(handles[k])
 median=[statistics.median(x[i] for x in timings) for i in (0,1)] if timings else [None,None];report={'full_frames_compared':cases,'pixels_compared':pixels,'actor_states_compared':actorcases,'mismatches':0,'host_world_30_frame_median_seconds':{'stage33':median[0],'stage34':median[1]},'host_ratio':median[0]/median[1] if timings else None,'reference_library_sha256':hashlib.sha256(Path(a.reference_library).read_bytes()).hexdigest(),'scope':'Stage33 source checkpoint baseline, legacy/original world/overlap fixture, four viewport widths, complete output frame and exposed states/requests. Host timing, not Android FPS.'};(ROOT/('docs/session_render_legacy_validation.json' if a.legacy_only else 'docs/session_render_cache_validation.json')).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
