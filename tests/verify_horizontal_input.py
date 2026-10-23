#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc]);u.mem_write(0x020017cc+0xc4,struct.pack('<I',0x03001101));u.mem_write(0x03001120,struct.pack('<2H',0x6001,0x4770))
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));fn=lib.s2_horizontal_input_file;fn.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_int32),ctypes.c_int,ctypes.c_int]+[ctypes.POINTER(ctypes.c_int32)]*3;fn.restype=ctypes.c_int
 rng=random.Random(202644);cases=0
 for n in range(30):
  d=scene_collision(r,n);bounds=d['nodes'][0]['bounds'];u.mem_write(0x02000800,struct.pack('<I',ROM_BASE+d['root_offset']));u.mem_write(0x02003254,struct.pack('<I',0x02000800));path=str((root/f'collision/scene_{n:02d}/scene.s2cl').resolve()).encode();points=[]
  for s in d['segments']:
   if s['type'] in [1,2]:
    x,y,a,b=s['endpoints'];points.append((x*256+(16*128+256 if s['type']==1 else -16*128-256),(y+b)*128))
  points.extend((rng.randint(bounds[0],bounds[2])*256,rng.randint(bounds[1],bounds[3])*256) for _ in range(100))
  for xy in points:
   for buttons in [0,16,32,48]:
    values=[rng.randint(-1000,1000) for _ in range(12)];values[4]=rng.randint(0,100);contact=[rng.randint(0,1) for _ in range(4)];flip=rng.randint(0,1);actor=0x02004000;component=0x02008000;sprite=0x02009000;svtable=0x02009100
    u.mem_write(actor,bytes(0x400));u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x174,bytes([16,50]));u.mem_write(actor+0x178,struct.pack('<2i',*xy));u.mem_write(actor+0xa8,struct.pack('<4i',*contact));u.mem_write(actor+0x1bc,struct.pack('<I',component));u.mem_write(actor+0x1c0,struct.pack('<I',sprite));u.mem_write(actor+0x1e8,struct.pack('<I',ROM_BASE+0x4b73c));u.mem_write(component,struct.pack('<12i',*values));u.mem_write(sprite,struct.pack('<I',flip));u.mem_write(sprite+0x2c,struct.pack('<I',svtable));u.mem_write(svtable+0x18,struct.pack('<2I',0,0x03001121));u.mem_write(0x03001100,struct.pack('<2H',0x2000|buttons,0x4770))
    u.ctl_remove_cache(0x03001100,0x03001104);u.reg_write(UC_ARM_REG_R0,actor);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(0x0800de8d,0x03001000,count=300000)
    if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original input routine did not return')
    expected=struct.unpack('<12i',u.mem_read(component,48));expected_flip=struct.unpack('<I',u.mem_read(sprite,4))[0];parameters=(ctypes.c_int32*12)(*values);facing=(ctypes.c_int32*1)(flip);code=fn(path,buttons,(ctypes.c_int32*2)(*xy),16,50,parameters,(ctypes.c_int32*4)(*contact),facing)
    if code or tuple(parameters)!=expected or facing[0]!=expected_flip:raise AssertionError((n,xy,buttons,code,tuple(parameters),expected,facing[0],expected_flip))
    cases+=1
 result={'original_directional_logic':'0x0800DE8C','cases':cases,'mismatches':0,'scope':'Original actor code; input getter and sprite-facing setter replaced by test fixtures; original static probes/state setters execute unmodified; dynamic-contact list empty'}
 (root/'docs/horizontal_input_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
