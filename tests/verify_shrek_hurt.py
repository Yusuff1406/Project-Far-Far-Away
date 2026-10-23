#!/usr/bin/env python3
"""Type3 damage and recovery versus original Thumb, explicit overlay fixture."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;held=0;overlays=[]
 context=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(context,bytes(32));u.mem_write(context+8,struct.pack('<I',0x02006000));u.mem_write(0x02006000,bytes(32));u.mem_write(0x02006015,bytes([4]));u.mem_write(0x0203f000,bytes(16))
 def hook(uc,a,size,data):
  ret=None
  if a in [0x0800bec0,0x0800bf04]:ret=0
  elif a==0x0800fb2c:ret=0x02007400
  elif a==0x0800fadc:ret=held
  elif a==0x08018848:overlays.append(1);ret=0
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.call(0x080111cc,o.actor,0x0804b714,35*256,350*256)
 assert struct.unpack('<I',u.mem_read(o.actor,4))[0]==0x02001e6c
 o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 @FC
 def fetch(a,out,n,ctx):
  try:raw=u.mem_read(a,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP]
 hurt=lib.s2_shrek_hurt_receive;hurt.argtypes=[IP,IP,IP,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,FC,ctypes.c_void_p]
 recover=lib.s2_shrek_hurt_behavior;recover.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p]
 rng=random.Random(45);events=(ctypes.c_int32*3)(1,7,0)
 def put(off,value):u.mem_write(o.actor+off,struct.pack('<i',value))
 def seed(state):
  nonlocal held
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();wt=rng.choice([0,100,2147483647,-2147483648,rng.randrange(-1000,1000)]);at=rng.randrange(-1000,1000);held=rng.choice([0,16,32,48])
  assert init((ctypes.c_int32*2)(120*256,350*256),rng.randrange(2),0x0834f25c,at,fetch,None,s)==0
  s[2:14]=[rng.randrange(-3000,3000)for _ in range(12)];s[60]=rng.choice([-512,-1,0,1,512]);s[41:44]=[1,7,0];s[14:18]=[rng.randrange(2)for _ in range(4)];s[64:68]=[rng.randrange(2)for _ in range(4)];e[0]=state;status[0]=3;status[1]=rng.randrange(-2,5);status[3]=0;status[4]=ctypes.c_int32(wt+rng.choice([-1,0,1])).value;status[7]=rng.choice([0,ctypes.c_int32(wt-1).value,wt,ctypes.c_int32(wt+1).value]);book[0]=0;book[1]=0;book[2]=rng.randrange(-1000,1000);book[3]=rng.randrange(-100000,100000)
  o.seed(s);u.mem_write(o.actor+0x188,struct.pack('<i',s[60]));u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x170,struct.pack('<hhBBH',s[72],s[73],s[30],s[31],0))
  for off,value in [(0x1e8,0x0804b714),(0x1d8,state),(0x1ec,0),(0x258,0),(0x200,status[0]),(0x1fc,status[1]),(0x1d0,status[4]),(0x1f0,status[7]),(0x260,book[0]),(0x25c,book[1]),(0x1dc,book[2]),(0x204,book[3]),(0x264,0)]:put(off,value)
  u.mem_write(o.actor+0x20c,bytes([status[3]]));u.mem_write(o.actor+0x228,struct.pack('<3i',*events));u.mem_write(0x0200324c,struct.pack('<i',at));u.mem_write(0x020033e0,struct.pack('<i',wt));u.mem_write(0x02007400,bytes([held])+bytes(15));return s,e,status,book,wt,at
 def compare(data,label):
  s,e,status,book,wt,at=data
  expected=[list(struct.unpack('<12i',u.mem_read(o.component,48))),u.mem_read(o.sprite,1)[0],list(struct.unpack('<4i',u.mem_read(o.sprite+4,16))),list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),*[struct.unpack('<i',u.mem_read(o.actor+off,4))[0]for off in [0x1d8,0x1fc,0x1d0,0x1f0,0x260,0x25c,0x1dc,0x204]]]
  actual=[list(s[2:14]),s[20],[s[21],s[47],s[22],s[23]],list(s[41:44]),e[0],status[1],status[4],status[7],*book[:4]]
  assert actual==expected,(label,actual,expected)
 accepted=0
 for i in range(3000):
  data=seed(rng.choice([0,1,2,3,4,6,7,8,13,19,20]));s,e,status,book,wt,at=data
  # DD74 preserves normal held props (modes1/2/3/4/6), even while hurt.
  mode=rng.choice([0,1,2,3,4,6]);e[1]=mode;e[3]=77 if mode else 0
  put(0x258,mode);put(0x1ec,0x02007000 if mode else 0)
  event=(ctypes.c_int32*3)(rng.randrange(0,5),rng.choice([37,38,39]),rng.choice([-1,0,1,2,3]))
  u.mem_write(0x02007300,struct.pack('<3i',*event));o.call(0x08010c08,o.actor,0x02007300);expected=u.reg_read(UC_ARM_REG_R0)
  result=hurt(s,e,status,book,event,wt,at,0x0804b73c,fetch,None);assert result==expected,(i,result,expected);compare(data,('receive',i));accepted+=result
 for i in range(2000):
  data=seed(6);s,e,status,book,wt,at=data;o.call(0x0800f2f0,o.actor)
  assert recover(s,e,status,book,held,wt,at,0x0804b73c,events,fetch,None)==0;compare(data,('recover',i))
 report={'original_receive_cases':3000,'accepted_hits':accepted,'original_recovery_cases':2000,'mismatches':0,'scope':'Real type3 constructor111CC/vtable1E6C; original10C08->E3A0/DD74 and F2F0, real primary animation/motion, life/deadlines/cache. Allocator/world registry/input and auxiliary flashing sprite creation are explicit fixtures. Normal carry modes1/2/3/4/6 retained; effect modes5/7 are separately owned. Full world/game-over manager and device execution excluded.'}
 (ROOT/'docs/shrek_hurt_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
