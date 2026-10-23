import ctypes as C,struct,json,sys
from verify_generic_runtime import Original,Rom,FC,IP,ROOT
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
r=Rom(sys.argv[1]);o=Original(r);u=o.u;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32;P=C.c_void_p;SINK=C.CFUNCTYPE(C.c_int,C.c_int,C.c_uint32,I,P);fx=[];orig=[]
@FC
def fetch(a,out,n,ctx):
 try:data=u.mem_read(a,n*4)
 except:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,data)):out[i]=v
 return 1
@SINK
def sink(k,a,b,ctx):fx.append((k,a,b));return 0
def hook(uc,a,size,ctx):
 ret=None
 if a==0x080163ac:orig.append((11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));ret=0
 elif a==0x08011160:orig.append((35,0,0));ret=0
 elif a==0x08019024:orig.append((26,uc.reg_read(UC_ARM_REG_R0),0));ret=0x08025000
 elif a==0x0800bec0:
  p=uc.reg_read(UC_ARM_REG_R0);packet=struct.unpack('<3i',uc.mem_read(p,12))
  if packet[:2]!=(0,3):orig.append((1,0x08024be0,0))
  ret=0
 if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
init=l.s2_puss_boss_init;init.argtypes=[IP,FC,P,IP,IP];behavior=l.s2_puss_boss_behavior;behavior.argtypes=[IP,IP,I,I,FC,SINK,P];receive=l.s2_puss_boss_receive;receive.argtypes=[IP,IP,IP,I,I,FC,SINK,P]
checks=0
def setup():
 o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x0200324c,bytes(4));u.mem_write(0x020033e0,bytes(4));o.call(0x0800c3d4,o.actor,190*256,142*256);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];u.mem_write(o.actor+0x164,struct.pack('<i',20));p=(I*80)();s=(I*16)();assert init((I*2)(190*256,142*256),fetch,None,p,s)==0;return p,s
def compare(tag,p,s):
 global checks
 expected=o.snapshot();indices=[*range(2,14),18,20,21,22,23,39,40,41,42,43,47,52,56,76,77,78];diff={i:(p[i],expected[i])for i in indices if p[i]!=expected[i]};assert not diff,(tag,diff)
 fields=list(struct.unpack('<9i',u.mem_read(o.actor+0x1cc,36)));assert list(s[:9])==fields,(tag,list(s[:9]),fields);assert fx==orig,(tag,fx,orig);checks+=1
p,s=setup();fx.clear();orig.clear();compare('ctor',p,s)
for state,phase,bounces,grabbed,tick,contact in[(0,0,0,0,1,0),(0,0,0,0,120,0),(1,0,0,0,200,0),(1,0,8,0,200,0),(1,2,0,0,200,0),(1,2,8,0,200,0),(2,0,0,0,200,1),(2,2,0,0,200,1),(2,1,9,0,200,1),(3,0,0,0,201,0),(3,2,5,0,201,0),(4,0,0,1,201,0),(4,2,0,1,201,0),(4,2,0,3,201,0),(5,0,0,3,201,0)]:
 p,s=setup();s[0]=state;s[2]=phase;s[3]=bounces;s[6]=grabbed;s[4]=s[8]=200
 if contact==0:p[15]=1
 elif contact==1:p[14]=1
 u.mem_write(o.actor+0x1cc,struct.pack('<9i',*s[:9]));o.seed(p);u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));fx.clear();orig.clear();o.call(0x0800c48c,o.actor);assert behavior(p,s,20,tick,fetch,sink,None)==0;compare(('behavior',state,phase,bounces,grabbed,tick),p,s)
for state,phase,recovery,id,tick in[(3,0,0,10,200),(3,2,0,10,200),(2,0,0,10,200),(4,0,200,11,200),(4,0,200,11,201),(4,1,200,11,201),(4,3,200,11,201)]:
 p,s=setup();s[0]=state;s[2]=phase;s[8]=recovery;u.mem_write(o.actor+0x1cc,struct.pack('<9i',*s[:9]));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x02007200,struct.pack('<3i',0,id,0));fx.clear();orig.clear();o.call(0x0800cab4,o.actor,0x02007200);assert receive(p,s,(I*3)(0,id,0),20,tick,fetch,sink,None)==u.reg_read(UC_ARM_REG_R0);compare(('receive',state,phase,id,tick),p,s)
report=dict(differential_cases=checks,mismatches=0,scope='74 constructor, state dispatch, wall/ground branches, capture/release, strict deadlines, original sounds and three-capture finish.',device_tested=False)
(ROOT/'docs/puss_boss_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
