#!/usr/bin/env python3
"""Registration, tag filtering and guarded activation against original Thumb."""
import argparse,ctypes,json,random,struct,sys
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from verify_generic_runtime import Original,ROOT,IP,FC,RC,Rom,ROM_BASE
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));actor=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();originalRegistry=[];nativeRegistry=[]
 def hook(uc,addr,size,data):
  if addr in [0x0800bf04,0x0800bee8]:originalRegistry.append(1 if addr==0x0800bf04 else 0);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @REG
 def registry(enabled,ctx):nativeRegistry.append(enabled)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,x in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=x
  return 1
 event=lib.s2_generic_event;event.argtypes=[IP,IP,IP,IP,ctypes.c_int32,FC,REG,ctypes.c_void_p];event.restype=ctypes.c_int
 activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];activate.restype=ctypes.c_int
 init=lib.s2_reactions_init;init.argtypes=[ctypes.c_int32,IP];init.restype=None
 end=lib.s2_generic_reaction_frame_end;end.argtypes=[IP];end.restype=None
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 definition=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['39']['definition'];o.ctor(definition)
 stack=struct.unpack('<I',u.mem_read(o.vm+0x18,4))[0]
 def seed():
  u.mem_write(o.actor+0x250,struct.pack('<i',r[0]));u.mem_write(o.actor+0x298,struct.pack('<i',r[1]));u.mem_write(o.actor+0x254,bytes([r[2]]));u.mem_write(o.actor+0x2a0,struct.pack('<i',r[3]));u.mem_write(o.actor+0x2a4,struct.pack('<i',r[4]));u.mem_write(o.actor+0x164,struct.pack('<i',r[5]));u.mem_write(o.actor+0x1d0,struct.pack('<32i',*r[8:40]));u.mem_write(o.actor+0x258,struct.pack('<16i',*r[40:56]));u.mem_write(o.vm+4,struct.pack('<4i',*v[:4]));u.mem_write(o.vm+0x14,struct.pack('<I',stack+v[2]*20))
  for depth in range(10):u.mem_write(stack+depth*20,struct.pack('<5i',*v[8+depth*5:13+depth*5]))
 def check():
  expected=[struct.unpack('<i',u.mem_read(o.actor+x,4))[0] for x in [0x250,0x298]]+[u.mem_read(o.actor+0x254,1)[0]]+[struct.unpack('<i',u.mem_read(o.actor+x,4))[0] for x in [0x2a0,0x2a4,0x164]]
  assert list(r[:6])==expected,(list(r[:6]),expected)
  assert list(r[8:40])==list(struct.unpack('<32i',u.mem_read(o.actor+0x1d0,128)))
  assert list(r[40:56])==list(struct.unpack('<16i',u.mem_read(o.actor+0x258,64)))
  assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)))
  for d in range(v[2]+1):
   expected=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));expected[2]&=255;assert list(v[8+d*5:13+d*5])==expected,(d,list(v[8+d*5:13+d*5]),expected)
  assert nativeRegistry==originalRegistry,(nativeRegistry,originalRegistry)
 rng=random.Random(202611);cases=0;init(123,r);start(0x0804f650,v)
 # Persistent sequence exercises first/last registration and capacity/replacement.
 for iteration in range(4000):
  id=rng.choice([12,13,14,15]);eid=rng.randrange(22)
  if id==14 and r[1]==8:eid=r[40+2*rng.randrange(8)]
  pair=0x02007300;u.mem_write(pair,struct.pack('<2i',eid,0x0804f650+eid*12));payload=pair if id in [12,14] else eid
  seed();originalRegistry.clear();nativeRegistry.clear();o.message(id,payload,1);cmd=(ctypes.c_int32*3)(8,id,payload);assert event(actor,v,r,cmd,1,fetch,registry,None)==0;check();cases+=1
 # All list sizes; matching/missing IDs, mismatching tags and full VM stack.
 broadcastCases=activationCases=0
 for n in range(17):
  for depth in [-1,0,4,8,9]:
   for variant in range(8):
    init(123,r);r[0]=n;r[1]=min(n,8)
    for i in range(n):r[8+2*i]=i//2;r[9+2*i]=0x0804f650+i*12
    for i in range(min(n,8)):r[40+2*i]=i//2;r[41+2*i]=0x0804f650+i*12
    for i in range(64):v[i]=0
    v[0]=17;v[1]=111;v[2]=depth;v[3]=-9
    for d in range(max(0,depth+1)):v[8+d*5]=0x0804f650;v[9+d*5]=10+d;v[11+d*5]=0x0802547c
    seed();originalRegistry.clear();nativeRegistry.clear();eid=variant if variant<6 else -1;target=[0,123,124,-1][variant%4];cmd=(ctypes.c_int32*3)(9,eid,target);u.mem_write(0x02007200,struct.pack('<3i',*cmd));o.call(0x08013b8c,o.actor,0x02007200);assert event(actor,v,r,cmd,1,fetch,registry,None)==0;check();broadcastCases+=1
    # Guard is a byte, and matching is ID-only regardless of event class/payload.
    for guard in [0,1,255]:
     r[2]=guard;seed();originalRegistry.clear();nativeRegistry.clear();cmd=(ctypes.c_int32*3)(variant-3,eid,-876);u.mem_write(0x02007200,struct.pack('<3i',*cmd));o.call(0x08013a54,o.actor,0x02007200);ret=u.reg_read(UC_ARM_REG_R0);assert activate(v,r,cmd)==ret;check();activationCases+=1
 # Dedicated capacity and replace-at-full checks (random sequence may not fill both).
 capacity=0
 for which,id in [(0,12)]:
  for eid in [5,99]:
   init(123,r);r[which]=16
   for i in range(16):r[(40 if which else 8)+i*2]=i;r[(41 if which else 9)+i*2]=0x0804f650+i*12
   seed();originalRegistry.clear();nativeRegistry.clear();u.mem_write(0x02007300,struct.pack('<2i',eid,0x0804f650));o.message(id,0x02007300,1);assert event(actor,v,r,(ctypes.c_int32*3)(8,id,0x02007300),1,fetch,registry,None)==0;check();capacity+=1
 # Reject the original unsafe ninth broadcast write before any mutation.
 init(123,r);r[1]=8
 for i in range(8):r[40+i*2]=i;r[41+i*2]=0x0804f650
 u.mem_write(0x02007300,struct.pack('<2i',99,0x0804f650));before=list(r);nativeRegistry.clear();assert event(actor,v,r,(ctypes.c_int32*3)(8,14,0x02007300),1,fetch,registry,None)==-4 and list(r)==before and not nativeRegistry
 # Confirm original overlapping storage: ninth entry aliases +0x298/+0x29C.
 seed();o.message(14,0x02007300,1);count=struct.unpack('<i',u.mem_read(o.actor+0x298,4))[0];neighbor=struct.unpack('<i',u.mem_read(o.actor+0x29c,4))[0];assert count==9 and neighbor==0x0804f650
 hazard={'safe_table_start':'0x258','safe_table_end_exclusive':'0x298','original_capacity_check':16,'ninth_entry_overlaps_count':True,'count_after_ninth_add':count,'word_29c_after_ninth_add':neighbor,'native_policy':'reject a new ninth broadcast listener with -4 before mutation; replacement within eight listeners remains supported'}
 result={'unsafe_ninth_listener_rejection':True,'registration_commands':cases,'class9_cases':broadcastCases,'activation_cases':activationCases,'capacity_cases':capacity,'mismatches':0,'scope':'Original registration/removal helpers, handler class-9 tag filter and slot-0x58 activation execute with original VM call handler. BF04/BEE8 world registry effects are recorded callbacks; no full mutable world actor list or game loop.'}
 # Native event-enabled runtime and original whole actor chain.
 from verify_generic_runtime import FIELDS
 runtime_init=lib.s2_generic_runtime_init;runtime_init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP]
 step=lib.s2_generic_runtime_step_events;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG];step.restype=ctypes.c_int
 @RC
 def rand(ctx):return 37
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];whole=0
 for sourceType in [39,18]:
  binding=bindings[str(sourceType)];o.ctor(binding['definition'],xy=(120*256,310*256));stack=struct.unpack('<I',u.mem_read(o.vm+0x18,4))[0];assert runtime_init((ctypes.c_int32*2)(120*256,310*256),0,binding['animation'],0,fetch,None,actor)==0;init(123,r);o.seed(actor)
  if sourceType==39:
   program=0x02007800;subA=0x02007a00;subB=0x02007b00
   bank=json.loads((ROOT/'sprites'/binding['bank']/'bank.json').read_text());other=ROM_BASE+bank['animations'][32]['record_offset']
   for p,data in [(0x02007600,[7,subA]),(0x02007610,[11,subB]),(0x02007620,[-900,49,1792]),(0x02007630,[0,49,1792]),(0x02007640,[256,0,256]),(0x02007650,[0,0,0])]:u.mem_write(p,struct.pack('<'+'i'*len(data),*data))
   commands=[[8,12,0x02007600],[8,14,0x02007610],[8,30,1],[8,22,0x02007630],[5,8,1000],[5,6,0]]
   subCommands=[[8,4,other],[8,22,0x02007620],[5,8,20],[8,45,0],[5,6,0]]
   broadcastCommands=[[8,0,1],[8,21,0x02007640],[5,8,10],[8,21,0x02007650],[5,6,0]]
   for p,cmds in [(program,commands),(subA,subCommands),(subB,broadcastCommands)]:u.mem_write(p,b''.join(struct.pack('<3i',*x) for x in cmds))
  else:program=next(x['script'] for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18)
  start(program,v);seed();o.call(0x08013344,o.vm,program);originalRegistry.clear();nativeRegistry.clear()
  for tick in range(1,241 if sourceType==39 else 181):
   u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick))
   if sourceType==39 and tick in [40,60]:
    cmd=(ctypes.c_int32*3)(9,11,124 if tick==40 else 123);u.mem_write(0x02007200,struct.pack('<3i',*cmd));o.call(0x08013b8c,o.actor,0x02007200);assert event(actor,v,r,cmd,tick,fetch,registry,None)==0
   if sourceType==39 and tick in [100,160,161]:
    for repeat in range(2):
     cmd=(ctypes.c_int32*3)(2,7,456);u.mem_write(0x02007200,struct.pack('<3i',*cmd));o.call(0x08013a54,o.actor,0x02007200);ret=u.reg_read(UC_ARM_REG_R0);assert activate(v,r,cmd)==ret
   o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),actor,v,tick,3200*256,400*256,fetch,rand,None,4096,r,registry)==0,(sourceType,tick)
   check();snap=o.snapshot();diff={i:(actor[i],val) for i,val in snap.items() if actor[i]!=val};assert not diff,(sourceType,tick,diff)
   assert list(actor[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(actor[32:36])==list(struct.unpack('<4i',u.mem_read(o.actor+0x190,16)));assert list(actor[30:32])==list(u.mem_read(o.actor+0x174,2));whole+=1
  if sourceType==18:assert r[0]==1 and r[8]==8 and r[9]==0x080531fc
 result['original_storage_hazard']=hazard;result['whole_actor_event_ticks']=whole;result['whole_actor_scope']='240 ticks with test registrations, tag-filtered class-9 input, two same-frame guarded activations and next-frame reactivation; 180 ticks of original type-18 startup script and original sprite resources. Original ctor, handler, VM and actor update run together; registry/camera/allocator are fixtures. No real sound playback or physical discovery of contact events.'
 (ROOT/'docs/generic_reactions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
