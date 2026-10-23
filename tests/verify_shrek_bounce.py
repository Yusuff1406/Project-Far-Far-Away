#!/usr/bin/env python3
"""Original E3A0 event28, with input and ceiling answer fixtures."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR

def main():
 o=Original(Rom(sys.argv[1]));o.ctor(0x08052694);u=o.u;held=clear=0
 def hook(uc,addr,size,data):
  if addr in (0x0800df9c,0x0800729c):
   uc.reg_write(UC_ARM_REG_R0,clear if addr==0x0800df9c else held);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));fn=lib.s2_shrek_bounce_receive;fn.argtypes=[IP]*5+[ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,ctypes.c_int,FC,ctypes.c_void_p]
 rng=random.Random(202632);accepted=0
 for case in range(6000):
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)()
  s[2:14]=[rng.randint(-2000,2000) for _ in range(12)];s[11]=rng.choice([-1,0,1,256,1792]);s[62]=rng.randrange(3);s[20:24]=[0,0,0,rng.randrange(101)];s[47]=0x0834f25c;s[41:44]=[1,7,0]
  e[0]=rng.choice([20,rng.randrange(17)]);e[1]=rng.randrange(8);held=rng.choice([0,1,16,32]);e[2]=held;clear=rng.randrange(2);tick=rng.randrange(10000);strength=rng.choice([1430,1,0,-1,2147483647,-2147483648]);event=(ctypes.c_int32*3)(strength,28,rng.randint(-1000,1000))
  scene=case>=3000;u.mem_write(o.actor,struct.pack('<I',0x02001e6c if scene else 0x020017cc));u.mem_write(o.actor+0x264,bytes(4));o.seed(s)
  for off,value in [(0x16c,s[62]),(0x1d8,e[0]),(0x258,e[1]),(0x1e8,0x0804b73c),(0x260,0),(0x25c,0)]:u.mem_write(o.actor+off,struct.pack('<i',value))
  for addr in (0x0200324c,0x020033e0):u.mem_write(addr,struct.pack('<i',tick))
  u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08010c08 if scene else 0x0800e3a0,o.actor,0x02007200);expected=u.reg_read(UC_ARM_REG_R0)&255
  selected=lib.s2_shrek_scene_bounce_receive if scene else fn;selected.argtypes=fn.argtypes;result=selected(s,e,status,book,event,tick,tick,0x0804b73c,clear,fetch,None);assert result==expected,(case,result,expected);accepted+=result==1
  assert list(s[2:14])==list(struct.unpack('<12i',u.mem_read(o.component,48))),case
  assert e[0]==struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],case
  assert s[47]==struct.unpack('<i',u.mem_read(o.sprite+8,4))[0],case
  assert list(book[:2])==[struct.unpack('<i',u.mem_read(o.actor+x,4))[0] for x in (0x260,0x25c)],case
  assert list(s[20:24])==[u.mem_read(o.sprite,1)[0],struct.unpack('<i',u.mem_read(o.sprite+4,4))[0],*struct.unpack('<2i',u.mem_read(o.sprite+12,8))],case
 report={'original_event28_cases':6000,'type3_override_cases':3000,'accepted':accepted,'mismatches':0,'scope':'Original E3A0/10C08/F0F8 and motion/animation helpers. DF9C ceiling answer and held input are fixtures, not a full original world.'}
 (ROOT/'docs/shrek_bounce_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
