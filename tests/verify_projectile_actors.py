#!/usr/bin/env python3
"""Original spell/cookie projectiles67/68/69/157/160/161: construction, movement, impacts and parry."""
import ctypes as C,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from extract_collision import scene_collision
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32;P=C.c_void_p;r=Rom(sys.argv[1]);o=Original(r);u=o.u;rng=random.Random(67);SINK=C.CFUNCTYPE(C.c_int,C.c_int,C.c_uint32,I,P);fx=[];originalFx=[]
u.mem_write(0x02000800,struct.pack('<3I',0x08000000+scene_collision(r,21)['root_offset'],5440*256,640*256))
@FC
def fetch(a,out,n,ctx):
 try:raw=u.mem_read(a,n*4)
 except Exception:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
 return 1
@SINK
def sink(kind,addr,scale,ctx):fx.append((kind,addr,scale));return 0
hero=0x02008000;u.mem_write(hero+0x178,struct.pack("<2i",2100*256,300*256))
def hooks(uc,a,size,ctx):
 if a==0x080078cc:uc.reg_write(UC_ARM_REG_R0,hero);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 if a==0x080163ac:originalFx.append((11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 if a in [0x0800bf04,0x0800bee8,0x0800bec0]:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hooks)
init=l.s2_projectile_init;init.argtypes=[C.c_char_p,I,IP,I,I,FC,SINK,P,IP,IP];step=l.s2_projectile_step;step.argtypes=[C.c_char_p,I,IP,I,FC,SINK,P];receive=l.s2_projectile_receive;receive.argtypes=[I,IP,IP,IP,I,FC,SINK,P]
home=l.s2_projectile_target;home.argtypes=[I,IP,IP,FC,P]
path=str(ROOT/'collision/scene_21/scene.s2cl').encode();constructors=frames=parries=0
for kind,definition in [(67,0x0804d6b4),(69,0x0804d71c),(68,0x0804d784),(157,0x0804d7b8),(146,0x0804d6e8),(160,0x0804d64c),(161,0x0804d680)]:
 for flips in range(4):
  for xy in [[1900*256,250*256],[4930*256,400*256],[100*256,500*256],[0,0]]:
   o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x0203f000,struct.pack('<2I',flips&1,flips>>1));u.mem_write(0x0200324c,bytes(4));u.mem_write(0x020033e0,bytes(4));fx.clear();originalFx.clear();o.call(0x080121a4,o.actor,definition,*xy);o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];s=(I*80)();deadline=I();assert init(path,kind,(I*2)(*xy),flips,0,fetch,sink,None,s,C.byref(deadline))==0
   def compare(tag):
    # Projectile subclasses have no generic actor fields at2A8..2E0.
    expected=o.snapshot();indices=[*range(2,14),18,38,20,21,22,23,39,40,41,42,43,47,56,72,73,74,75,76,77,78];diff={i:(s[i],expected[i])for i in indices if s[i]!=expected[i]};assert not diff,(kind,flips,tag,diff);assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert fx==originalFx,(tag,fx,originalFx)
   compare('ctor');constructors+=1
   for tick in range(1,181):
    fx.clear();originalFx.clear();u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick))
    if s[40]&1:break
    # Source event5 is a directional reflection; it intentionally returns0.
    if tick in [12,13,24,55] and s[47]!=struct.unpack_from('<i',r.data,definition-0x08000000+4)[0]:
     event=(I*3)(0,5,1 if s[18] else 2);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08012568,o.actor,0x02007200);assert receive(kind,s,C.byref(deadline),event,tick,fetch,sink,None)==u.reg_read(UC_ARM_REG_R0);parries+=1;compare(('parry',tick))
    # Actual outgoing-hit fixture causes original impact on the next frame.
    if tick==80:s[40]|=16;u.mem_write(o.actor+0x15c,bytes([u.mem_read(o.actor+0x15c,1)[0]|16]))
    try:o.call(0x08018208,o.actor)
    except Exception as error:raise AssertionError((kind,tick,hex(u.reg_read(UC_ARM_REG_PC))))from error
    assert step(path,kind,s,tick,fetch,sink,None)==0
    assert home(kind,s,(I*2)(2100*256,300*256),fetch,None)==0
    compare(('frame',tick));frames+=1
# Query74 spans all source animations and sequence frames.
q=l.s2_generic_frame_query;q.argtypes=[IP,FC,P,IP];queries=0
for row in json.loads((ROOT/'objects/generic_animation_headers.json').read_text())['animations']:
 header=bytes.fromhex(row['header_hex']);count=header[21]
 for frame in range(count):
  s=(I*80)();s[47]=row['address'];s[22]=frame;u.mem_write(o.sprite+8,struct.pack('<2i',s[47],frame));expected=o.query(74);out=I();assert q(s,fetch,None,C.byref(out))==0 and out.value==expected,(hex(s[47]),frame,out.value,expected);queries+=1
report=dict(original_projectile_constructors=constructors,original_projectile_frames=frames,directional_parry_cases=parries,original_attack_frame_queries=queries,mismatches=0,scope='Actual121A4/18208/123DC/12470/12568 for67/68/69/146/157/160/161, original scene21 collision. Fixed nearest hero for homing157; Outgoing-hit flag, silent audio device and allocator are explicit fixtures; all387 animations queried for74.')
(ROOT/'docs/projectile_actors_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
