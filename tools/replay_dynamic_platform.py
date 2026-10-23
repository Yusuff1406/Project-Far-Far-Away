#!/usr/bin/env python3
"""Native integration demo; platform is a research fixture, not a ROM object."""
import argparse,ctypes,json,csv
from replay_generic_actor import Resources,FC
from replay_shrek_controls import SINK,DSP
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--native-frame",action="store_true");args=ap.parse_args()
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);init=lib.s2_prototype_init;init.argtypes=[ip];init.restype=None;step=lib.s2_prototype_step_dynamic;step.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ip,ip,ctypes.c_int,ip];step.restype=ctypes.c_int;build=lib.s2_dynamic_surfaces;build.argtypes=[ip,ctypes.c_int,ctypes.c_int,ip,ip,ctypes.c_int,ip];build.restype=ctypes.c_int
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];render.restype=ctypes.c_int;sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];sprite.restype=ctypes.c_int;anchor=lib.s2_prototype_anchor;anchor.argtypes=[ctypes.c_char_p,ip,ip];anchor.restype=ctypes.c_int
 cp=str(ROOT/'collision/scene_00/scene.s2cl').encode();sp=str(ROOT/'sprites/shrek_ogre/bank.s2sp').encode();scene=str(ROOT/'extracted/scene_00/scene.s2lv').encode();s=(ctypes.c_int32*40)();init(s);s[0]=160*256;s[1]=262*256;s[27]=s[1];s[32]=s[0]-2048;s[33]=s[1]-6400;s[36]=s[0];s[37]=s[1];lastX=160;frames=[];trace=[]
 if args.native_frame:
  res=Resources();pose=(ctypes.c_int32*80)();extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();initializer=lib.s2_generic_runtime_init;initializer.argtypes=[ip,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,ip]
  assert initializer((ctypes.c_int32*2)(163*256,261*256),0,0x0834f25c,0,res.fetch,None,pose)==0;pose[40]=6
  enter=lib.s2_shrek_locomotion_enter;enter.argtypes=[ip,ip,ip,ip,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,ip,FC,ctypes.c_void_p];assert enter(pose,extra,status,book,0x158,0,0,0,0x0804b73c,(ctypes.c_int32*3)(1,7,0),res.fetch,None)==0
  frame=lib.s2_shrek_player_step_dynamic;frame.argtypes=[ctypes.c_char_p,ip,ip,ip,ip,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ip,ip,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,DSP,ctypes.c_void_p,ip,ctypes.c_int]
  @SINK
  def sink(k,r,g,c):return 0
  @DSP
  def dispatch(i,e,c):raise AssertionError('Unexpected carry delivery')
  pointFn=lib.s2_actor_anchor_q8;pointFn.argtypes=[ip,ip,ctypes.c_int,ctypes.c_int,ip];pointFn.restype=None
 for tick in range(1,241):
  phase=tick%160;x=160+(phase if phase<=80 else 160-phase);delta=(x-lastX)*256;lastX=x;surfaces=(ctypes.c_int32*36)();flags=(ctypes.c_int32*1)(1);n=build((ctypes.c_int32*2)(x*256,292*256),96,8,flags,(ctypes.c_int32*2)(delta,0),0,surfaces);dyn=(ctypes.c_int32*4)();
  if args.native_frame:
   assert frame(cp,pose,extra,status,book,0,tick,tick,(ctypes.c_int32*3)(1,0,0),(ctypes.c_int32*9)(1,7,0,0,12,0,0,11,0),0x0804b73c,0x0804b708,res.fetch,sink,dispatch,None,surfaces,n)==0
   s[:24]=pose[:24];s[26]=extra[0];s[19]=res.lookup[pose[47]]['index'];dyn[:]=pose[64:68]
  else:assert step(cp,sp,0,s,surfaces,n,dyn)==0
  assert s[0]==x*256 and s[1]==262*256 and dyn[0]>0,(tick,list(s[:2]),x,list(dyn));trace.append([tick,x*256,delta,*s[:2],*dyn,s[26]])
  if tick%6:continue
  cx,cy=100,230;buf=(ctypes.c_uint8*(240*160*4))();assert render(scene,cx,cy,240,160,-1,buf,len(buf))==0;im=Image.new('RGBA',(240,160),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)));draw=ImageDraw.Draw(im);draw.rectangle((x-48-cx,288-cy,x+48-cx,296-cy),fill=(113,93,42,255),outline=(208,177,99,255));draw.rectangle((2,146,126,159),fill=(0,0,0,255));draw.text((5,148),'MOVING PLATFORM TEST',fill=(255,255,255,255));point=(ctypes.c_int32*2)();
  if args.native_frame:pointFn(ctypes.cast(ctypes.byref(pose,72*4),ip),pose,pose[18],pose[38],point);point[0]>>=8;point[1]>>=8
  else:assert anchor(sp,s,point)==0
  assert sprite(sp,s[19],s[22],s[18],240,160,point[0]-cx,point[1]-cy,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)));frames.append(im.convert('RGB'))
 prefix='native_player_platform' if args.native_frame else 'native_dynamic_platform'
 frames[0].save(ROOT/f'previews/{prefix}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[12].resize((720,480),Image.Resampling.NEAREST).save(ROOT/f'previews/{prefix}.png')
 with (ROOT/('native_player_platform_replay.csv' if args.native_frame else 'dynamic_platform_replay.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','platform_x_q8','platform_dx_q8','player_x_q8','player_y_q8','dynamic_floor','dynamic_left','dynamic_right','dynamic_ceiling','logical_state']);w.writerows(trace)
 result={'native_player_frame':args.native_frame,'ticks':240,'frames':len(frames),'checks':'Player carried by platform in both directions; constant standing height and nonzero dynamic floor contact every tick','scope':'Native integration, synthetic platform fixture drawn over original scene. Original object-spawn logic and platform AI not used.'};(ROOT/('native_player_platform_validation.json' if args.native_frame else 'dynamic_platform_validation.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
