#!/usr/bin/env python3
"""Compare selected constructor effects with whole original generic ctor."""
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);init=lib.s2_generic_actor_init;init.argtypes=[ip,ip]+[ctypes.c_int]*5+[ip];init.restype=ctypes.c_int
 actor=0x02004000;pos=0x02007000;params=0x02007100;heap=0x02010000
 def hook(uc,address,size,data):
  nonlocal heap
  ret=None
  if address in [0x0801bc5c,0x0801bc4c]:
   n=uc.reg_read(UC_ARM_REG_R0);ret=heap;uc.mem_write(heap,bytes(n));heap=(heap+n+3)&~3
  elif address==0x080150d4:ret=0x100
  elif address==0x080007e0:ret=1
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(0x020031e8,struct.pack('<I',0x0200b000));u.mem_write(0x0200b000,bytes(0x40));u.mem_write(0x02003264,struct.pack('<I',0x0200b040));u.mem_write(0x0200b040,bytes(0x40));rng=random.Random(202619);cases=0
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']
 for typ,info in bindings.items():
  definition=info['definition'];bank=json.loads((ROOT/'sprites'/info['bank']/'bank.json').read_text());animation=bank['animations'][info['index']];bounds=animation['bounds']
  for flags in range(4):
   for _ in range(4):
    heap=0x02010000;u.mem_write(actor,bytes(0x1000));xy=[rng.randint(-200000,1000000) for _ in range(2)];tick=rng.randint(0,10000);u.mem_write(pos,struct.pack('<2i',*xy));u.mem_write(params,bytes([flags])+bytes(31));u.mem_write(0x0200324c,struct.pack('<i',tick));u.reg_write(UC_ARM_REG_R0,actor);u.reg_write(UC_ARM_REG_R1,definition);u.reg_write(UC_ARM_REG_R2,pos);u.reg_write(UC_ARM_REG_R3,params);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(0x08013715,0x03001000,count=500000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000
    sprite,component=struct.unpack('<I',u.mem_read(actor+0x1c0,4))[0],struct.unpack('<I',u.mem_read(actor+0x1bc,4))[0];assert struct.unpack('<I',u.mem_read(sprite+8,4))[0]==info['animation'];s=(ctypes.c_int32*40)();assert init((ctypes.c_int32*4)(*bounds),(ctypes.c_int32*2)(*xy),flags,info['index'],animation['rate_byte'],animation['sequence_count'],tick,s)==0
    expect={'position':list(struct.unpack('<2i',u.mem_read(actor+0x178,8))),'motion':list(struct.unpack('<12i',u.mem_read(component,48))),'rect':list(struct.unpack('<4i',u.mem_read(actor+0x190,16))),'previous':list(struct.unpack('<2i',u.mem_read(actor+0x180,8))),'clock':[u.mem_read(sprite,1)[0],struct.unpack('<i',u.mem_read(sprite+4,4))[0],*struct.unpack('<2i',u.mem_read(sprite+12,8))],'flips':list(u.mem_read(sprite+0x28,2)),'size':list(u.mem_read(actor+0x174,2))}
    actual={'position':list(s[:2]),'motion':list(s[2:14]),'rect':list(s[32:36]),'previous':list(s[36:38]),'clock':list(s[20:24]),'flips':[s[18],s[38]],'size':list(s[30:32])};assert actual==expect,(typ,flags,{k:(actual[k],expect[k]) for k in actual if actual[k]!=expect[k]});cases+=1
 result={'constructor_cases':cases,'generic_definitions':len(bindings),'mismatches':0,'original_constructor':'0x08013714 with 0x080180B0 and sprite/motion/VM allocation initialization','scope':'Whole generic constructor executes with allocator/camera fixtures. Compare selected normalized body, position, previous rect/center, motion and animation effects; remaining original fields, resource priorities, script state and event registrations are not claimed ported.'};(ROOT/'docs/generic_actor_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
