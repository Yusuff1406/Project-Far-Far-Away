#!/usr/bin/env python3
"""Type10 startup/attack destruction against original generic actor execution."""
import ctypes,json,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC,RC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int,IP];step=lib.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];frames=0;results=[]
 for flip in (0,1):
  for trigger in (None,20,80):
   o=Original(Rom(sys.argv[1]));o.ctor(0x08051c04,(1063*256,254*256),flip);u=o.u;originalFx=[];nativeFx=[]
   def hook(uc,addr,size,data):
    if addr==0x080163ac:originalFx.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)])
    elif addr==0x08009cc0:originalFx.append([19,0,0])
    else:return
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   @FC
   def fetch(addr,out,n,ctx):
    try:raw=u.mem_read(addr,n*4)
    except Exception:return 0
    for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
    return 1
   @RC
   def rng(ctx):return 37
   @REG
   def registry(enabled,ctx):raise AssertionError('Only local reactions expected')
   s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)()
   @SINK
   def sink(kind,address,scale,ctx):
    nativeFx.append([kind,address,scale])
    if kind==19:s[40]|=1;return 0
    return 0 if kind==11 else -4
   assert init((ctypes.c_int32*2)(1063*256,254*256),flip,0x0834ad30,0,fetch,None,s)==0;start(0x08051d70,v);rinit(0,r);o.seed(s);u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));removed=None
   for tick in range(1,241):
    if trigger==tick:
     event=(ctypes.c_int32*3)(1,9,2 if flip else 1);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007200);nativeActivation=activate(v,r,event);assert nativeActivation==u.reg_read(UC_ARM_REG_R0)==1,(flip,trigger,tick,nativeActivation,u.reg_read(UC_ARM_REG_R0),list(r[:18]),list(struct.unpack("<8i",u.mem_read(o.actor+0x1d0,32))))
    for addr in (0x0200324c,0x020033e0):u.mem_write(addr,struct.pack('<i',tick))
    originalFx.clear();nativeFx.clear();o.call(0x08018208,o.actor)
    assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,v,tick,3200*256,400*256,fetch,rng,None,4096,r,registry,sink)==0
    diff={i:(s[i],val) for i,val in o.snapshot().items() if s[i]!=val};assert not diff,(flip,trigger,tick,diff)
    assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));assert originalFx==nativeFx,(tick,originalFx,nativeFx);frames+=1
    if s[40]&1:removed=tick;break
   assert (removed is not None)==(trigger is not None);results.append({'flip':flip,'attack_tick':trigger,'removal_tick':removed})
 report={'original_actor_frames':frames,'scenarios':results,'mismatches':0,'scope':'Original type10 startup and attack9 reaction, real animation/VM helpers. Camera/allocator and sound/scene-bitmap delivery fixtures. Whole world order and dynamic discovery separately tested.'};(ROOT/'docs/breakable_script_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
