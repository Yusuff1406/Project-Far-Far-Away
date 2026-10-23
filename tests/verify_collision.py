#!/usr/bin/env python3
"""Run original Thumb static-tree queries and compare exact ordered hits."""
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom,unpack,ROM_BASE
from extract_collision import scene_collision
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 def execute(addr,regs,stack=()):
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,v&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001)
  if stack:u.mem_write(0x0203f000,struct.pack('<'+'i'*len(stack),*stack))
  u.emu_start(addr|1,0x03001000,count=300000)
  if u.reg_read(UC_ARM_REG_PC)!=0x03001000 or u.reg_read(UC_ARM_REG_SP)!=0x0203f000:raise AssertionError(('Original routine did not return',hex(u.reg_read(UC_ARM_REG_PC))))
  return u.reg_read(UC_ARM_REG_R0)
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));clip=lib.s2_segment_rect;clip.argtypes=[ctypes.POINTER(ctypes.c_int32)]*2;clip.restype=ctypes.c_int
 query=lib.s2_collision_query_file;query.argtypes=[ctypes.c_char_p,ctypes.c_int]+[ctypes.c_int32]*4+[ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t];query.restype=ctypes.c_int
 probe=lib.s2_static_probe_q8;probe.argtypes=[ctypes.c_char_p,ctypes.c_int]+[ctypes.c_int32]*4;probe.restype=ctypes.c_int
 rng=random.Random(20261013);clipcases=0;querycases=0;probecases=0;offsets=[]
 for n in range(30):
  d=scene_collision(r,n);path=str((root/f'collision/scene_{n:02d}/scene.s2cl').resolve()).encode();bounds=d['nodes'][0]['bounds'];rp=ROM_BASE+d['root_offset']
  u.mem_write(0x02000800,struct.pack('<I',rp));u.mem_write(0x02003254,struct.pack('<I',0x02000800))
  def compare_query(t,box):
   nonlocal querycases
   u.mem_write(0x02001000,struct.pack('<4i',*box));count=execute(0x08017dbc,(t,0x02001000,0x02008000,0));expected=[struct.unpack('<I',u.mem_read(0x02008000+k*8,4))[0]-ROM_BASE for k in range(count)]
   out=(ctypes.c_uint32*max(1,d['segment_count']))();got=query(path,t,*box,out,len(out))
   if got!=count or list(out)[:got]!=expected:raise AssertionError(('query',n,t,box,got,count,list(out)[:got],expected))
   querycases+=1
  for t in range(7):compare_query(t,bounds)
  for s in d['segments']:
   line=s['endpoints']
   for box in [[line[0]-1,line[1]-1,line[0]+1,line[1]+1],[line[2]-1,line[3]-1,line[2]+1,line[3]+1],[min(line[0],line[2]),min(line[1],line[3]),max(line[0],line[2]),max(line[1],line[3])]]:
    u.mem_write(0x02001000,struct.pack('<4i',*box));u.mem_write(0x02001100,struct.pack('<4i',*line)+bytes(8));expected=execute(0x08017a30,(0x02001000,0x02001100));got=clip((ctypes.c_int32*4)(*line),(ctypes.c_int32*4)(*box))
    if got!=expected:raise AssertionError(('clip',n,line,box,got,expected))
    clipcases+=1
  for k in range(120):
   x=rng.randint(bounds[0]-80,bounds[2]+80);y=rng.randint(bounds[1]-80,bounds[3]+80);w=rng.randint(0,300);h=rng.randint(0,100);t=rng.randint(1,6);compare_query(t,[x,y,x+w,y+h])
   # Original actor wrapper, with dynamic-instance collision list empty.
   u.mem_write(0x02002000,bytes(0x400));xq=x*256+rng.randint(0,255);yq=y*256+rng.randint(0,255);wq=w*256;hq=h*256
   expected=execute(0x08004be0,(0x02002000,xq,yq,wq),(hq,t));got=probe(path,t,xq,yq,wq,hq)
   if got!=expected:raise AssertionError(('probe',n,t,xq,yq,wq,hq,got,expected))
   probecases+=1
 result={'original_segment_rect':'0x08017A30','segment_rect_cases':clipcases,'original_tree_query':'0x08017DBC','ordered_tree_query_cases':querycases,'original_actor_probe':'0x08004BE0','static_actor_probe_cases':probecases,'scene_count':30,'mismatches':0,'scope':'Original ROM tree and static geometry; actor dynamic collision list empty; no full gameplay execution'}
 (root/'docs/collision_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
