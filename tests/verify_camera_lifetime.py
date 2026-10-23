#!/usr/bin/env python3
"""Original051E0 activity predicate and D438 out-of-level defeat boundary."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import *
def main():
 o=Original(Rom(sys.argv[1]));o.camera_fixture=False;u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));active=l.s2_actor_camera_active;active.argtypes=[IP,IP];outside=l.s2_actor_outside_world;outside.argtypes=[IP,ctypes.c_int32,ctypes.c_int32];rng=random.Random(51);packets=[]
 def hook(uc,a,size,data):
  if a in [0x800bf04,0x800fb2c,0x800fadc]:uc.reg_write(UC_ARM_REG_R0,0x2007400 if a==0x800fb2c else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif a==0x800bec0:packets.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(0x2003268,struct.pack('<I',0x2009000));cases=deaths=0
 for i in range(2048):
  s=(ctypes.c_int32*80)();camera=(ctypes.c_int32*4)(-240*256,80*256,720*256,480*256);s[0]=rng.choice([-240*256-1,-240*256,480*256,480*256+1,rng.randrange(-400*256,3600*256)]);s[1]=rng.choice([80*256-1,80*256,560*256,560*256+1,rng.randrange(-300*256,900*256)]);s[39]=rng.randrange(256);s[40]=rng.randrange(256);s[30]=rng.randrange(1,256);s[31]=rng.randrange(1,256)
  u.mem_write(0x2009000,bytes(camera));u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x15d,bytes([s[39]]));u.mem_write(o.actor+0x15c,bytes([s[40]]));u.mem_write(o.actor+0x174,bytes([s[30],s[31]]));o.call(0x80051e0,o.actor);assert bool(active(s,camera))==bool(u.reg_read(UC_ARM_REG_R0)),(i,list(s[:2]),s[39],s[40]);cases+=1
  packets.clear();o.call(0x800d438,o.actor);assert bool(outside(s,3200*256,400*256))==bool(packets),(i,list(s[:2]),s[30],s[31],packets);deaths+=bool(packets)
 # Use the original health-animation header, rather than a synthetic life byte.
 u.mem_write(o.actor,bytes(0x1000));o.heap=0x2001000
 context=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(context,bytes(32));u.mem_write(context+8,struct.pack('<I',0x083283f8));u.mem_write(0x203f000,bytes(16));o.call(0x80111cc,o.actor,0x804b714,35*256,350*256)
 counters=list(struct.unpack('<2i',u.mem_read(o.actor+0x1fc,8)));assert counters==[6,6],counters
 report={'original_health_counters':counters,'health_animation':hex(0x083283f8),'source_activity_cases':cases,'source_boundary_cases':cases,'defeat_packets':deaths,'mismatches':0,'scope':'Actual051E0/07B0 camera point/forced flags; actualD438 body/world bounds and defeat packet. Only global packet delivery intercepted. Native viewport expansion preserves source240/160 margins; full original category scheduler excluded.'};(ROOT/'docs/camera_lifetime_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
