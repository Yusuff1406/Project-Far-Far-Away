#!/usr/bin/env python3
"""Original type14/16 scripts and packed collision-mask helper, not carry integration."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC,RC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int,IP];step=lib.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];msg=lib.s2_generic_message;msg.argtypes=[IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,FC,ctypes.c_void_p]
 r=Rom(sys.argv[1]);frames=0;results=[]
 for type,definition,animation,program,xy,events in [(14,0x080526a4,0x0834acb8,0x08052714,(1296,358),[None,2,5,10,11,12,41]),(16,0x08052684,0x0834abc8,0x080528e0,(1919,254),[None,8,2,5,10,11,12])]:
  for flip in (0,1):
   for eventId in events:
    o=Original(r);o.ctor(definition,tuple(x*256 for x in xy),flip);u=o.u;originalFx=[];nativeFx=[]
    def hook(uc,addr,size,data):
     if addr!=0x080163ac:return
     originalFx.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
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
    @SINK
    def sink(kind,address,scale,ctx):nativeFx.append([kind,address,scale]);return 0 if kind==11 else -4
    s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();reactions=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(*(x*256 for x in xy)),flip,animation,0,fetch,None,s)==0;start(program,v);rinit(0,reactions);o.seed(s);u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));accepted=[];sounds=[]
    for tick in range(1,161):
     if eventId is not None and tick in (20,80):
      event=(ctypes.c_int32*3)(1,eventId,2 if flip else 1);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007200);a=activate(v,reactions,event);assert a==u.reg_read(UC_ARM_REG_R0);accepted.append(a)
     for addr in (0x0200324c,0x020033e0):u.mem_write(addr,struct.pack('<i',tick))
     originalFx.clear();nativeFx.clear();o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,v,tick,3200*256,400*256,fetch,rng,None,4096,reactions,registry,sink)==0,(type,flip,eventId,tick,list(v[:12]),list(s[39:48]))
     diff={i:(s[i],val) for i,val in o.snapshot().items() if s[i]!=val};assert not diff,(type,flip,eventId,tick,diff)
     assert s[25]==(struct.unpack('<H',u.mem_read(o.actor+6,2))[0]>>6)&255==63
     assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));assert originalFx==nativeFx,(type,tick,originalFx,nativeFx)
     assert reactions[0]==struct.unpack('<I',u.mem_read(o.actor+0x250,4))[0];assert list(reactions[8:8+2*reactions[0]])==list(struct.unpack('<'+'i'*(2*reactions[0]),u.mem_read(o.actor+0x1d0,8*reactions[0])))
     sounds.extend([[tick,*fx] for fx in nativeFx]);frames+=1
    if eventId==12:assert accepted==[0,0]
    results.append({'type':type,'flip':flip,'event':eventId,'accepted':accepted,'sounds':sounds})
 # Native ABI exposes only mask bits; original packed helper must preserve all other header bits.
 generator=random.Random(38);cases=0
 for payload in [0,1,63,255,256,-1,-256,0x7fffffff,-0x80000000]+[generator.randrange(-2**31,2**31) for _ in range(1015)]:
  header=generator.randrange(65536);u.mem_write(o.actor+6,struct.pack('<H',header));o.message(10,payload,0);assert msg(s,8,10,payload,0,fetch,None)==0
  packed=struct.unpack('<H',u.mem_read(o.actor+6,2))[0];assert packed==(header&0xc03f)|((payload&255)<<6);assert s[25]==(packed>>6)&255;cases+=1
 report={'original_actor_frames':frames,'mask_cases':cases,'scenarios':results,'grab12_refused_by_both_types':True,'mismatches':0,'scope':'Original generic update and reactions at source coordinates, both facings. Allocator/camera/audio-delivery fixtures. No claim of pickup12 or complete world dynamic scheduling.'};(ROOT/'docs/environment_script_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'frames':frames,'mask_cases':cases,'mismatches':0})
if __name__=='__main__':main()
