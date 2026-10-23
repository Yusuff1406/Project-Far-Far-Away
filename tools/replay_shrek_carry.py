#!/usr/bin/env python3
"""Native carry tail with locomotion and carried-object graphics; ownership is a fixture."""
import ctypes,json,struct,csv
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC
DSP=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p)
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));pose=(ctypes.c_int32*80)();target=(ctypes.c_int32*80)();player=(ctypes.c_int32*40)();extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();tick=0;events=[];effects=[]
 lib.s2_prototype_init.argtypes=[IP];lib.s2_prototype_init(player);move=lib.s2_prototype_step;move.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,IP];init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];profile=lib.s2_shrek_reactions_init;profile.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32];assert profile(pose,extra,status,4,0)==0;assert init((ctypes.c_int32*2)(190*256,310*256),0,0x08342dcc,0,res.fetch,None,target)==0
 extra[0]=8;extra[3]=77;receive=lib.s2_shrek_receive;receive.argtypes=[IP,IP,IP,ctypes.c_int32];assert receive(extra,status,(ctypes.c_int32*3)(0,18,0),0)==1
 follow=lib.s2_shrek_carry_follow;follow.argtypes=[IP,IP,IP,IP,ctypes.c_int32,ctypes.c_int32,FC,SINK,DSP,ctypes.c_void_p];release=lib.s2_shrek_carry_release;release.argtypes=[IP,IP,ctypes.c_int32,IP,DSP,ctypes.c_void_p];clock=lib.s2_animation_step;clock.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int32,IP];clock.restype=None
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 @DSP
 def dispatch(ident,event,ctx):events.append([tick,ident,*event[:3],extra[1]]);return 0 # delivery recorder, no subtype script/physics
 @SINK
 def sink(kind,address,scale,ctx):effects.append([tick,kind,address,scale]);return 0
 cp=str(ROOT/'collision/scene_00/scene.s2cl').encode();sp=str(ROOT/'sprites/shrek_ogre/bank.s2sp').encode();frames=[];trace=[]
 for tick in range(1,361):
  buttons=16 if 40<=tick<110 else 32 if 235<=tick<300 else 0
  assert move(cp,sp,buttons,player)==0;pose[:2]=player[:2];pose[18]=player[18];pose[30:32]=player[30:32];pose[22]=player[22];pose[47]=0x0834f25c+24*player[19];raw=bytes.fromhex(res.lookup[pose[47]]['header_hex']);bounds=struct.unpack_from('<hhBB',raw,12);pose[26:28]=bounds[:2];pose[72:76]=bounds
  extra[2]=2 if 150<=tick<200 else 0
  if tick==220:extra[3]=77;extra[0]=8;assert receive(extra,status,(ctypes.c_int32*3)(0,21,0),tick)==1 # supplied reacquisition/handshake
  if tick==340:assert release(extra,status,tick,(ctypes.c_int32*3)(0,11,0),dispatch,None)==0
  clock(target[76],target[77],target[78],tick,ctypes.cast(ctypes.byref(target,20*4),IP));assert follow(pose,extra,status,target,tick,tick,res.fetch,sink,dispatch,None)==0
  trace.append([tick,*pose[:2],*target[:2],extra[1],extra[3],target[47],target[22],status[5],status[6],len(events),len(effects)])
  if tick%6:continue
  w=240;h=160;cx=max(0,(pose[0]>>8)-120);cy=240;buf=(ctypes.c_uint8*(w*h*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),cx,cy,w,h,-1,buf,len(buf))==0;im=Image.new('RGBA',(w,h),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  for s in [pose,target]:
   a=res.lookup[s[47]];point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point);assert sprite(str(ROOT/'sprites'/a['bank']/'bank.s2sp').encode(),a['index'],s[22],s[18],w,h,point[0]//256-cx,point[1]//256-cy,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  d=ImageDraw.Draw(im);d.rectangle((0,0,w-1,38),fill='black');d.text((4,2),'CARRY FOLLOW / ACTION / RELEASE',fill='white');d.text((4,14),f'{tick:03d} MODE {extra[1]} HELD {extra[3]} BYTE {status[5]}',fill=(196,231,152));d.text((4,26),'OWNERSHIP / DELIVERY FIXTURES',fill=(230,211,147));frames.append(im.convert('RGB'))
 assert [e[3] for e in events]==[29,11] and not extra[3] and len(effects)==3
 frames[0].save(ROOT/'previews/native_shrek_carry.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[15].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_shrek_carry.png')
 with (ROOT/'docs/native_shrek_carry.csv').open('w',newline='') as f:
  out=csv.writer(f);out.writerow(['tick','player_x','player_y','carried_x','carried_y','mode','carried_id','animation','sequence','byte_1c8','next_fx_tick','events','fx']);out.writerows(trace)
 result={'ticks':360,'gif_frames':len(frames),'delivered_events':events,'sound_requests':effects,'final_carried_id':extra[3],'scope':'Native locomotion plus recovered carry positioning/facing, mode1 carried animation/throw event, mode5 sound timer/byte toggle and detach. Initial ownership, reacquisition and incoming messages18/21 are explicit fixtures; target uses bank_342d40 graphics with standalone animation clock. Dispatch records events without subtype script/projectile physics, world removal/destructor lifecycle, actual PCM or Android execution.'};(ROOT/'docs/native_shrek_carry_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
