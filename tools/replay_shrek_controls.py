#!/usr/bin/env python3
"""Selected entry -> frame contact -> real item script -> Shrek reply -> detach."""
import argparse,ctypes,json,struct
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
DSP=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p);REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);REPLY=ctypes.CFUNCTYPE(ctypes.c_int,IP,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--air",action="store_true");ap.add_argument("--native-frame",action="store_true");ap.add_argument("--trace",action="store_true");args=ap.parse_args();args.air=args.air or args.native_frame;trace=[];transitions=[];lastState=0
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));source=(ctypes.c_int32*80)();item=(ctypes.c_int32*80)();extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();vm=(ctypes.c_int32*64)();reactions=(ctypes.c_int32*72)();tick=0;captures=[];replies=[];deliveries=[];errors=[];book=(ctypes.c_int32*8)();previous=0;states=[]
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
 behavior=lib.s2_shrek_grab_behavior;behavior.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p];locomotion=lib.s2_shrek_locomotion_enter;locomotion.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p];decide=lib.s2_player_decide;decide.argtypes=[ctypes.c_int,IP,IP,IP];physics=lib.s2_actor_move_file;physics.argtypes=[ctypes.c_char_p,IP,IP,IP,IP,ctypes.c_int,ctypes.c_int,ctypes.c_int,IP,IP];preserve=lib.s2_preserve_bottom;preserve.argtypes=[ctypes.c_int,IP,ctypes.c_int,IP];preserve.restype=None;source[40]|=2;assert locomotion(source,extra,status,book,0x158,0,0,0,0x0804b73c,(ctypes.c_int32*3)(1,7,0),res.fetch,None)==0
 landing=lib.s2_shrek_landing_enter;landing.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,ctypes.c_void_p];clear=lib.s2_shrek_clear_contact_event;clear.argtypes=[IP];contact=lib.s2_contact_actions;contact.argtypes=[ctypes.c_int,IP,IP,IP];horizontal=lib.s2_horizontal_input_file;horizontal.argtypes=[ctypes.c_char_p,ctypes.c_int,IP,ctypes.c_int,ctypes.c_int,IP,IP,IP]
 def apply(action):
  if action==0x190:return enter(source,extra,status,tick,tick,0x0804b73c,(ctypes.c_int32*3)(0,12,0),(ctypes.c_int32*3)(0,11,0),res.fetch,dispatch,None,book)
  if action==0x1d8:return clear(source)
  if action==0x178:return landing(source,extra,book,held,tick,0x0804b73c,0x0804b708,res.fetch,sink,None)
  if action==0x10000:return horizontal(str(ROOT/'collision/scene_00/scene.s2cl').encode(),held,source,source[30],source[31],ctypes.cast(ctypes.byref(source,2*4),IP),ctypes.cast(ctypes.byref(source,14*4),IP),ctypes.cast(ctypes.byref(source,18*4),IP))
  return locomotion(source,extra,status,book,action,held,tick,tick,0x0804b73c,(ctypes.c_int32*3)(1,7,0),res.fetch,None)
 playerFrame=lib.s2_shrek_player_step_empty_dynamic;playerFrame.argtypes=[ctypes.c_char_p,IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,IP,IP,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,DSP,ctypes.c_void_p]
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None;frames=[]
 for tick in range(1,361):
  held=4 if tick in [80,240 if args.air else 220] else 16 if 125<=tick<160 else 0
  if args.air and tick in [170,300]:held=1
  code=step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),item,vm,tick,3200*256,400*256,res.fetch,rand,None,4096,reactions,registry,sink);assert code==0,(tick,code,list(vm[:4]))
  if args.native_frame:
   assert playerFrame(str(ROOT/'collision/scene_00/scene.s2cl').encode(),source,extra,status,book,held,tick,tick,(ctypes.c_int32*3)(1,0,0),(ctypes.c_int32*9)(1,7,0,0,12,0,0,11,0),0x0804b73c,0x0804b708,res.fetch,sink,dispatch,None)==0
   states.append([tick,extra[0],extra[1],extra[3],source[0]])
  else:
   source[40]&=~16;clock(source[76],source[77],source[78],tick,ctypes.cast(ctypes.byref(source,20*4),IP))
   ground=physics(str(ROOT/'collision/scene_00/scene.s2cl').encode(),ctypes.cast(ctypes.byref(source,2*4),IP),source,ctypes.cast(ctypes.byref(source,32*4),IP),ctypes.cast(ctypes.byref(source,36*4),IP),source[30],source[31],source[40],ctypes.cast(ctypes.byref(source,14*4),IP),ctypes.cast(ctypes.byref(source,60*4),IP));assert ground>=0
   if args.air:
    contactActions=(ctypes.c_int32*16)();ncontact=contact(extra[0],ctypes.cast(ctypes.byref(source,14*4),IP),(ctypes.c_int32*4)(),contactActions)
    assert ncontact>=0
    for action in contactActions[:ncontact]:assert apply(action)==0
   extra[2]=held
   if extra[0]==8:assert behavior(source,extra,status,book,held,tick,tick,0x0804b73c,(ctypes.c_int32*3)(1,7,0),res.fetch,None)==0
   else:
    assert extra[0] in ([0,1,2,3,4,5] if args.air else [0,1]);inputs=(ctypes.c_int32*15)(held,held&~previous,source[14]!=0,source[15]!=0,source[16]!=0,1,1,source[18],1,1,0,0,source[20],extra[1],source[11]);actions=(ctypes.c_int32*16)();face=(ctypes.c_int32*1)(source[18]);n=decide(extra[0],inputs,actions,face);assert n>=0;source[18]=face[0]
    for i in range(n):
     assert apply(actions[i])==0,(tick,hex(actions[i]),extra[0],source[14])
    status[3]=0
   source[26:28]=source[72:74];source[30:32]=source[74:76];preserve(ground,ctypes.cast(ctypes.byref(source,32*4),IP),source[31],source);previous=held;states.append([tick,extra[0],extra[1],extra[3],source[0]])
  if extra[0]!=lastState:transitions.append([tick,lastState,extra[0],extra[3]]);lastState=extra[0]
  d=(ctypes.c_int32*8)();assert pair(source,extra,0,77,3,item,vm,reactions,res.fetch,None,d)==0
  if d[1]:captures.append([tick,extra[3]])
  diag=(ctypes.c_int32*4)();assert back(item,source,res.fetch,reply,None,diag)==0;assert follow(source,extra,status,item,tick,tick,res.fetch,sink,dispatch,None)==0;assert not errors
  if args.trace:trace.append(list(source)+list(extra)+list(status)+list(book)+list(item)+list(vm)+list(reactions))
  if tick%6:continue
  w=240;h=160;buf=(ctypes.c_uint8*(w*h*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,240,w,h,-1,buf,len(buf))==0;im=Image.new('RGBA',(w,h),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  for s in [source,item]:
   a=res.lookup[s[47]];p=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],p);assert sprite(str(ROOT/'sprites'/a['bank']/'bank.s2sp').encode(),a['index'],s[22],s[18],w,h,p[0]//256,p[1]//256-240,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)))
  draw=ImageDraw.Draw(im);draw.rectangle((0,0,w-1,38),fill='black');draw.text((4,2),'GRAB / WALK / JUMP / LAND' if args.air else 'GRAB CONTROLS / AUTOMATIC IDLE',fill='white');draw.text((4,14),f'{tick:03d} STATE {extra[0]} MODE {extra[1]} ID {extra[3]}',fill=(196,231,152));draw.text((4,26),'INPUT / EMPTY WORLD FIXTURE',fill=(230,211,147));frames.append(im.convert('RGB'))
 exits=[states[i][0] for i in range(1,len(states)) if states[i-1][1]==8 and states[i][1]==0];assert captures==[[80,77]] and replies==[[81,0,18,2,1]] and not extra[3] and exits==[112,272 if args.air else 252] and sum(x[1]==1 for x in states)==35 and source[0]>160*256,(captures,replies,extra[3],exits,sum(x[1]==1 for x in states),source[0],transitions)
 if args.trace:(ROOT/'tests/fixtures').mkdir(parents=True,exist_ok=True);(ROOT/'tests/fixtures/shrek_session_trace.json').write_text(json.dumps(trace)+'\n')
 prefix='native_shrek_frame' if args.native_frame else 'native_shrek_air' if args.air else 'native_shrek_controls'
 if args.air:
  assert sum(t[2]==2 for t in transitions)==2 and sum(t[2]==5 for t in transitions)==2,transitions
 frames[0].save(ROOT/f'previews/{prefix}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[28 if args.air else 24].resize((720,480),Image.Resampling.NEAREST).save(ROOT/f'previews/{prefix}.png')
 result={'transitions':transitions,'native_player_frame':args.native_frame,'air_demo':args.air,'ticks':360,'captures':captures,'item_replies':replies,'detach_deliveries':deliveries,'final_carried_id':extra[3],'gif_frames':len(frames),'automatic_idle_exit_ticks':[states[i][0] for i in range(1,len(states)) if states[i-1][1]==8 and states[i][1]==0],'walk_frames':sum(x[1]==1 for x in states),'final_source_position_q8':list(source[:2]),'scope':('Native C++ selected player frame: animation, static physics, contact response, states0..5/8, geometric direction/jump probes and body update. Real type77 VM response18, carry follow and release11 execute separately in supplied world order. Scripted input and input-activity/drop/idle-timer predicates; explicit empty dynamic world. Full world discovery/lifetime, player timers, attacks, other states, PCM and Android execution excluded.' if args.native_frame else 'Recovered F224 entry, actual grab animation frame boxes, capture through EBC0, original type77 script response and geometric reply18 to Shrek E3A0, carry follow and detach event11. Scripted button4 at tick80 and tick240 (--air) or tick220 (default) drives the existing idle/walk input decisions; second grab entry releases the held item. F1E4 automatically exits to idle. Source uses selected static physics/body updates and idle/walk entries; allowed-direction/input/timer predicates and update ordering are fixtures. With --native-frame, C++ schedules the selected player frame and performs static direction/jump probes; input activity/drop/timer predicates remain supplied. With --air, selected states0..5/8 run with two scripted jumps, contact transitions, F030 landing and F600 event clear. Jump-clear and direction probes remain fixtures; attacks, timers, other states and full D484/world loop are excluded. Explicit empty dynamic world; true scene activation/destruction, PCM and Android execution excluded.')};(ROOT/f'docs/{prefix}_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
