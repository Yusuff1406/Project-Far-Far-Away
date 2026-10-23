#!/usr/bin/env python3
"""Original type3 incoming event30, B gate and idle entry versus native."""
import ctypes,json,struct,sys
from verify_generic_runtime import *
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;held=0
 context=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(context,bytes(32));u.mem_write(context+8,struct.pack('<I',0x2006000));u.mem_write(0x2006015,bytes([4]));u.mem_write(0x203f000,bytes(16))
 def hook(uc,a,size,data):
  ret=None
  if a in[0x800bec0,0x800bf04]:ret=0
  elif a==0x800fb2c:ret=0x2007400
  elif a==0x800fadc:ret=held
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.call(0x80111cc,o.actor,0x804b714,35*256,350*256);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=l.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];talk=l.s2_shrek_talk_receive;talk.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,FC,ctypes.c_void_p]
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
  return 1
 cases=accepted=0
 for state in range(22):
  for pressed in[0,1,2,3,16,32,34]:
   for held in[0,16,32]:
    s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();assert init((ctypes.c_int32*2)(35*256,350*256),0,0x834f25c,100,fetch,None,s)==0;e[0]=state;e[2]=held;s[41:44]=[1,7,0];o.seed(s)
    for off,value in[(0x1d8,state),(0x1ec,held),(0x260,0),(0x25c,0),(0x1dc,0),(0x204,0),(0x258,0),(0x1fc,3)]:u.mem_write(o.actor+off,struct.pack('<i',value))
    u.mem_write(o.actor+0x20c,bytes([0]));u.mem_write(o.actor+0x228,struct.pack('<3i',1,7,0));u.mem_write(0x200324c,struct.pack('<i',100));u.mem_write(0x20033e0,struct.pack('<i',100));u.mem_write(0x2007400,bytes([held])+bytes(7)+bytes([pressed])+bytes(7));u.mem_write(0x2007300,struct.pack('<3i',0,30,0));o.call(0x8010c08,o.actor,0x2007300);expected=u.reg_read(UC_ARM_REG_R0);result=talk(s,e,status,book,pressed,100,fetch,None);assert result==expected,(state,pressed,held,result,expected)
    wanted=[list(struct.unpack('<12i',u.mem_read(o.component,48))),u.mem_read(o.sprite,1)[0],list(struct.unpack('<4i',u.mem_read(o.sprite+4,16))),list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x1dc,4))[0]]
    actual=[list(s[2:14]),s[20],[s[21],s[47],s[22],s[23]],list(s[41:44]),e[0],book[2]];assert actual==wanted,(state,pressed,held,actual,wanted);cases+=1;accepted+=result
 report={'original_talk_cases':cases,'accepted':accepted,'mismatches':0,'scope':'Original111CC/10C08/E3A0 event30 and F158 idle action. Input/world/allocator are fixtures; canonical ogre table, no held item and primary animation/motion fields. NPC collision and UI separately tested.'};(ROOT/'docs/shrek_talk_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
