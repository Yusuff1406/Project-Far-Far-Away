#!/usr/bin/env python3
"""Selected entry -> frame contact -> real item script -> Shrek reply -> detach."""
import ctypes,json,struct
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
DSP=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p);REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);REPLY=ctypes.CFUNCTYPE(ctypes.c_int,IP,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));source=(ctypes.c_int32*80)();item=(ctypes.c_int32*80)();extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();vm=(ctypes.c_int32*64)();reactions=(ctypes.c_int32*72)();tick=0;captures=[];replies=[];deliveries=[];errors=[]
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];assert init((ctypes.c_int32*2)(123*256,349*256),0,0x0834f25c,0,res.fetch,None,source)==0;assert init((ctypes.c_int32*2)(120*256,340*256),0,0x08342dcc,0,res.fetch,None,item)==0;profile=lib.s2_shrek_reactions_init;profile.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32];assert profile(source,extra,status,4,0)==0;start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start(0x0804d084,vm)
 enter=lib.s2_shrek_grab_enter;enter.argtypes=[IP,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,IP,FC,DSP,ctypes.c_void_p,IP];release=lib.s2_shrek_carry_release;release.argtypes=[IP,IP,ctypes.c_int32,IP,DSP,ctypes.c_void_p];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];receive=lib.s2_shrek_receive;receive.argtypes=[IP,IP,IP,ctypes.c_int32]
 step=lib.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];pair=lib.s2_shrek_contact_pair;pair.argtypes=[IP,IP,ctypes.c_int32,ctypes.c_uint32,ctypes.c_int,IP,IP,IP,FC,ctypes.c_void_p,IP];back=lib.s2_generic_contact_pair_receiver;back.argtypes=[IP,IP,FC,REPLY,ctypes.c_void_p,IP];follow=lib.s2_shrek_carry_follow;follow.argtypes=[IP,IP,IP,IP,ctypes.c_int32,ctypes.c_int32,FC,SINK,DSP,ctypes.c_void_p];clock=lib.s2_animation_step;clock.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int32,IP];clock.restype=None
 @REG
 def registry(enabled,ctx):errors.append('unexpected broadcast registry')
 @RC
 def rand(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):errors.append(['unsupported effect',kind,address]);return -4
 @DSP
 def dispatch(ident,event,ctx):assert ident==77;deliveries.append([tick,*event[:3]]);activate(vm,reactions,event);return 0
 @REPLY
 def reply(event,ctx):result=receive(extra,status,event,tick);replies.append([tick,*event[:3],result]);return result
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None;frames=[]
 for tick in range(1,361):
  if tick==80:assert enter(source,extra,status,tick,tick,0x0804b73c,(ctypes.c_int32*3)(0,12,0),(ctypes.c_int32*3)(0,11,0),res.fetch,dispatch,None,(ctypes.c_int32*2)())==0
  if tick==220:assert release(extra,status,tick,(ctypes.c_int32*3)(0,11,0),dispatch,None)==0
  code=step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),item,vm,tick,3200*256,400*256,res.fetch,rand,None,4096,reactions,registry,sink);assert code==0,(tick,code,list(vm[:4]));source[40]&=~16;clock(source[76],source[77],source[78],tick,ctypes.cast(ctypes.byref(source,20*4),IP))
  d=(ctypes.c_int32*8)();assert pair(source,extra,0,77,3,item,vm,reactions,res.fetch,None,d)==0
  if d[1]:captures.append([tick,extra[3]])
  diag=(ctypes.c_int32*4)();assert back(item,source,res.fetch,reply,None,diag)==0;assert follow(source,extra,status,item,tick,tick,res.fetch,sink,dispatch,None)==0;assert not errors
  if tick%6:continue
  w=240;h=160;buf=(ctypes.c_uint8*(w*h*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,240,w,h,-1,buf,len(buf))==0;im=Image.new('RGBA',(w,h),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  for s in [source,item]:
   a=res.lookup[s[47]];p=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],p);assert sprite(str(ROOT/'sprites'/a['bank']/'bank.s2sp').encode(),a['index'],s[22],s[18],w,h,p[0]//256,p[1]//256-240,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  draw=ImageDraw.Draw(im);draw.rectangle((0,0,w-1,38),fill='black');draw.text((4,2),'GRAB ENTRY / REAL ITEM SCRIPT REPLY',fill='white');draw.text((4,14),f'{tick:03d} STATE {extra[0]} MODE {extra[1]} ID {extra[3]}',fill=(196,231,152));draw.text((4,26),'ENTRY TIMING / EMPTY WORLD FIXTURE',fill=(230,211,147));frames.append(im.convert('RGB'))
 assert captures and captures[0][1]==77 and any(x[2]==18 and x[-1]==1 for x in replies) and not extra[3]
 frames[0].save(ROOT/'previews/native_shrek_grab.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[15].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_shrek_grab.png')
 result={'ticks':360,'captures':captures,'item_replies':replies,'detach_deliveries':deliveries,'final_carried_id':extra[3],'gif_frames':len(frames),'scope':'Recovered F224 entry, actual grab animation frame boxes, capture through EBC0, original type77 script response and geometric reply18 to Shrek E3A0, carry follow and detach event11. Entry/release timing and initial actor placement are fixtures; source pose/clock has no full state8 FSM or locomotion update. Explicit empty dynamic world; true scene activation/destruction, PCM and Android execution excluded.'};(ROOT/'docs/native_shrek_grab_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
