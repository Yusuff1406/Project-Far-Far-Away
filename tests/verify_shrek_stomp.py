#!/usr/bin/env python3
"""Type3 ctor and stomp entry/phases versus original Thumb; explicit fixture scope."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;context=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(context,bytes(32));u.mem_write(context+8,struct.pack('<I',0x02006000));u.mem_write(0x02006000,bytes(32));u.mem_write(0x02006015,bytes([4]));u.mem_write(0x0203f000,bytes(16));fx=[];horizontal=[]
 def hook(uc,a,size,data):
  if a in (0x0800bec0,0x0800bf04):uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif a==0x0800fb2c:uc.reg_write(UC_ARM_REG_R0,0x02007400);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif a==0x0800de8c:horizontal.append(1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.call(0x080111cc,o.actor,0x0804b714,35*256,350*256);assert struct.unpack('<I',u.mem_read(o.actor,4))[0]==0x02001e6c;o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];camera=0x02006800;cameraGlobal=struct.unpack_from('<I',o.r.data,0xa64)[0];u.mem_write(cameraGlobal,struct.pack('<I',camera))
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];enter=lib.s2_shrek_stomp_enter;enter.argtypes=[IP,IP,IP,ctypes.c_int32,ctypes.c_uint32,FC,ctypes.c_void_p];phase=lib.s2_shrek_stomp_behavior;phase.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,SINK,ctypes.c_void_p];audio=lib.s2_shrek_stomp_audio;audio.argtypes=[IP,IP,ctypes.c_int32,FC,SINK,ctypes.c_void_p]
 @FC
 def fetch(a,out,n,ctx):
  try:raw=u.mem_read(a,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 @SINK
 def sink(kind,address,scale,ctx):fx.append([kind,address,scale]);return 0
 rng=random.Random(39);events=(ctypes.c_int32*3)(1,7,0)
 def seed(state):
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();at=rng.randrange(-1000,1000);wt=rng.choice([2147483647,-2147483648,rng.randrange(-1000,1000)]);anim=0x0834f424 if state==21 else 0x0834f40c
  assert init((ctypes.c_int32*2)(123*256,250*256),rng.randrange(2),anim,at,fetch,None,s)==0;s[2:14]=[rng.randrange(-3000,3000)for _ in range(12)];s[20]=rng.choice([0,1,255]);s[22]=rng.randrange(s[77]);s[23]=at+rng.randrange(-3,5);s[14]=rng.randrange(2);s[64]=rng.randrange(2);s[41:44]=[rng.randrange(12),rng.randrange(14),rng.randrange(3)];e[0]=state;status[3]=rng.randrange(256);book[1]=0x08053ccc;book[5]=rng.randrange(-1000,1000);o.seed(s)
  u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x170,struct.pack('<hhBBH',s[72],s[73],s[30],s[31],0))
  for off,value in [(0x1e8,0x0804b714),(0x1d8,state),(0x1ec,0),(0x258,0),(0x260,0),(0x25c,book[1]),(0x270,book[5])]:u.mem_write(o.actor+off,struct.pack('<i',value))
  u.mem_write(o.actor+0x20c,bytes([status[3]]));u.mem_write(o.actor+0x228,struct.pack('<3i',*events));u.mem_write(0x0200324c,struct.pack('<i',at));u.mem_write(0x020033e0,struct.pack('<i',wt));u.mem_write(0x02007400,bytes(16));u.mem_write(camera+0x20,bytes(20));fx.clear();horizontal.clear();return s,e,status,book,at,wt
 def compare(data,label):
  s,e,status,book,at,wt=data;expected=[list(struct.unpack('<12i',u.mem_read(o.component,48))),u.mem_read(o.sprite,1)[0],list(struct.unpack('<4i',u.mem_read(o.sprite+4,16))),list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],*[struct.unpack('<i',u.mem_read(o.actor+off,4))[0]for off in (0x260,0x25c,0x270)],u.mem_read(o.actor+0x20c,1)[0]];actual=[list(s[2:14]),s[20],[s[21],s[47],s[22],s[23]],list(s[41:44]),e[0],book[0],book[1],book[5],status[3]];assert actual==expected,(label,actual,expected)
 for i in range(2000):
  data=seed(rng.choice([3,4]));s,e,status,book,at,wt=data;pressed=i%2;u.mem_write(0x02007408,bytes([pressed*2]));o.call(0x08010d58,o.actor);assert u.reg_read(UC_ARM_REG_R0)==pressed
  if pressed:assert enter(s,e,book,at,0x0804b73c,fetch,None)==0
  compare(data,('entry',i))
 for state,address in [(19,0x08010de4),(20,0x08010ed8),(21,0x08010e64)]:
  for i in range(1500):
   data=seed(state);s,e,status,book,at,wt=data;o.call(address,o.actor);assert phase(s,e,status,book,0,wt,at,0x0804b73c,events,fetch,sink,None)==0;compare(data,(state,i));expected=[[20,1024,128]]if state==20 and (s[14]or s[64])else [];assert fx==expected
   if expected:assert list(struct.unpack('<5i',u.mem_read(camera+0x20,20)))==[1024,3,128,0,2]
   if state==21:assert horizontal==[1]
 for i in range(1000):
  s,e,status,book,at,wt=seed(19);o.call(0x0800fa4c,o.actor);cue=u.reg_read(UC_ARM_REG_R0);assert audio(s,book,at,fetch,sink,None)==0;assert fx==([[11,0x08053ccc,256]]if cue else [])
 report={'actual_constructor':'0x080111CC','actual_vtable':'0x02001E6C','original_cases':7500,'mismatches':0,'scope':'Real type3 constructor, stomp entry/phases, animation/motion helpers, event9 and audio cue predicate. Allocator, scene registration, input pointer and phase21 horizontal routine are explicit fixtures. Full world/device execution excluded.'};(ROOT/'docs/shrek_stomp_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
