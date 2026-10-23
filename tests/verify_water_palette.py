#!/usr/bin/env python3
"""Original E168 water entry and 18848/18870 palette expiry versus native."""
import ctypes,json,struct,sys
from verify_generic_runtime import *
I=ctypes.c_int32
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;context=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(context,bytes(32));u.mem_write(context+8,struct.pack('<I',0x083283f8));u.mem_write(0x203f000,bytes(16))
 def hook(uc,a,size,data):
  ret=0 if a in[0x800bec0,0x800bf04,0x800fadc] else 0x2007400 if a==0x800fb2c else None
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.call(0x80111cc,o.actor,0x804b714,35*256,350*256);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=l.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];water=l.s2_shrek_water_enter;water.argtypes=[IP,IP,IP,I,FC,ctypes.c_void_p]
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
  return 1
 def clock(t):
  for a in [0x200324c,0x20033e0]:u.mem_write(a,struct.pack('<i',t))
 cases=0
 for state in [0,2,4,6,7,8,13,14,19,20]:
  for tick in [1,100,999]:
   s=(I*80)();e=(I*8)();book=(I*8)();assert init((I*2)(35*256,350*256),0,0x834f25c,tick,fetch,None,s)==0;e[0]=state;s[41:44]=[1,7,0];o.seed(s)
   for off,v in [(0x1d8,state),(0x260,0),(0x25c,0),(0x258,0)]:u.mem_write(o.actor+off,struct.pack('<i',v))
   clock(tick);u.mem_write(0x2007300,struct.pack('<3i',1,40,0));o.call(0x8010c08,o.actor,0x2007300);assert u.reg_read(UC_ARM_REG_R0)==1
   assert water(s,e,book,tick,fetch,None)==0
   actual=[list(s[2:14]),s[20],[s[21],s[47],s[22],s[23]],e[0],book[0],book[1]]
   wanted=[list(struct.unpack('<12i',u.mem_read(o.component,48))),u.mem_read(o.sprite,1)[0],list(struct.unpack('<4i',u.mem_read(o.sprite+4,16))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x260,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x25c,4))[0]]
   assert actual==wanted,(state,tick,actual,wanted);cases+=1
 clock(100);o.call(0x8018848,o.actor,4,0x834f43c);palettes=[]
 for tick in range(100,108):
  clock(tick);o.call(0x8018870,o.actor);palette=struct.unpack('<I',u.mem_read(o.sprite+0x18,4))[0];assert palette==(0x8499408 if tick<104 else 0),(tick,hex(palette));palettes.append(palette)
 report={'original_water_entry_cases':cases,'original_palette_ticks':palettes,'mismatches':0,'scope':'Actual type3 incoming40/E168 motion17+idle physics; source palette deadline4 animation ticks. Whole game-over owner and Android excluded.'};(ROOT/'docs/water_palette_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
