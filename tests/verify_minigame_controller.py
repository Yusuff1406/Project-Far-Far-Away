#!/usr/bin/env python3
"""Original026B8 mouse timing/score gate and02650 wrap, isolated Thumb oracles."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR

def main():
 o=Original(Rom(sys.argv[1]));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));spawn=lib.s2_mouse_spawn_step;spawn.argtypes=[IP,ctypes.c_int32];wrap=lib.s2_mouse_wrap;wrap.argtypes=[IP];score=0;requests=[];rng=random.Random(141)
 def hook(uc,a,size,data):
  ret=None
  if a==0x080059d8:
   p=uc.reg_read(UC_ARM_REG_R1);requests.append((uc.reg_read(UC_ARM_REG_R0),*struct.unpack('<2i',uc.mem_read(p,8))));ret=0x02009000
  elif a in [0x08007ac4,0x08009358,0x080139b8]:ret=0
  elif a==0x08009284:ret=score
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def case(created,tick,points):
  nonlocal score
  score=points;requests.clear();s=(ctypes.c_int32*2)(created,tick);u.mem_write(o.actor+0x1c0,struct.pack('<2i',*s));o.call(0x080026b8,o.actor);made=spawn(s,score);assert list(s)==list(struct.unpack('<2i',u.mem_read(o.actor+0x1c0,8)));assert requests==([(140,120*256,0)]if made else []),(created,tick,score,requests)
 count=0
 for c in range(5):
  for t in [0,1,449,450,451,899,900,901,2147483647]:
   for points in [0,1,4,8,12]:case(c,t,points);count+=1
 for _ in range(1000):case(rng.randrange(5),rng.randrange(1500),rng.randrange(20));count+=1
 for countWrap,x in enumerate([-2147483648,-61441,-61440,-1,0,1,61439,61440,61441,122880,2147483647]+[rng.randrange(-150000,150000)for _ in range(1000)],1):
  xy=(ctypes.c_int32*2)(x,12345);u.mem_write(o.actor+0x178,struct.pack('<2i',*xy));o.call(0x08002650,o.actor);wrap(xy);assert list(xy)==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)))
 report={'controller_cases':count,'wrap_cases':countWrap,'mismatches':0,'scope':'Original026B8 and02650; allocation/registration, score accessor and base generic update hooked. Timing450/900 or score4/8 gates and strict 0/240px seam verified; complete mouse generic VM and contacts exercised in native integration test.'};(ROOT/'docs/minigame_controller_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
