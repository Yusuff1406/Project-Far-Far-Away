#!/usr/bin/env python3
"""Scripted input replay for the experimental native first-scene harness."""
import ctypes,csv,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
 lib=ctypes.CDLL(str((ROOT/'native/build/libshrek_scene.so').resolve()))
 init=lib.s2_prototype_init;init.argtypes=[ctypes.POINTER(ctypes.c_int32)];init.restype=None
 step=lib.s2_prototype_step;step.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_int32)];step.restype=ctypes.c_int
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];render.restype=ctypes.c_int
 sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];sprite.restype=ctypes.c_int
 anchor=lib.s2_prototype_anchor;anchor.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32)];anchor.restype=ctypes.c_int
 cp=str((ROOT/'collision/scene_00/scene.s2cl').resolve()).encode();sp=str((ROOT/'sprites/shrek_ogre/bank.s2sp').resolve()).encode();scene=str((ROOT/'extracted/scene_00/scene.s2lv').resolve()).encode();s=(ctypes.c_int32*40)();init(s);frames=[];trace=[]
 for tick in range(480):
  buttons=0 if tick<30 else 16
  if tick in [95,170,245,320,395]:buttons|=1
  code=step(cp,sp,buttons,s)
  if code:raise RuntimeError((tick,code))
  trace.append([tick,buttons,s[0],s[1],s[5],s[11],*s[14:18],s[19],s[22],s[26]])
  if tick%3:continue
  x=s[0]//256;y=s[1]//256;cx=max(0,min(3200-240,x-120));cy=max(0,min(400-160,y-95));buf=(ctypes.c_uint8*(240*160*4))();assert render(scene,cx,cy,240,160,-1,buf,len(buf))==0
  image=Image.new('RGBA',(240,160),(24,24,24,255));image.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)))
  point=(ctypes.c_int32*2)();assert anchor(sp,s,point)==0
  assert sprite(sp,s[19],s[22],s[18],240,160,point[0]-cx,point[1]-cy,buf,len(buf))==0;image.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)));frames.append(image.convert('RGB').resize((480,320),Image.Resampling.NEAREST))
 with (ROOT/'docs/prototype_replay.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','buttons','x_q8','y_q8','vx_q8','vy_q8','floor_contacts','left_contacts','right_contacts','ceiling_contacts','animation','sequence_index','logical_state']);w.writerows(trace)
 frames[0].save(ROOT/'previews/native_movement_prototype.gif',save_all=True,append_images=frames[1:],duration=50,loop=0);frames[40].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_movement_prototype.png')
 # A meaningful basic integration check: jump from flat ground and land again.
 init(s)
 for _ in range(10):assert step(cp,sp,0,s)==0
 start_y=s[1];assert s[14]>0
 assert step(cp,sp,1,s)==0;lowest_y=s[1];landed=False
 for _ in range(100):
  assert step(cp,sp,0,s)==0;lowest_y=min(lowest_y,s[1])
  if s[14] and s[1]==start_y:landed=True;break
 assert lowest_y<start_y and landed
 # Walking into the left level boundary must stop at the original one-pixel gap.
 init(s)
 for _ in range(150):assert step(cp,sp,32,s)==0
 assert s[0]>=9*256 and s[0]<=10*256
 result={'scripted_ticks':480,'gif_frames':len(frames),'jump_from_flat_ground':'rises and lands at initial height','left_boundary':'stops with original gap','scope':'Integration test for recovered locomotion subset with recovered actor ordering/body/anchor and no dynamic objects; whole-world scheduling still provisional'}
 (ROOT/'docs/prototype_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
