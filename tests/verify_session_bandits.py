#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Bandit AI/physical hit plus explicit owner-event defeat fixture."""
import ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for n,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_health',[ctypes.c_void_p]),('s2_session_player_event',[ctypes.c_void_p,IP]),('s2_session_coin_count',[ctypes.c_void_p]),('s2_session_actor_event',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_aux_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(lib,n).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']
 source=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());results=[];frames=0;images=[]
 with tempfile.TemporaryDirectory() as tmp:
  for pattern,ticks in [('approach',300),('attack',420),('owner_defeat',480)]:
   raw=bytearray(source)
   struct.pack_into('<HH',raw,18+8*44,60 if pattern=='attack'else 100,350)
   p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw);reference=None;summary={}
   for width in [240,480]:
    err=I();h=create(*[str(x).encode()for x in paths],str(p).encode(),ctypes.byref(err));assert h and err.value==0
    assert lib.s2_session_set_viewport(h,width,160)==0
    try:
     for replay in range(2):
      if replay:assert lib.s2_session_reset(h)==0
      pixels=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();enemy=(I*216)();aux=(I*80)();trace=[];min_counter=6;lastAttack=-100
      for tick in range(1,ticks+1):
       if pattern=='owner_defeat'and tick in [20,100,180,260,340,420]:assert lib.s2_session_actor_event(h,9,(I*3)(3,13,0))==1,(width,replay,tick)
       held=0
       if pattern=='attack' and (tick==1 or (enemy[52]>0 and not(enemy[40]&1))):
        dx=enemy[0]-hero[0];dy=enemy[1]-hero[1]
        if tick==1 or (abs(dx)<30*256 and abs(dy)<25*256 and hero[80]<=1 and tick-lastAttack>28):held=2;lastAttack=tick
        elif abs(dx)>24*256:held=16 if dx>0 else 32
       e=lib.s2_session_step(h,held,pixels,len(pixels),info);assert e==0,(pattern,width,replay,tick,e,list(info))
       assert lib.s2_session_snapshot(h,hero)==0;assert lib.s2_session_actor_snapshot(h,9,enemy)==0
       aux[:]=[0]*80;present=lib.s2_session_aux_snapshot(h,9,aux);assert present in [0,1]
       trace.append([*hero,*enemy,present,*aux,lib.s2_session_coin_count(h)]);frames+=1;min_counter=min(min_counter,enemy[52])
       if pattern=='approach'and width==240 and replay==0 and tick%3==0:images.append(Image.frombytes('RGBA',(width,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
      if reference is None:
       requests=(I*(256*8))();n=lib.s2_session_requests(h,requests,256);assert n>=0
       summary={'pattern':pattern,'ticks':ticks,'health':lib.s2_session_health(h),'phase':hero[80],'min_enemy_counter':min_counter,'enemy_removed':bool(enemy[40]&1),'requests':[list(requests[i*8:i*8+8])for i in range(n)]};reference=trace
      else:assert trace==reference,(pattern,width,replay)
      if pattern=='approach':assert summary['health']<6
      elif pattern=='attack':assert min_counter==0 and summary['enemy_removed']
      else:assert summary['enemy_removed'] and any(q[1]==24 and q[4]==90 for q in summary['requests'])
    finally:lib.s2_session_destroy(h)
   results.append(summary)
 images[0].save(ROOT/'previews/native_bandit_contact_fixture.gif',save_all=True,append_images=images[1:],duration=50,loop=0);images[20].save(ROOT/'previews/native_bandit_contact_fixture.png')
 report={'frame_comparisons':frames,'scenarios':results,'mismatches':0,'scope':'Relocated bandit9 uses real controller/physical contact for approach and B hit. Six explicit actor13 owner events verify defeat/drop as a separate event-route check; normal B plus controller chase defeats in two hits; owner-event13 remains a six-hit weak-event fixture. Native auxiliary animation/marker attachment, wide/reset state equality checked; full original world and Android device excluded.'}
 (ROOT/'docs/session_bandit_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
