#!/usr/bin/env python3
"""Two normalized actors receive native stable-list broadcasts and local triggers."""
import ctypes,csv,json
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);CB=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None;rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int32,IP];rinit.restype=None
 step=lib.s2_generic_runtime_step_events;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG];event=lib.s2_generic_event;event.argtypes=[IP,IP,IP,IP,ctypes.c_int32,FC,REG,ctypes.c_void_p];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];broadcast=lib.s2_event_broadcast;broadcast.argtypes=[ctypes.POINTER(ctypes.c_uint32),IP,ctypes.c_int,IP,CB,ctypes.c_void_p]
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['39'];animations={x['index']:x['address'] for x in res.animations if x['bank']==binding['bank']};program=0x02007800;subA=0x02007a00;subB=0x02007b00
 for p,data in [(0x02007600,[7,subA]),(0x02007610,[11,subB]),(0x02007620,[-900,49,1792]),(0x02007630,[0,49,1792]),(0x02007640,[256,0,256]),(0x02007650,[0,0,0])]:res.put(p,data)
 for p,cmds in [(program,[[8,12,0x02007600],[8,14,0x02007610],[8,30,1],[8,22,0x02007630],[5,8,1000],[5,6,0]]),(subA,[[8,4,animations[32]],[8,22,0x02007620],[5,8,20],[8,45,0],[5,6,0]]),(subB,[[8,0,1],[8,21,0x02007640],[5,8,10],[8,21,0x02007650],[5,6,0]])]:res.put(p,[v for cmd in cmds for v in cmd])
 actors={};listeners=[];registryLog=[];currentTick=0
 for ident,x,tag in [(1,100,123),(2,190,456)]:
  s=(ctypes.c_int32*80)();vm=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(x*256,310*256),0,binding['animation'],0,res.fetch,None,s)==0;start(program,vm);rinit(tag,r)
  def make_registry(actorID):
   @REG
   def register(enabled,ctx):
    registryLog.append([currentTick,actorID,enabled])
    if enabled and actorID not in listeners:listeners.append(actorID)
    if not enabled and actorID in listeners:listeners.remove(actorID)
   return register
  actors[ident]=(s,vm,r,make_registry(ident))
 @RC
 def random_value(ctx):return 37
 received=[]
 @CB
 def receiver(ident,cmd,ctx):
  s,vm,r,reg=actors[ident];before=vm[2];code=event(s,vm,r,cmd,currentTick,res.fetch,reg,None);received.append([currentTick,ident,cmd[0],cmd[1],cmd[2],before,vm[2],code]);return code
 frames=[];trace=[];activation=[];subtitle='REGISTER REACTIONS'
 for currentTick in range(1,241):
  if currentTick in [40,60,140]:
   tag={40:999,60:123,140:0}[currentTick];cmd=(ctypes.c_int32*3)(9,11,tag);ids=(ctypes.c_uint32*len(listeners))(*listeners);adjust=(ctypes.c_int32*len(listeners))();assert broadcast(ids,adjust,len(listeners),cmd,receiver,None)==len(listeners);subtitle='TAG MISS' if tag==999 else 'TARGET ACTOR 1' if tag==123 else 'BROADCAST TO BOTH'
  if currentTick in [100,160,161]:
   s,vm,r,reg=actors[1];cmd=(ctypes.c_int32*3)(2,7,456);returns=[activate(vm,r,cmd),activate(vm,r,cmd)];assert returns==[1,0];activation.append([currentTick,*returns]);subtitle='LOCAL TRIGGER: 1 THEN 0'
  for ident,(s,vm,r,reg) in actors.items():
   assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,currentTick,3200*256,400*256,res.fetch,random_value,None,4096,r,reg)==0;trace.append([currentTick,ident,*s[:2],s[5],s[11],s[47],s[22],vm[2],r[0],r[1],r[2]])
  if currentTick%4:continue
  width=320;height=160;buf=(ctypes.c_uint8*(width*height*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,230,width,height,-1,buf,len(buf))==0;im=Image.new('RGBA',(width,height),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)))
  for ident,(s,vm,r,reg) in actors.items():
   item=res.lookup[s[47]];point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point);assert sprite(str(ROOT/'sprites'/item['bank']/'bank.s2sp').encode(),item['index'],s[22],s[18],width,height,point[0]//256,point[1]//256-230,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)));ImageDraw.Draw(im).text((max(0,s[0]//256-8),max(28,s[1]//256-230-s[31]//2-12)),str(ident),fill='yellow')
  d=ImageDraw.Draw(im);d.rectangle((0,0,width-1,26),fill='black');d.text((4,2),'NATIVE EVENTS / TEST SCRIPTS',fill='white');d.text((4,14),f'{currentTick:03d} {subtitle}',fill=(196,231,152));frames.append(im.convert('RGB'))
 frames[0].save(ROOT/'previews/native_actor_events.gif',save_all=True,append_images=frames[1:],duration=67,loop=0);frames[34].resize((960,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_actor_events.png')
 with (ROOT/'docs/native_actor_events.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','actor','x_q8','y_q8','vx_q8','vy_q8','animation_address','sequence','vm_depth','local_count','broadcast_count','guard_after_frame']);w.writerows(trace)
 assert len(received)==6 and all(x[-1]==0 for x in received);assert received[0][5]==received[0][6] and received[1][5]==received[1][6];assert received[2][6]==received[2][5]+1 and received[3][6]==received[3][5];assert all(x[6]==x[5]+1 for x in received[4:])
 result={'actors':2,'ticks':240,'actor_ticks':480,'gif_frames':len(frames),'registry_log':registryLog,'broadcast_deliveries':received,'guarded_activations':activation,'scope':'Native stable-list broadcast, registry callbacks and event-enabled generic actor/VM runtime. Scripts, trigger times, tags and actor placement are fixtures; artwork/scene/collision are original resources. No original enemy AI, contact discovery or Android execution.'};(ROOT/'docs/native_actor_events_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
