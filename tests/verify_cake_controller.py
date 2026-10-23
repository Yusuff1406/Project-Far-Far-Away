"""Differential controller154 construction/damage/timer against B704/B870/B7C0."""
import ctypes as C,struct,json,sys
from verify_generic_runtime import Original,Rom,FC,IP,ROOT
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
r=Rom(sys.argv[1]);o=Original(r);u=o.u;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32;P=C.c_void_p
SINK=C.CFUNCTYPE(C.c_int,C.c_int,C.c_uint32,I,P);fx=[];original=[];remaining=1800
@FC
def fetch(a,out,n,ctx):
 try:data=u.mem_read(a,n*4)
 except:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,data)):out[i]=v
 return 1
@SINK
def sink(k,a,scale,ctx):fx.append((k,a,scale));return 0
def hook(uc,a,size,ctx):
 global remaining
 ret=None
 if a==0x080163ac:original.append((11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));ret=0
 elif a==0x08000a68:original.append((20,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)));ret=0
 elif a==0x0800bec0:
  p=uc.reg_read(UC_ARM_REG_R0);original.append(('packet',tuple(struct.unpack('<3i',uc.mem_read(p,12)))));ret=0
 elif a==0x08003a9c:ret=remaining
 elif a==0x08019024:original.append(('dialogue',uc.reg_read(UC_ARM_REG_R0)));ret=0x08025000
 if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
init=l.s2_cake_init;init.argtypes=[IP,FC,P,IP,IP,IP];receive=l.s2_cake_receive;receive.argtypes=[IP,IP,IP,I,SINK,P];step=l.s2_cake_step;step.argtypes=[IP,IP,IP,I,I,SINK,P]
cases=0
for xy in[(44*256,53*256),(120*256,80*256)]:
 o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x0200324c,bytes(4));u.mem_write(0x020033e0,bytes(4));o.call(0x0800b704,o.actor,*xy);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
 p=(I*80)();aux=(I*80)();state=(I*8)();assert init((I*2)(*xy),fetch,None,p,aux,state)==0
 snap=o.snapshot()
 for i in[2,3,4,5,6,7,8,9,10,11,12,13,18,20,21,22,23,39,40,41,42,43,47,52,56,76,77,78]:assert p[i]==snap[i],(i,p[i],snap[i])
 assert state[1]==state[2]==11
 for tick,event_id in[(1,13),(2,38),(3,38),(61,38),(62,38),(120,38),(150,38),(151,38),(211,38),(212,38),(272,38),(300,38)]:
  u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x02007200,struct.pack('<3i',3,event_id,0));original.clear();fx.clear();o.call(0x0800b870,o.actor,0x02007200);got=receive(p,state,(I*3)(3,event_id,0),tick,sink,None);assert got==u.reg_read(UC_ARM_REG_R0)
  hp,maxhp=struct.unpack('<2i',u.mem_read(o.actor+0x1d0,8));assert list(state[1:3])==[hp,maxhp]
  cooldown=struct.unpack('<i',u.mem_read(o.actor+0x1dc,4))[0];assert state[3]==cooldown
  expected=[(1,0x08024bbc,0)if x[0]=='packet'else x for x in original];assert fx==expected,(tick,fx,expected)
  if hp>0:assert p[22]==struct.unpack('<i',u.mem_read(o.sprite+12,4))[0]
  cases+=1
# Fresh timer cases: source queue dialogue42 precisely on remaining==0.
for remaining in[1800,1,0]:
 p=(I*80)();aux=(I*80)();state=(I*8)();assert init((I*2)(44*256,53*256),fetch,None,p,aux,state)==0;fx.clear();original.clear();u.mem_write(0x020033e0,struct.pack('<i',1799));o.call(0x0800b7c0,o.actor);assert step(p,aux,state,1799,remaining,sink,None)==0
 assert any(x[0]=='dialogue'and x[1]==42 for x in original)==(remaining==0);assert any(x[:2]==(26,42)for x in fx)==(remaining==0);cases+=1
report=dict(differential_cases=cases,mismatches=0,source_functions=['B704','B870','B7C0'],device_tested=False)
(ROOT/'docs/cake_controller_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
