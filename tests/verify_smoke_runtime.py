#!/usr/bin/env python3
"""Original type71 constructor/update versus native animation, physics and expiry."""
import sys,struct,ctypes,json
from verify_generic_runtime import *
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 init=l.s2_smoke_runtime_init;init.argtypes=[ctypes.c_char_p,IP,ctypes.c_int,ctypes.c_int32,FC,ctypes.c_void_p,IP]
 step=l.s2_smoke_runtime_step;step.argtypes=[ctypes.c_char_p,IP,ctypes.c_int32]
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
  return 1
 removed=[]
 def hook(uc,a,size,data):
  if a==0x80163ac:
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if a==0x8005168:
   removed.append(1);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 path=str(ROOT/'collision/scene_00/scene.s2cl').encode();frames=0;cases=0;expiry=[]
 for xy in [(120,325),(1000,200),(1800,180),(2750,130),(0,160)]:
  for flips in range(4):
   for start in [0,217]:
    o.heap=0x2010000;u.mem_write(o.actor,bytes(4096));u.mem_write(0x203f000,struct.pack('<2I',flips&1,flips>>1));u.mem_write(0x200324c,struct.pack('<i',start));u.mem_write(0x20033e0,struct.pack('<i',start));removed.clear()
    o.call(0x80121a4,o.actor,0x804d7ec,xy[0]*256,xy[1]*256);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
    s=(ctypes.c_int32*80)();assert init(path,(ctypes.c_int32*2)(*(v*256 for v in xy)),flips,start,fetch,None,s)==0
    for t in range(start,start+41):
     if t>start:
      u.mem_write(0x200324c,struct.pack('<i',t));u.mem_write(0x20033e0,struct.pack('<i',t));o.call(0x8018208,o.actor);assert step(path,s,t)==0
     expected={0:struct.unpack('<i',u.mem_read(o.actor+0x178,4))[0],1:struct.unpack('<i',u.mem_read(o.actor+0x17c,4))[0]}
     expected.update({i:v for i,v in enumerate(struct.unpack('<12i',u.mem_read(o.component,48)),2)})
     sp=o.sprite
     expected.update({18:u.mem_read(sp+0x28,1)[0],38:u.mem_read(sp+0x29,1)[0],20:u.mem_read(sp,1)[0],21:struct.unpack('<i',u.mem_read(sp+4,4))[0],22:struct.unpack('<i',u.mem_read(sp+12,4))[0],23:struct.unpack('<i',u.mem_read(sp+16,4))[0],40:u.mem_read(o.actor+0x15c,1)[0]|bool(removed)})
     diff={i:(s[i],v)for i,v in expected.items()if s[i]!=v};assert not diff,(xy,flips,start,t,diff);frames+=1
     if removed:expiry.append(t-start);break
    else:raise AssertionError('smoke did not expire')
    cases+=1
 report={'constructor_cases':cases,'original_frame_comparisons':frames,'expiry_ticks':sorted(set(expiry)),'mismatches':0,'scope':'Real121A4 constructor/18208 update/123DC expiry, original static collision and animation. Allocator/camera/removal manager are fixtures; native retains removed marker instead of heap free. Offscreen world activation excluded.'}
 (ROOT/'docs/smoke_runtime_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
