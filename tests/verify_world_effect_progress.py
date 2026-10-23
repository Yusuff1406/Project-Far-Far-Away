#!/usr/bin/env python3
"""Camera tail0962, screen1ADA0 and RGB555 palette3 against original code."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R6,UC_ARM_REG_SP,UC_ARM_REG_PC,UC_ARM_REG_LR
UP=ctypes.POINTER(ctypes.c_uint16)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Rom(args.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202627);cam=0x02006800;minimum=0x02006600;maximum=0x02006610;positions=[]
 def hook(uc,addr,size,data):
  ret=None
  if addr==0x08014fd8:ret=minimum
  elif addr==0x08014fe4:ret=maximum
  elif addr==0x080150e0:positions.append([ctypes.c_int32(uc.reg_read(UC_ARM_REG_R1)).value,ctypes.c_int32(uc.reg_read(UC_ARM_REG_R2)).value]);ret=0
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(0x020031e8,struct.pack('<I',0x02006000));camera=lib.s2_camera_effect_step;camera.argtypes=[IP,IP,IP,IP]
 for case in range(10000):
  values=[rng.choice([-2147483648,2147483647,-1,0,128,1024,rng.randint(-2000,2000)]),rng.randint(-10,10),rng.choice([-2147483648,2147483647,0,128,rng.randint(-2000,2000)]),rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]),rng.choice([-1,0,1,2,3])];s=(ctypes.c_int32*5)(*values);base=(ctypes.c_int32*2)(*[rng.randint(-2147483648,2147483647) for _ in range(2)]);bounds=(ctypes.c_int32*4)(*[rng.randint(-2147483648,2147483647) for _ in range(4)]);out=(ctypes.c_int32*2)(17,19)
  u.mem_write(cam+0x10,struct.pack('<2i',*base));u.mem_write(cam+0x20,struct.pack('<5i',*s));u.mem_write(minimum,struct.pack('<2i',*bounds[:2]));u.mem_write(maximum,struct.pack('<2i',*bounds[2:]));sp=0x0203f000;u.mem_write(sp,struct.pack('<6I',0,0,0,0,0,0x03001001));u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_R6,cam);positions.clear();u.emu_start(0x08000963,0x03001000,count=500000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000
  result=camera(s,base,bounds,out);assert list(s)==list(struct.unpack('<5i',u.mem_read(cam+0x20,20))),(case,list(s),values);assert result==len(positions);assert list(out)==(positions[0] if positions else [17,19]),(case,list(out),positions)
 screen=lib.s2_screen_effect_step;screen.argtypes=[IP];globals=[struct.unpack_from('<I',rom.data,a)[0] for a in [0x1af5c,0x1af60,0x1af64,0x1af68]]
 for case in range(10000):
  s=(ctypes.c_int32*4)(rng.choice([-2147483648,2147483647,0,64,rng.randint(-1000,1000)]),rng.choice([-2147483648,2147483647,-1,0,1,rng.randint(-1000,1000)]),rng.choice([-1,0,1,2,3,4]),rng.choice([-2147483648,2147483647,0,64,rng.randint(-1000,1000)]))
  for a,v in zip(globals,s):u.mem_write(a,struct.pack('<i',v))
  o.call(0x0801ada0);assert screen(s)==0;assert list(s)==[struct.unpack('<i',u.mem_read(a,4))[0] for a in globals],(case,list(s))
 palette=lib.s2_screen_effect_rgb555;palette.argtypes=[IP,UP,UP,ctypes.c_size_t];argb=lib.s2_screen_effect_argb;argb.argtypes=[IP,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t];source=struct.unpack_from('<I',rom.data,0x1af14)[0];dest=struct.unpack_from('<I',rom.data,0x1af0c)[0];factor=struct.unpack_from('<I',rom.data,0x1af04)[0];mode=globals[2];pixelCases=0
 for case in range(1000):
  intensity=rng.choice([0,1,32,63,64,-1,-2147483648,2147483647,rng.randint(-100000,100000)]);colors=[rng.randrange(65536) for _ in range(512)];a=(ctypes.c_uint16*512)(*colors);b=(ctypes.c_uint16*512)();s=(ctypes.c_int32*4)(0,1,3,intensity);u.mem_write(mode,struct.pack('<i',3));u.mem_write(factor,struct.pack('<i',intensity));u.mem_write(source,struct.pack('<512H',*colors));o.call(0x0801adfc);assert palette(s,a,b,512)==0;assert list(b)==list(struct.unpack('<512H',u.mem_read(dest,1024)));pixelCases+=512
  if 0<=intensity<=64:
   pixels=(ctypes.c_uint32*512)(*[0xff000000|((c&31)*255//31)<<16|(((c>>5)&31)*255//31)<<8|((c>>10)&31)*255//31 for c in colors]);assert argb(s,pixels,512)==0
   expected=[0xff000000|((c&31)*255//31)<<16|(((c>>5)&31)*255//31)<<8|((c>>10)&31)*255//31 for c in b];assert list(pixels)==expected
 result={'original_camera_tail_cases':10000,'original_screen_step_cases':10000,'original_mode3_palette_cases':1000,'rgb555_words_compared':pixelCases,'mismatches':0,'scope':'Original0962 camera effect tail with supplied base/bounds and renderer setter fixtures;1ADA0 global scalar progression;1ADFC mode3 full512-word palette. Camera follow/smoothing, screen modes1/2 and original full scheduler excluded. ARGB adapter checked for normal factor0..64.'};(ROOT/'docs/world_effect_progress_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
