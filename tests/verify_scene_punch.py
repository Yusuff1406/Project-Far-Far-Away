#!/usr/bin/env python3
"""Actual type3 constructor111CC and ground-attack overrideF25C versus native."""
import ctypes,json,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
I=ctypes.c_int32
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));l.s2_generic_runtime_init.argtypes=[IP,I,ctypes.c_uint32,I,FC,ctypes.c_void_p,IP];l.s2_shrek_scene_attack_enter.argtypes=[IP,IP,IP,I,ctypes.c_uint32,FC,ctypes.c_void_p]
 def hook(uc,addr,size,ctx):
  if addr in [0x0800bec0,0x0800bf04]:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:data=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,data)):out[i]=v
  return 1
 checked=0;events=[];animations=set()
 for flip in [0,1]:
  o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x020031b0,bytes(32));u.mem_write(0x020031b8,struct.pack('<I',0x02006000));u.mem_write(0x02006000,bytes(32));u.mem_write(0x02006015,bytes([7]));u.mem_write(0x0203f000,bytes([flip])+bytes(15));o.call(0x080111cc,o.actor,0x0804b73c,120*256,350*256)
  event=list(struct.unpack('<3i',u.mem_read(o.actor+0x210,12)));assert event==[3,1,0];events.append(event)
  o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
  for counter in [*range(32),2147483647,-2147483648,-1,-2]:
   for tick in [0,12345,2000000000]:
    s=(I*80)();extra=(I*8)();book=(I*8)();assert l.s2_generic_runtime_init((I*2)(120*256,350*256),flip,0x0834f25c,tick,fetch,None,s)==0;s[19]=counter;s[2:14]=[384,51,435,-200,51,-435,-1011,49,1792,200,49,1792];o.seed(s)
    u.mem_write(o.actor+0x1e0,struct.pack('<i',counter));u.mem_write(o.actor+0x260,bytes(4));u.mem_write(o.actor+0x258,bytes(4));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick))
    o.call(0x0800f25c,o.actor);assert l.s2_shrek_scene_attack_enter(s,extra,book,tick,0x0804b73c,fetch,None)==0
    expected=[struct.unpack('<i',u.mem_read(o.actor+0x1e0,4))[0],list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),list(struct.unpack('<12i',u.mem_read(o.component,48))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],struct.unpack('<I',u.mem_read(o.sprite+8,4))[0],[u.mem_read(o.sprite,1)[0],*struct.unpack('<i',u.mem_read(o.sprite+4,4)),*struct.unpack('<2i',u.mem_read(o.sprite+12,8))],struct.unpack('<i',u.mem_read(o.actor+0x260,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x25c,4))[0]]
    actual=[s[19],list(s[41:44]),list(s[2:14]),extra[0],s[47],list(s[20:24]),book[0],book[1]];assert actual==expected,(flip,counter,tick,actual,expected);animations.add(s[47]);checked+=1
 assert animations=={0x0834f304,0x0834f31c}
 report=dict(actual_constructor_events=events,original_attack_entry_cases=checked,alternating_animations=sorted(animations),outgoing_normal_punch=[3,1,0],previous_base_attack=[1,13,0],mismatches=0,scope='Full source111CC constructor, allocator/registration/broadcast owner fixtures; actual F25C action, motion/animation helpers. Native scene helper compared on both facings, counter wrap and tick values. No Android execution.');(ROOT/'docs/scene_punch_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
