#!/usr/bin/env python3
"""Execute original relocated ARM column decoder; compare every source column."""
import argparse, json, struct, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom,unpack
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_ARM,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out');args=ap.parse_args();r=Rom(args.rom)
 u=Uc(UC_ARCH_ARM,UC_MODE_ARM);u.mem_map(0x08000000,len(r.data));u.mem_write(0x08000000,r.data)
 u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 u.mem_map(0x02000000,0x40000);u.mem_map(0x04000000,0x1000)
 def dma(uc,access,address,size,value,user):
  if address!=0x040000dc:return
  src,dst=struct.unpack('<2I',uc.mem_read(0x040000d4,8));count=value&65535
  if value&0x01000000:payload=bytes(uc.mem_read(src,2))*count
  else:payload=bytes(uc.mem_read(src,count*2))
  uc.mem_write(dst,payload)
 u.hook_add(UC_HOOK_MEM_WRITE,dma)
 checked=0;maps=set()
 for n in range(30):
  w=unpack('<8I',r.data,0x28d94+n*32)
  for lp in w[1:5]:
   if not lp:continue
   p=unpack('<6I',r.data,r.offset(lp))[1]
   if p in maps:continue
   maps.add(p);width,height,rows,_=r.column_map(p);o=r.offset(p);base=p+4+width*4
   ptrs=[base+unpack('<I',r.data,o+4+4*x)[0]*2 for x in range(width)]
   u.mem_write(0x02001000,struct.pack('<'+'I'*width,*ptrs))
   u.mem_write(0x02000100,struct.pack('<3I',0x02001000,0,height))
   for x in range(width):
    u.mem_write(0x02002000,bytes(height*2));u.reg_write(UC_ARM_REG_R0,0x02000100);u.reg_write(UC_ARM_REG_R1,x);u.reg_write(UC_ARM_REG_R2,0x02002000)
    u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001000)
    u.emu_start(0x03000000,0x03001000,count=10000)
    got=struct.unpack('<'+'H'*height,u.mem_read(0x02002000,height*2));expected=tuple(rows[y*width+x] for y in range(height))
    if got!=expected:raise AssertionError((n,hex(p),x,got,expected))
    checked+=1
 result={'original_arm_decoder_offset':0x707dd8,'runtime_address':'0x03000000','unique_column_maps':len(maps),'columns_compared':checked,'mismatches':0,'method':'Unicorn original ARM code execution with synchronous DMA3 halfword transfers'}
 print(json.dumps(result,indent=2))
 if args.out:Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
