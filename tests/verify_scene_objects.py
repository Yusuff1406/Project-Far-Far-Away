#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);up=ctypes.POINTER(ctypes.c_uint32)
 plan=lib.s2_scene_spawn_plan_file;plan.argtypes=[ctypes.c_char_p,up,ctypes.c_size_t,ip,ctypes.c_size_t];plan.restype=ctypes.c_int;count=lib.s2_scene_type_count_file;count.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.c_int];count.restype=ctypes.c_int;category=lib.s2_object_category;category.argtypes=[ctypes.c_int];category.restype=ctypes.c_int
 fake=0x02008000;vt=0x02009000;maskptr=0x0200a000;maskglobal=struct.unpack_from('<I',r.data,0x9cbc)[0];u.mem_write(maskglobal,struct.pack('<I',maskptr));u.mem_write(fake,struct.pack('<I',vt));u.mem_write(vt+0x40,struct.pack('<2I',0,0x03001101));requests=[];pending=None;registration=[]
 def hook(uc,address,size,data):
  nonlocal pending
  ret=None
  if address==0x080059d8:
   typ=uc.reg_read(UC_ARM_REG_R0);xy=list(struct.unpack('<2i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8)));param=uc.reg_read(UC_ARM_REG_R2);flags=uc.mem_read(param,1)[0];tag=struct.unpack('<i',uc.mem_read(param+8,4))[0];secondary=struct.unpack('<h',uc.mem_read(param+12,2))[0];pending=[None,typ,*xy,param,flags,tag,secondary];ret=fake
  elif address==0x03001100:pending[0]=uc.reg_read(UC_ARM_REG_R1);requests.append(pending);ret=0
  elif address==0x08007ab0:registration.append(uc.reg_read(UC_ARM_REG_R1));ret=0
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def run(addr,r0,r1=0):
  u.reg_write(UC_ARM_REG_R0,r0&0xffffffff);u.reg_write(UC_ARM_REG_R1,r1&0xffffffff);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=500000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000;return ctypes.c_int32(u.reg_read(UC_ARM_REG_R0)).value
 categories=0
 for typ in list(range(158))+[-32768,-1,158,999,65535]:assert category(typ)==run(0x080072c0,typ);categories+=1
 rng=random.Random(202608);plans=0;requestCases=0;counts=0
 for scene in range(30):
  desc=struct.unpack_from('<8I',r.data,0x28d94+scene*32)[6];n=struct.unpack_from('<H',r.data,desc-ROM_BASE)[0];path=str(ROOT/f'objects/scene_{scene:02d}/scene.s2ob').encode();manager=0x02004000;u.mem_write(manager+0x18,struct.pack('<I',desc))
  for pattern in range(40):
   words=(n+32)//32;bits=[0 if pattern==0 else 0xffffffff if pattern==1 else rng.getrandbits(32) for _ in range(words)];u.mem_write(maskptr,struct.pack('<'+'I'*words,*bits));requests=[];registration=[];run(0x08007084,desc);out=(ctypes.c_int32*(n*8))();result=plan(path,(ctypes.c_uint32*words)(*bits),words,out,n);actual=[list(out[i*8:i*8+8]) for i in range(result)];assert actual==requests and registration==[x[1] for x in actual],(scene,pattern,actual[:3],requests[:3]);plans+=1;requestCases+=len(requests)
  for typ in sorted(set([0,89,999]+[x['type'] for x in json.loads((ROOT/f'objects/scene_{scene:02d}/objects.json').read_text())['objects']])):
   assert count(path,typ,0)==run(0x08006f0c,manager,typ);counts+=1
  for group in range(12):assert count(path,group,1)==run(0x08007014,manager,group);counts+=1
 result={'category_cases':categories,'spawn_plan_cases':plans,'spawn_requests_compared':requestCases,'type_category_count_cases':counts,'mismatches':0,'scope':'Original 0x08007084 traversal, parameter indirection and persisted-bit filter execute unmodified. Factory constructor and actor ID/registration callbacks mocked; requests compared exactly. Original category and count methods execute unmodified. No actor constructor or behavior implementation.'};(ROOT/'docs/scene_objects_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
