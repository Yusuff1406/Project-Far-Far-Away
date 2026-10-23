#!/usr/bin/env python3
"""Compare original event32 sound, manager counter and update packet."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 o=Original(Rom(sys.argv[1]));o.ctor(0x08052694);u=o.u;actual=[];expected=[];manager=0x2002e9c
 def hook(uc,addr,size,data):
  if addr==0x080163ac:expected.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)])
  elif addr==0x0800bec0:expected.append([1,uc.reg_read(UC_ARM_REG_R0),0])
  else:return
  uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @SINK
 def sink(kind,address,scale,ctx):actual.append([kind,address,scale]);return 0
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));fn=lib.s2_shrek_coin_receive;fn.argtypes=[IP,IP,IP,SINK,ctypes.c_void_p];rng=random.Random(202633);accepted=0
 for case in range(4000):
  state=rng.randrange(18);value=rng.choice([-2147483648,2147483647,0,32,33,rng.randint(-100000,100000)]);extra=(ctypes.c_int32*8)(state);event=(ctypes.c_int32*3)(rng.randint(-1000,1000),32,rng.randint(-1000,1000));counter=ctypes.c_int32(value)
  u.mem_write(o.actor+0x1d8,struct.pack('<i',state));u.mem_write(manager+0x1c,struct.pack('<i',value));u.mem_write(0x02007200,struct.pack('<3i',*event));actual.clear();expected.clear();o.call(0x0800e3a0,o.actor,0x02007200)
  result=fn(extra,event,ctypes.byref(counter),sink,None);assert result==u.reg_read(UC_ARM_REG_R0)&255,(case,result);assert counter.value==struct.unpack('<i',u.mem_read(manager+0x1c,4))[0],case;assert actual==expected,(case,actual,expected);accepted+=result==1
 assert struct.unpack('<3i',u.mem_read(0x08024cdc,12))==(2,3,0)
 report={'original_event32_cases':4000,'accepted':accepted,'mismatches':0,'scope':'Original E3A0 event32 executes 9358/9288; low-level sound and global delivery are fixtures. Wrapped pickup counter and both descriptor addresses/ordering compared. HUD/full global manager are separate.'};(ROOT/'docs/coin_pickup_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
