#!/usr/bin/env python3
"""Original F224 grab entry and real type77 updates with no dynamic candidates."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,RC,Rom
from verify_shrek_carry import DSP,SINK
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202618)
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];o.ctor(bindings['18']['definition']);target=o.actor;targetVm=o.vm;stack=struct.unpack('<I',u.mem_read(targetVm+0x14,4))[0];source=0x02005000;sourceSprite=0x0200e000;component=0x0200d000
 enter=lib.s2_shrek_grab_enter;enter.argtypes=[IP,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,IP,FC,DSP,ctypes.c_void_p,IP];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 originalMessages=[];nativeMessages=[]
 def hook(uc,address,size,data):
  if address==0x08013a54:originalMessages.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12))))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 for case in range(6000):
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();out=(ctypes.c_int32*2)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();start(0x08052c28,v);r[0]=1;r[8:10]=[11,0x080531fc];r[2]=case%3==0
  s[2:14]=[rng.randint(-10000,10000) for _ in range(12)];s[18]=case%2;s[47]=0x0834f25c;s[20:24]=[case%2,case%3,0,123];e[0]=rng.randrange(18);e[1]=rng.randrange(9);e[3]=123 if case%4 else 0;status[4]=rng.randint(-10000,10000);status[5]=rng.randrange(256);tick=rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]);animTick=rng.randint(-10000,10000);grab=(ctypes.c_int32*3)(rng.randrange(5),12,rng.randint(-100,100));detach=(ctypes.c_int32*3)(0,11,0)
  u.mem_write(source,struct.pack('<I',0x020017cc));u.mem_write(source+0x1bc,struct.pack('<I',component));u.mem_write(component,struct.pack('<12i',*s[2:14]));u.mem_write(source+0x1c0,struct.pack('<I',sourceSprite));u.mem_write(sourceSprite,bytes([s[20]]));u.mem_write(sourceSprite+4,struct.pack('<4i',s[21],s[47],s[22],s[23]));u.mem_write(sourceSprite+0x28,bytes([s[18],0]));u.mem_write(source+0x1e8,struct.pack('<I',0x0804b73c));u.mem_write(source+0x260,bytes(4));u.mem_write(source+0x240,struct.pack('<3i',*grab));u.mem_write(source+0x234,struct.pack('<3i',*detach));u.mem_write(source+0x1ec,struct.pack('<I',target if e[3] else 0));u.mem_write(source+0x258,struct.pack('<i',e[1]));u.mem_write(source+0x1d0,struct.pack('<i',status[4]));u.mem_write(source+0x1c8,bytes([status[5]]));u.mem_write(0x0200324c,struct.pack('<i',animTick));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(target+0x250,struct.pack('<i',1));u.mem_write(target+0x1d0,struct.pack('<2i',11,0x080531fc));u.mem_write(target+0x254,bytes([r[2]]));u.mem_write(target+0x2a0,bytes(8));u.mem_write(targetVm+4,struct.pack('<4i',*v[:4]));u.mem_write(stack,struct.pack('<5i',*v[8:13]));originalMessages.clear();nativeMessages.clear()
  @DSP
  def dispatch(ident,event,ctx):assert ident==123;nativeMessages.append(list(event[:3]));activate(v,r,event);return 0
  o.call(0x0800f224,source);assert enter(s,e,status,tick,animTick,0x0804b73c,grab,detach,fetch,dispatch,None,out)==0
  actual=[list(s[2:14]),list(s[41:44]),s[47],list(s[20:24]),e[0],e[1],e[3],status[4],status[5],list(out)];expected=[list(struct.unpack('<12i',u.mem_read(component,48))),list(struct.unpack('<3i',u.mem_read(source+0x1a0,12))),struct.unpack('<i',u.mem_read(sourceSprite+8,4))[0],[u.mem_read(sourceSprite,1)[0],struct.unpack('<i',u.mem_read(sourceSprite+4,4))[0],*struct.unpack('<2i',u.mem_read(sourceSprite+12,8))],struct.unpack('<i',u.mem_read(source+0x1d8,4))[0],struct.unpack('<i',u.mem_read(source+0x258,4))[0],123 if struct.unpack('<I',u.mem_read(source+0x1ec,4))[0] else 0,struct.unpack('<i',u.mem_read(source+0x1d0,4))[0],u.mem_read(source+0x1c8,1)[0],[struct.unpack('<i',u.mem_read(source+0x260,4))[0],struct.unpack('<i',u.mem_read(source+0x25c,4))[0]]];assert actual==expected,(case,actual,expected);assert nativeMessages==originalMessages;assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(targetVm+4,16)))
 # Real type77 startup, floor wait, listener registration and original grab response.
 spec=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==77);o.ctor(spec['definition'],xy=(120*256,340*256));s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];assert init((ctypes.c_int32*2)(120*256,340*256),0,spec['initial_animation'],0,fetch,None,s)==0;o.seed(s);u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));u.mem_write(o.actor+0x148,bytes(4));start(spec['script'],v);o.call(0x08013344,o.vm,spec['script']);stack=struct.unpack('<I',u.mem_read(o.vm+0x14,4))[0];effects=[]
 @REG
 def registry(enabled,ctx):raise AssertionError('local-only script')
 @RC
 def rand(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):effects.append([kind,address,scale]);return 0
 step=lib.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];seen12=False
 for tick in range(1,481):
  if tick==120:
   assert any(r[8+2*i]==12 for i in range(r[0]));event=(ctypes.c_int32*3)(0,12,1);u.mem_write(0x02007300,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007300);assert activate(v,r,event)==1
  if tick==130:s[40]|=16;u.mem_write(o.actor+0x15c,bytes([s[40]])) # successful outgoing reply supplied by integration owner
  u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));o.call(0x08018208,o.actor);code=step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,v,tick,3200*256,400*256,fetch,rand,None,4096,r,registry,sink);assert code==0,(tick,code,list(v[:4]),s[40]);snap=o.snapshot();assert all(s[i]==value for i,value in snap.items()),(tick,{i:(s[i],value) for i,value in snap.items() if s[i]!=value});assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));assert [r[0],r[2],r[3],r[4]]==[struct.unpack('<i',u.mem_read(o.actor+0x250,4))[0],u.mem_read(o.actor+0x254,1)[0],*struct.unpack('<2i',u.mem_read(o.actor+0x2a0,8))]
  for d in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));f[2]&=255;assert list(v[8+d*5:13+d*5])==f
  seen12|=any(r[8+2*i]==12 for i in range(r[0]))
 assert seen12 and not effects
 result={'original_grab_entry_cases':6000,'real_type77_actor_ticks':480,'type77_registered_grab_listener':seen12,'final_listeners':list(r[8:8+r[0]*2]),'mismatches':0,'scope':'Original F224 entry, release of previous carried actor, event copy, motion10 animation/cache/sound and X triple (Y preserved). Original type77 18208 startup/grab response with explicit empty dynamic candidates, real script/physics and VM stacks. Grab trigger at tick120 and successful outgoing-reply flag at tick130 are integration fixtures; full player state8 FSM and world scheduling remain separate.'};(ROOT/'docs/shrek_grab_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
