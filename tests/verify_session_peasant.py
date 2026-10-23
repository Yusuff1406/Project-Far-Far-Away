#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Native peasant limit, child death notice, ID reuse, reset and wide replay."""
import ctypes,hashlib,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p;lib.s2_session_set_auto_restart.argtypes=[ctypes.c_void_p,I]
 for n,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_world_info',[ctypes.c_void_p,IP]),('s2_session_spawner_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_actor_event',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(lib,n).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']
 raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+30*44,60,350);struct.pack_into('<HH',raw,18+62*44,180,350);struct.pack_into('<I',raw,16+62*44+24,0);images=[];results=[];frames=0
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw)
  for recycle in [False,True,'attack']:
   ticks=420 if recycle=='attack'else 900
   reference=None;summary={}
   for width in [240,480]:
    reference=None # Child activity depends on the viewport; reset must reproduce each width.
    err=I();h=create(*[str(x).encode()for x in paths],str(p).encode(),ctypes.byref(err));assert h and err.value==0;lib.s2_session_set_auto_restart(h,0)
    assert lib.s2_session_set_viewport(h,width,160)==0
    try:
     for replay in range(2):
      if replay:assert lib.s2_session_reset(h)==0
      pixels=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();actor=(I*216)();sub=(I*8)();meta=(I*4)();trace=[];maximum=0
      for tick in range(1,ticks+1):
       if recycle is True and tick in [20,80]:
        ident=63 if tick==20 else 72;assert lib.s2_session_actor_event(h,ident,(I*3)(3,13,0))==1,(tick,ident)
       e=lib.s2_session_step(h,2 if recycle=='attack'and tick%30==1 else 0,pixels,len(pixels),info);assert e==0,(recycle,width,replay,tick,e,list(info))
       assert lib.s2_session_snapshot(h,hero)==0;assert lib.s2_session_spawner_snapshot(h,31,sub)==0;assert 0<=sub[2]<=5 and sub[3]==sub[2];maximum=max(maximum,sub[2])
       assert lib.s2_session_actor_snapshot(h,31,actor)==0 and actor[149]==1031
       state=bytearray(bytes(hero)+bytes(actor)+bytes(sub))
       for ident in range(72,80):
        actor[:]=[0]*216;present=lib.s2_session_actor_snapshot(h,ident,actor);assert present in [0,-2]
        if present==0:assert actor[149]in([0,2031]if recycle=='attack'else[2031])and actor[79]==0,(recycle,tick,ident,actor[149],actor[79],list(sub))
        state.extend(struct.pack('<i',present));state.extend(bytes(actor))
       trace.append(hashlib.sha256(state).hexdigest());frames+=1
       if not recycle and width==240 and replay==0 and tick<=180 and tick%3==0:images.append(Image.frombytes('RGBA',(width,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
      assert lib.s2_session_world_info(h,meta)==0 and list(meta)==[71,67,3,70]
      rows=(I*(256*8))();n=lib.s2_session_requests(h,rows,256);assert n>=0
      births=[list(rows[i*8:i*8+8])for i in range(n)if rows[i*8+1]==23 and rows[i*8+4]==53]
      if recycle=='attack':
       assert lib.s2_session_actor_snapshot(h,31,actor)==0 and actor[40]&1 and actor[52]==0
      else:
       assert len(births)==(6 if recycle else 5),(recycle,births,list(sub));assert maximum==5 and sub[2]==5
      if recycle is True:assert [q[7]for q in births]==[72,72,73,74,75,76]
      if reference is None:reference=trace;summary={'recycle':recycle,'births':births,'maximum_live_count':maximum,'final_subtype':list(sub)}
      else:assert trace==reference,(recycle,width,replay)
    finally:lib.s2_session_destroy(h)
   results.append(summary)
 images[0].save(ROOT/'previews/native_peasant_spawn_fixture.gif',save_all=True,append_images=images[1:],duration=50,loop=0);images[20].save(ROOT/'previews/native_peasant_spawn_fixture.png')
 report={'native_frame_comparisons':frames,'scenarios':results,'mismatches':0,'scope':'Peasant31 relocated near original player spawn; unrelated pumpkin63 explicitly relocated to180,350 inside both viewports and its secondary coin disabled only in fixture to isolate tag/refund checks; no gameplay buttons in cap/recycle cases. Attack case uses B only to defeat the peasant. Cap5 verified with automatic level restart disabled for isolated child-lifetime inspection. Recycling case explicitly sends hit13 to unrelated pumpkin63 and visible generated child72 at tick80; real death scripts broadcast their tags, parent ignores unrelated notice and restores a slot, freed ID72 is reused. Serialized player/parent/subtype/dynamic states hashed for reset equality per viewport. Production coordinates unchanged; exact original whole-world scheduling and Android device excluded.'}
 (ROOT/'docs/session_peasant_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
