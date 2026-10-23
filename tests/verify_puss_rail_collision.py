#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 def execute(addr,regs):
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,v&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=300000)
  if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original function did not return')
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));resolve=lib.s2_resolve_puss_static_file
 resolve.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int32)];resolve.argtypes.extend([ctypes.POINTER(ctypes.c_int32),ctypes.c_int]);resolve.restype=ctypes.c_int
 apply=lib.s2_apply_axis_triple;apply.argtypes=[ctypes.POINTER(ctypes.c_int32)]*2+[ctypes.c_int]*2;apply.restype=ctypes.c_int
 rng=random.Random(202610);cases=0;contacts_observed=0
 for n in range(30):
  d=scene_collision(r,n);path=str((root/f'collision/scene_{n:02d}/scene.s2cl').resolve()).encode();bounds=d['nodes'][0]['bounds'];u.mem_write(0x02000800,struct.pack('<I',ROM_BASE+d['root_offset']));u.mem_write(0x02003254,struct.pack('<I',0x02000800));tests=[]
  for s in d['segments']:
   x1,y1,x2,y2=s['endpoints'];kind=s['type'];mid=((x1+x2)*128,(y1+y2)*128);width=16;height=50
   if kind in [3,4,6]:old=(mid[0],mid[1]-height*128-1024);new=(mid[0],mid[1]-height*128+1024)
   elif kind==5:old=(mid[0],mid[1]+height*128+1024);new=(mid[0],mid[1]+height*128-1024)
   elif kind==1:old=(mid[0]+width*128+1024,mid[1]);new=(mid[0]+width*128-1024,mid[1])
   elif kind==2:old=(mid[0]-width*128-1024,mid[1]);new=(mid[0]-width*128+1024,mid[1])
   else:old=(mid[0],mid[1]-1024);new=(mid[0]+512,mid[1]+1024)
   tests.append((old,new,width,height,width,height,0))
  for _ in range(300):
   x=rng.randint(bounds[0],bounds[2])*256+rng.randint(0,255);y=rng.randint(bounds[1],bounds[3])*256+rng.randint(0,255);width=rng.choice([8,16,24,32]);height=rng.choice([16,32,50,64]);tests.append(((x,y),(x+rng.randint(-2560,2560),y+rng.randint(-2560,2560)),width,height,rng.choice([width,16]),rng.choice([height,50]),rng.choice([0,0,1])))
  for old,new,width,height,ow,oh,ground in tests:
   actor=0x02004000;u.mem_write(actor,bytes(0x400));u.mem_write(actor,struct.pack('<I',0x02001c8c));u.mem_write(actor+0x1fc,struct.pack('<i',4));u.mem_write(actor+0x174,bytes([width,height]));u.mem_write(actor+0x178,struct.pack('<2i',*new))
   oldrect=(old[0]-ow*128,old[1]-oh*128,ow*256,oh*256);u.mem_write(actor+0x190,struct.pack('<4i',*oldrect));u.mem_write(actor+0xa8,struct.pack('<4i',ground,0,0,0));execute(0x08004098,(actor,))
   expected_pos=struct.unpack('<2i',u.mem_read(actor+0x178,8));expected_counts=struct.unpack('<4i',u.mem_read(actor+0xa8,16));point=(ctypes.c_int32*2)(*new);counts=(ctypes.c_int32*4)(ground,0,0,0);code=resolve(path,(ctypes.c_int32*4)(*oldrect),point,width,height,counts,(ctypes.c_int32*3)(),1)
   if code or tuple(point)!=expected_pos or tuple(counts)!=expected_counts:raise AssertionError(('resolve',n,old,new,width,height,ow,oh,ground,code,tuple(point),expected_pos,tuple(counts),expected_counts))
   contacts_observed+=sum(expected_counts)-ground;cases+=1
 result=dict(static_resolution_cases=cases,accepted_contacts_observed=contacts_observed,scene_count=30,mismatches=0,scope='Actual04098 with Puss100DC floor override across all30 maps, including body-size changes and preexisting ground contacts. Type6 center-only projection before4/3; no full-route/device claim.')
 (root/'docs/puss_rail_collision_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
