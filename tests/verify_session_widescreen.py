#!/usr/bin/env python3
"""Different viewports must leave gameplay, requests and effect clocks identical."""
import ctypes,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
IP=ctypes.POINTER(ctypes.c_int32)

def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p
 destroy=lib.s2_session_destroy;destroy.argtypes=[ctypes.c_void_p]
 step=lib.s2_session_step;step.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]
 viewport=lib.s2_session_set_viewport;viewport.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
 snapshot=lib.s2_session_snapshot;snapshot.argtypes=[ctypes.c_void_p,IP]
 effects=lib.s2_session_effect_state;effects.argtypes=[ctypes.c_void_p,IP]
 requests=lib.s2_session_requests;requests.argtypes=[ctypes.c_void_p,IP,ctypes.c_size_t]
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']]
 widths=[240,284,320,356,373,480,640];states=[];buffers=[];handles=[];infos=[];ef=[];refusals=0;compared=0;crop=0
 def image(buf,w):return Image.frombytes('RGBA',(w,160),bytes(buf),'raw','BGRA').convert('RGB')
 try:
  for width in widths:
   error=ctypes.c_int32();h=create(*paths,ctypes.byref(error));assert h and not error.value;handles.append(h)
   assert viewport(h,width,160)==0
   states.append((ctypes.c_int32*320)());buffers.append((ctypes.c_uint32*(width*160))());infos.append((ctypes.c_int32*8)());ef.append((ctypes.c_int32*9)())
  for h,state in zip(handles,states):
   snapshot(h,state);before=list(state)
   for w,height in [(239,160),(641,160),(-1,160),(320,0),(320,161),(2147483647,160)]:
    assert viewport(h,w,height)==-1;assert snapshot(h,state)==0 and list(state)==before;refusals+=1
  assert viewport(None,320,160)==-1;refusals+=1
  assert step(handles[-1],0,buffers[-1],38400,infos[-1])==-1;refusals+=1
  frames=[]
  for tick in range(1,401):
   held=4 if tick==80 else 16 if 125<=tick<130 else 2 if 130<=tick<=190 else 0
   for i,w in enumerate(widths):
    assert step(handles[i],held,buffers[i],len(buffers[i]),infos[i])==0
    assert snapshot(handles[i],states[i])==0 and effects(handles[i],ef[i])==0
    assert all(p>>24==255 for p in buffers[i])
    if i:
     assert list(states[i])==list(states[0]),(tick,w)
     assert list(infos[i])==list(infos[0]) and list(ef[i])==list(ef[0]);compared+=1
     if tick<=79:
      for y in range(160):assert list(buffers[i][y*w:y*w+240])==list(buffers[0][y*240:(y+1)*240])
      crop+=1
   if tick==70:
    image(buffers[0],240).resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_session_widescreen_original.png')
    image(buffers[3],356).resize((1068,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_session_widescreen_wide.png')
   if tick%6==0:frames.append(image(buffers[3],356).resize((712,320),Image.Resampling.NEAREST))
  rows=[]
  for h in handles:
   r=(ctypes.c_int32*(8*256))();n=requests(h,r,256);assert n==5;rows.append(list(r[:n*8]))
  assert all(row==rows[0] for row in rows)
  # Change format repeatedly inside the same active session, without a restart.
  for tick in range(401,481):
   w=widths[tick%len(widths)];buf=(ctypes.c_uint32*(w*160))()
   assert viewport(handles[-1],w,160)==0
   assert step(handles[0],0,buffers[0],38400,infos[0])==0
   assert step(handles[-1],0,buf,len(buf),infos[-1])==0
   snapshot(handles[0],states[0]);snapshot(handles[-1],states[-1]);assert list(states[0])==list(states[-1]);compared+=1
  frames[0].save(ROOT/'previews/native_session_widescreen.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
 finally:
  for h in handles:destroy(h)
 result={'widths':widths,'height':160,'gameplay_frame_comparisons':compared,'common_area_pixel_frame_comparisons':crop,'live_format_switches':80,'invalid_size_or_capacity_refusals':refusals,'request_queues_equal':True,'mismatches':0,'scope':'Owned scene, native rendering, all320 gameplay words, effects and requests. Common pixels checked while both cameras share the left-edge position; no Android device execution or general world activation.'}
 (ROOT/'docs/session_widescreen_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
