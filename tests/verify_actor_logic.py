#!/usr/bin/env python3
"""Compare translated actor primitives with original Thumb instructions."""
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom
from extract_sprites import bank,roots
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);rom=Rom(a.rom)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x08000000,len(rom.data));u.mem_write(0x08000000,rom.data);u.mem_map(0x02000000,0x40000);u.mem_map(0x03000000,0x2000)
 def execute(addr,r0=0x02001000,r1=0,r2=0):
  u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_R1,r1);u.reg_write(UC_ARM_REG_R2,r2);u.reg_write(UC_ARM_REG_SP,0x03001f00);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=1000)
  if u.reg_read(UC_ARM_REG_SP)!=0x03001f00:raise AssertionError('Original routine did not return')
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));fn=lib.s2_animation_step;fn.argtypes=[ctypes.c_int]*3+[ctypes.c_int32,ctypes.POINTER(ctypes.c_int32)];fn.restype=None
 approach=lib.s2_approach_step;approach.argtypes=[ctypes.c_int32]*3;approach.restype=ctypes.c_int32
 pointer_cases=0;timing_cases=0
 for ro in roots(rom):
  d=bank(rom,ro)
  for anim in d['animations']:
   ptr=0x08000000+anim['record_offset']
   for i,k in enumerate(anim['frame_indices']):
    execute(0x08016a64,r1=ptr,r2=i);expected=0x08000000+d['frames'][k]['record_offset']
    if u.reg_read(UC_ARM_REG_R0)!=expected:raise AssertionError(('frame pointer',ro,anim['index'],i))
    pointer_cases+=1
   for direction in [0,1,2,-1]:
    state=(ctypes.c_int32*4)(0,direction,0 if direction!=1 else anim['sequence_count']-1,anim['ticks_per_frame'])
    ticks=list(range(0,anim['ticks_per_frame']*(anim['sequence_count']+3)))+[10000,10001,20000]
    for now in ticks:
     u.mem_write(0x02001000,struct.pack('<5i',state[0],state[1],ptr,state[2],state[3]));u.mem_write(0x0200324c,struct.pack('<i',now))
     execute(0x0801682c);raw=bytes(u.mem_read(0x02001000,20));words=struct.unpack('<5i',raw);expected=(raw[0],words[1],words[3],words[4])
     fn(anim['rate_byte'],anim['sequence_count'],anim['flags'],now,state)
     if tuple(state)!=expected:raise AssertionError(('timing',ro,anim['index'],now,tuple(state),expected))
     timing_cases+=1
 rng=random.Random(2026);approach_cases=0
 cases=[(c,s,t) for c in [-2147483648,-1000,-1,0,1,1000,2147483647] for s in [0,1,168,600] for t in [-1000,0,1000]]
 cases.extend((rng.randint(-200000,200000),rng.randint(0,10000),rng.randint(-200000,200000)) for _ in range(5000))
 for current,step,target in cases:
  u.mem_write(0x02001000,struct.pack('<6i',0,0,0,current,step,target));execute(0x080002dc);expected=struct.unpack('<i',u.mem_read(0x0200100c,4))[0];got=approach(current,step,target)
  if got!=expected:raise AssertionError(('approach',current,step,target,got,expected))
  approach_cases+=1
 result={'original_thumb_frame_helper':'0x08016A64','sequence_positions_compared':pointer_cases,'original_thumb_animation_step':'0x0801682C','animation_steps_compared':timing_cases,'original_thumb_approach_step':'0x080002DC','approach_steps_compared':approach_cases,'mismatches':0,'scope':'Original code for these functions only; full player physics and collisions not executed'}
 (root/'docs/actor_logic_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
