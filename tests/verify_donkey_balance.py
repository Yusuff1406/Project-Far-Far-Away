#!/usr/bin/env python3
"""Type138 source behavior9D84 and full18208 frames, with explicit fixtures."""
import ctypes as C,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC,RC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
r=Rom(sys.argv[1]);o=Original(r);u=o.u;lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(66);P=C.c_void_p;I=C.c_int32
SC=C.CFUNCTYPE(C.c_int,C.c_int,C.c_uint32,I,P);REG=C.CFUNCTYPE(None,C.c_int,P)
score=[];expected=[];rv=0;isolated=True
@RC
def random_(ctx):return rv
@SC
def sink(kind,address,scale,ctx):score.append(kind);return 0
@REG
def registry(enabled,ctx):pass
@FC
def fetch(a,out,n,ctx):
 try:raw=u.mem_read(a,n*4)
 except Exception:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
 return 1
def hooks(uc,a,size,ctx):
 ret=0 if isolated and a==0x080139b8 else None
 if a==0x08009358:ret=0x02007800
 if a==0x08009288:expected.append(29);ret=0
 if a==0x0800021a:ret=rv
 if a in [0x0800bf04,0x0800bee8,0x0800bec0,0x080163ac]:ret=0
 if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hooks);o.ctor(0x0804a4d8,(119*256,145*256));u.mem_write(o.actor,struct.pack('<I',0x0200117c))
behavior=lib.s2_donkey_balance_behavior;behavior.argtypes=[IP,RC,SC,P]
s=(I*80)()
for case in range(4000):
 s[40]=rng.choice([0,8,16,24]);s[7]=rng.choice([-2147483648,-449,-448,-447,-1,0,1,446,447,448,449,2147483647,rng.randint(-600,600)]);s[5]=rng.randint(-5000,5000);s[15:17]=[rng.randrange(2),rng.randrange(2)];s[65:67]=[rng.randrange(2),rng.randrange(2)];rv=rng.getrandbits(15);score.clear();expected.clear();o.seed(s);o.call(0x08009d84,o.actor);assert behavior(s,random_,sink,None)==0
 expect={i:v for i,v in enumerate(struct.unpack('<12i',u.mem_read(o.component,48)),2)};assert all(s[i]==expect[i] for i in [7,5]),(case,s[7],expect[7],s[5],expect[5]);assert score==expected
isolated=False
# Whole frames use actual scene07 wall collision and original script/reactions.
from extract_collision import scene_collision
u.mem_write(0x02000800,struct.pack('<3I',0x08000000+scene_collision(r,7)['root_offset'],240*256,160*256))
init=lib.s2_generic_runtime_init;init.argtypes=[IP,C.c_int,C.c_uint32,I,FC,P,IP]
start=lib.s2_vm_start;start.argtypes=[C.c_uint32,IP]
step=lib.s2_donkey_balance_step;step.argtypes=[C.c_char_p,IP,IP,I,I,I,FC,RC,P,C.c_int,IP,REG,SC]
activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP]
reactionInit=lib.s2_reactions_init;reactionInit.argtypes=[I,IP]
s=(I*80)();assert init((I*2)(119*256,145*256),0,0x0834abf8,0,fetch,None,s)==0;s[6]=25
vm=(I*64)();reaction=(I*72)();start(0x0804a530,vm);reactionInit(0,reaction)
o.ctor(0x0804a4d8,(119*256,145*256));u.mem_write(o.actor,struct.pack('<I',0x0200117c));o.seed(s);o.call(0x08013344,o.vm,0x0804a530)
u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));strikes=0
for tick in range(1,1201):
 for glob in [0x0200324c,0x020033e0]:u.mem_write(glob,struct.pack('<i',tick))
 rv=37;score.clear();expected.clear()
 # Foot contact fixtures, using actual activation handler to set pending flag.
 if tick>2 and tick%31==0:
  event=(I*3)(0,8,0);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007200);assert activate(vm,reaction,event)==1;s[40]|=16;u.mem_write(o.actor+0x15c,bytes([u.mem_read(o.actor+0x15c,1)[0]|16]));strikes+=1
 o.call(0x08018208,o.actor)
 assert step(str(ROOT/'collision/scene_07/scene.s2cl').encode(),s,vm,tick,240*256,160*256,fetch,random_,None,4096,reaction,registry,sink)==0
 diff={i:(s[i],v)for i,v in o.snapshot().items()if s[i]!=v};assert not diff,(tick,diff)
 assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8))),(tick,'position');assert score==expected,(tick,score,expected)
report=dict(behavior_original_cases=4000,whole_original_actor_frames=1200,foot_contact_fixtures=strikes,mismatches=0,scope='9D84 plus18208 and source4A530/4A860 scripts. Original scene07 walls. Input contacts, random values, score manager and camera are explicit fixtures; no Android device test.')
(ROOT/'docs/donkey_balance_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
