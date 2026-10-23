#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Physical enemy fixtures: controller input, damage, death/drop and reset."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for n,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_health',[ctypes.c_void_p]),('s2_session_coin_count',[ctypes.c_void_p]),('s2_session_world_info',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(lib,n).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']
 raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());results=[];frames=0;images=[]
 def buttons(pattern,t):
  if pattern=='attack':return 2 if t==1 else 16 if 65<=t<90 else 0
  if pattern=='hurt':return 16 if t<50 else 2 if t in [50,100,150,200,250] else 0
  return 16 if t<100 or 260<=t<420 else 32
 with tempfile.TemporaryDirectory() as tmp:
  for pattern,ticks in [('attack',300),('hurt',300),('defeat',960)]:
   data=bytearray(raw)
   for ident in ([59,61,62,63]if pattern=='defeat'else[63]):struct.pack_into('<HH',data,16+(ident-1)*44+2,60 if pattern=='attack'else 90,350)
   fixture=Path(tmp)/'scene.s2ob';fixture.write_bytes(data);reference=None;summary={}
   for width in [240,480]:
    # Different visible areas legitimately activate different enemies on this long route.
    if pattern=='defeat':reference=None
    err=I();h=create(*[str(p).encode()for p in paths],str(fixture).encode(),ctypes.byref(err));assert h and err.value==0
    assert lib.s2_session_set_viewport(h,width,160)==0
    try:
     for replay in range(2):
      if replay:assert lib.s2_session_reset(h)==0
      assert lib.s2_session_health(h)==6 and lib.s2_session_coin_count(h)==0
      pixels=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();enemy=(I*216)();trace=[];meta=(I*4)()
      for tick in range(1,ticks+1):
       e=lib.s2_session_step(h,buttons(pattern,tick),pixels,len(pixels),info);assert e==0,(pattern,width,replay,tick,e,list(info))
       assert lib.s2_session_snapshot(h,hero)==0;assert lib.s2_session_actor_snapshot(h,63,enemy)==0
       trace.append([*hero,*enemy,lib.s2_session_health(h),lib.s2_session_coin_count(h)]);frames+=1
       if pattern=='attack'and width==240 and replay==0 and tick%3==0:images.append(Image.frombytes('RGBA',(width,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
      assert lib.s2_session_world_info(h,meta)==0 and list(meta)==[71,67,3,70]
      if reference is None:reference=trace;summary={'pattern':pattern,'ticks':ticks,'health':lib.s2_session_health(h),'coins':lib.s2_session_coin_count(h),'phase':hero[80],'enemy_removed':bool(enemy[40]&1)}
      else:assert trace==reference,(pattern,width,replay)
      if pattern=='attack':assert summary['health']==6 and summary['coins']==1 and summary['enemy_removed']
      elif pattern=='hurt':assert summary['health']==5 and any(x[80]==6 for x in trace)
      else:assert 0<summary['health']<6 and summary['phase']!=13,summary
    finally:lib.s2_session_destroy(h)
   results.append(summary)
 images[0].save(ROOT/'previews/native_enemy_combat_fixture.gif',save_all=True,append_images=images[1:],duration=50,loop=0,optimize=False,disposal=2);images[10].save(ROOT/'previews/native_enemy_combat_fixture.png')
 report={'frame_comparisons':frames,'scenarios':results,'mismatches':0,'scope':'Relocated original type53 enemies, controller-only physical contact and attack, actual coin90 creation/pickup, health/recovery and survival at the restored six-hit capacity; six-hit primary death checked separately, reset determinism; local fights invariant across viewports, travelling survival checked per viewport. Source positions unchanged. Auxiliary flashing, full game-over and device execution excluded.'}
 (ROOT/'docs/session_enemy_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
