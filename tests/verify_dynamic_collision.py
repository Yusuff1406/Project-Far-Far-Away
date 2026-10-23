#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc]);actor=0x02004000
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);fn=lib.s2_resolve_dynamic;fn.argtypes=[ip,ip,ctypes.c_int,ctypes.c_int,ip,ctypes.c_int,ip,ip];fn.restype=ctypes.c_int;probe=lib.s2_actor_probe_file;probe.argtypes=[ctypes.c_char_p,ctypes.c_int]+[ctypes.c_int32]*4+[ip,ctypes.c_int];probe.restype=ctypes.c_int
 rng=random.Random(202607);cases=0;acceptedCases=0
 def setup(lines):
  u.mem_write(actor,bytes(0x400));u.mem_write(actor+0x148,struct.pack('<i',len(lines)))
  for i,s in enumerate(lines):
   p=0x02008000+i*64;aux=p+24 if s[5] else 0;u.mem_write(p,struct.pack('<5iI',*s[:5],aux));u.mem_write(actor+0xb8+i*8,struct.pack('<2I',p,0x0200c000+i*0x400))
   if aux:u.mem_write(aux,struct.pack('<2iB',*s[6:9]))
 def run(addr,args):
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000
 for _ in range(14000):
  w,h=rng.choice([8,16,24,32]),rng.choice([16,32,50,64]);cx,cy=rng.randint(-64,640)*256,rng.randint(-64,400)*256;old=[cx-w*128,cy-h*128,w*256,h*256];new=[cx+rng.randint(-2048,2048),cy+rng.randint(-2048,2048)];lines=[]
  for i in range(rng.choice([0,1,1,2,4,8,16])):
   kind=rng.choice([1,2,3,5]);x,y=(cx>>8)+rng.randint(-32,32),(cy>>8)+rng.randint(-60,60);width,height=rng.randint(1,64),rng.randint(1,100)
   if kind in [1,2]:s=[x,y,x,y+height,kind,0,0,0,0]
   else:s=[x,y,x+width,y+rng.choice([0,0,0,-8,8]),kind,int(kind==3),rng.randint(-512,512) if kind==3 else 0,rng.randint(-256,256) if kind==3 else 0,rng.randint(0,1) if kind==3 else 0]
   lines.append(s)
  setup(lines);counts=[rng.randint(0,1) for _ in range(4)];flags=[rng.randint(0,1) for _ in lines];u.mem_write(actor+0x174,bytes([w,h]));u.mem_write(actor+0x178,struct.pack('<2i',*new));u.mem_write(actor+0x190,struct.pack('<4i',*old));u.mem_write(actor+0x14c,struct.pack('<4i',*counts));u.mem_write(actor+0x138,bytes(flags));run(0x08004768,[actor]);expectedPos=list(struct.unpack('<2i',u.mem_read(actor+0x178,8)));expectedCounts=list(struct.unpack('<4i',u.mem_read(actor+0x14c,16)));expectedFlags=list(u.mem_read(actor+0x138,len(lines)));flat=[v for s in lines for v in s];p=(ctypes.c_int32*2)(*new);co=(ctypes.c_int32*4)(*counts);af=(ctypes.c_int32*max(1,len(lines)))(*flags);code=fn((ctypes.c_int32*4)(*old),p,w,h,(ctypes.c_int32*len(flat))(*flat),len(lines),co,af)
  assert code==0 and list(p)==expectedPos and list(co)==expectedCounts and list(af[:len(lines)])==expectedFlags,(old,new,lines,code,list(p),expectedPos,list(co),expectedCounts)
  acceptedCases+=sum(expectedCounts)>sum(counts);cases+=1
 probes=0
 for scene in range(30):
  d=scene_collision(r,scene);u.mem_write(0x02000800,struct.pack('<I',ROM_BASE+d['root_offset']));u.mem_write(0x02003254,struct.pack('<I',0x02000800));path=str(ROOT/f'collision/scene_{scene:02d}/scene.s2cl').encode();bounds=d['nodes'][0]['bounds']
  for _ in range(100):
   x=rng.randint(bounds[0],bounds[2])*256;y=rng.randint(bounds[1],bounds[3])*256;ww,hh=rng.choice([1,16,32])*256,rng.choice([1,16,50])*256;kind=rng.choice([1,2,3,4,5,6]);lines=[[x//256,y//256,x//256+16,y//256+16,kind,int(kind==3),0,0,0]] if rng.randint(0,1) else [];setup(lines);stack=0x0203f000;u.mem_write(stack,struct.pack('<2i',hh,kind));run(0x08004be0,[actor,x,y,ww]);expected=u.reg_read(UC_ARM_REG_R0);flat=[v for s in lines for v in s];actual=probe(path,kind,x,y,ww,hh,(ctypes.c_int32*len(flat))(*flat),len(lines));assert actual==expected,(scene,kind,lines,actual,expected);probes+=1
 result={'dynamic_resolution_cases':cases,'cases_with_new_contact':acceptedCases,'combined_probe_cases':probes,'mismatches':0,'original_resolution':'0x08004768','original_probe':'0x08004BE0','scope':'Original dynamic contact resolution and acceptance/projection helpers run unmodified; supplied actor surface list is a fixture. Combined probes cover static trees of all 30 scenes. Dynamic world discovery and object events not reproduced.'}
 (ROOT/'docs/dynamic_collision_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
