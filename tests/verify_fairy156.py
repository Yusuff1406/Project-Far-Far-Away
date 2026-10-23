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
hero=0x02008000;u.mem_write(hero+0x178,struct.pack('<2i',70*256,300*256));u.mem_write(0x0200b080,bytes(64))
def hook(uc,a,size,ctx):
 ret=None
 if a==0x080163ac:orig.append((11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));ret=0
 elif a==0x08003a9c:ret=1800
 elif a==0x0800021a:ret=0
 elif a==0x080078cc:ret=hero
 elif a==0x08007908:ret=0x0200b080
 elif a==0x080059d8:orig.append((31,uc.reg_read(UC_ARM_REG_R0),0));ret=0
 elif a==0x08019024:orig.append((26,uc.reg_read(UC_ARM_REG_R0),0));ret=0x08025000
 elif a==0x0800bec0:
  p=uc.reg_read(UC_ARM_REG_R0);packet=struct.unpack('<3i',uc.mem_read(p,12))
  if packet[0]!=0 or packet[1]!=3:orig.append(('packet',packet))
  ret=0
 if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
init=l.s2_fairy156_init;init.argtypes=[IP,FC,P,IP,IP,IP];behavior=l.s2_fairy156_behavior;behavior.argtypes=[IP,IP,IP,IP,IP,I,I,I,FC,SINK,P];receive=l.s2_fairy156_receive;receive.argtypes=[IP,IP,IP,IP,I,FC,SINK,P]
markers=(I*8)(463*256,191*256,1031*256,63*256,2447*256,223*256,0,0);u.mem_write(0x02002df4,struct.pack('<8i',*markers));target=(I*2)(70*256,300*256)
o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));o.call(0x08002ddc,o.actor,475*256,180*256);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];p=(I*80)();aux=(I*80)();s=(I*8)();assert init((I*2)(475*256,180*256),fetch,None,p,s,aux)==0
cases=0
def compare(tag):
 global cases
 expected=o.snapshot();indices=[*range(2,14),18,20,21,22,23,39,40,41,42,43,47,52,56,76,77,78];diff={i:(p[i],expected[i])for i in indices if p[i]!=expected[i]};assert not diff,(tag,diff)
 fields=list(struct.unpack('<5i',u.mem_read(o.actor+0x1cc,20)));assert [s[0],s[1],s[2],s[5],s[4]]==fields,(tag,list(s),fields)
 expectedfx=[]
 for x in orig:
  if x[0]=='packet':
   packet=x[1];a=0x08024b28 if packet==(9,1,1)else 0x08024b34 if packet==(9,1,2)else 0x08024be0;expectedfx.append((1,a,0))
  else:expectedfx.append(x)
 # Native marks existing projectile collection; oracle fixture's collection is empty.
 assert [x for x in fx if x[0]!=32]==expectedfx,(tag,fx,expectedfx)
 cases+=1
compare('ctor')
for tick in[1,29,30,119,120,121,145,146,147,200]:
 fx.clear();orig.clear();u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick))
 if tick==145:p[20]=1;u.mem_write(o.sprite,bytes([1]))
 o.call(0x080033d8,o.actor);assert behavior(p,s,aux,markers,target,tick,1800,0,fetch,sink,None)==0;compare(('behavior',tick))
for tick,id in[(201,7),(202,13),(203,13),(217,13),(218,13),(234,13)]:
 fx.clear();orig.clear();u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x02007200,struct.pack('<3i',1,id,0));o.call(0x08002e70,o.actor,0x02007200);expected=u.reg_read(UC_ARM_REG_R0);assert receive(p,s,aux,(I*3)(1,id,0),tick,fetch,sink,None)==expected;compare(('damage',tick))
for tick in[263,264]:
 fx.clear();orig.clear();u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));o.call(0x080033d8,o.actor);assert behavior(p,s,aux,markers,target,tick,1800,0,fetch,sink,None)==0;compare(('finish',tick))
report=dict(differential_cases=cases,mismatches=0,scope='156 constructor, behavior dispatch, hits, cooldown and dialogue. Empty projectile collection and fixed nearest hero are explicit oracle fixtures.',device_tested=False)
(ROOT/'docs/fairy156_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
