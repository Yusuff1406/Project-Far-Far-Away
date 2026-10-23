#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom
from extract_collision import scene_collision
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x08000000,len(r.data));u.mem_write(0x08000000,r.data);u.mem_map(0x02000000,0x40000);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 def execute(addr,regs):
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,v&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=20000)
  if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original code failed to return')
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));motion=lib.s2_motion_step;motion.argtypes=[ctypes.POINTER(ctypes.c_int32)]*2;motion.restype=None
 project=lib.s2_project_segment_q8;project.argtypes=[ctypes.POINTER(ctypes.c_int32)]*2+[ctypes.c_int,ctypes.POINTER(ctypes.c_int32)];project.restype=ctypes.c_int
 rng=random.Random(202603);mcases=0;pcases=0
 for k in range(2000):
  axes=[]
  for _ in range(2):
   cur=rng.randint(-2000,2000);step=rng.randint(0,100);target=rng.randint(-2000,2000);axes.extend([cur,step,target,cur,step,target])
  parameters=(ctypes.c_int32*12)(*axes);position=(ctypes.c_int32*2)(rng.randint(-100000,100000),rng.randint(-100000,100000))
  for tick in range(8):
   u.mem_write(0x02001000,struct.pack('<12i',*parameters));u.mem_write(0x02001200,struct.pack('<2i',*position));execute(0x0800b96c,(0x02001000,0x02001200))
   expected_p=struct.unpack('<12i',u.mem_read(0x02001000,48));expected_xy=struct.unpack('<2i',u.mem_read(0x02001200,8));motion(parameters,position)
   if tuple(parameters)!=expected_p or tuple(position)!=expected_xy:raise AssertionError(('motion',k,tick))
   mcases+=1
 for n in range(30):
  d=scene_collision(r,n)
  for seg in d['segments']:
   line=seg['endpoints'];points=[(line[0]*256+64,line[1]*256+128),(line[2]*256-64,line[3]*256-128),((line[0]+line[2])*128,(line[1]+line[3])*128)]
   for point in points:
    for mode in [0,1]:
     u.mem_write(0x02001100,struct.pack('<4i',*line)+bytes(8));u.mem_write(0x02001300,struct.pack('<2I',0x02001100,0));u.mem_write(0x02001200,struct.pack('<2i',*point));execute(0x08017f9c,(0x02001000,0x02001300,0x02001200,mode))
     expected=struct.unpack('<2i',u.mem_read(0x02001000,8));out=(ctypes.c_int32*2)();code=project((ctypes.c_int32*4)(*line),(ctypes.c_int32*2)(*point),mode,out)
     if code or tuple(out)!=expected:raise AssertionError(('projection',n,line,point,mode,code,tuple(out),expected))
     pcases+=1
 result={'original_motion_update':'0x0800B96C','motion_update_cases':mcases,'original_surface_projection':'0x08017F9C','surface_projection_cases':pcases,'mismatches':0,'scope':'Original free-motion integrator and line projection; full controller and collision response order are not executed'}
 (root/'docs/motion_projection_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
