#!/usr/bin/env python3
"""Differential generic messages, queries and whole actor frames against Thumb."""
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision
IP=ctypes.POINTER(ctypes.c_int32);FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_int,ctypes.c_void_p);RC=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p)
FIELDS={39:(0x15d,'B'),40:(0x15c,'B'),41:(0x1a0,'i'),42:(0x1a4,'i'),43:(0x1a8,'i'),44:(0x2c4,'i'),45:(0x2c8,'i'),46:(0x2cc,'i'),48:(0x2b0,'i'),49:(0x2c0,'i'),50:(0x2a8,'i'),51:(0x2ac,'i'),52:(0x2d0,'i'),53:(0x2d4,'B'),54:(0x2e0,'B'),55:(0x1c8,'B'),56:(0x10,'B')}
class Original:
 def __init__(self,r):
  self.r=r;self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u=self.u;u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc]);self.actor=0x02004000;self.heap=0x02010000;self.query_snapshot=None;self.camera_fixture=True
  def hook(uc,address,size,data):
   ret=None
   if address in [0x0801bc5c,0x0801bc4c]:
    n=uc.reg_read(UC_ARM_REG_R0);ret=self.heap;uc.mem_write(ret,bytes(n));self.heap=(ret+n+3)&~3
   elif address==0x080150d4:ret=256
   elif address==0x080007e0 and self.camera_fixture:ret=1
   elif address in [0x0801501c,0x080052b4]:ret=0
   elif address==0x08013a1a:self.query_snapshot=list(struct.unpack('<4i',uc.mem_read(self.actor+0xa8,16)))
   if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  root=scene_collision(r,0)['root_offset'];u.mem_write(0x02000800,struct.pack('<3I',ROM_BASE+root,3200*256,400*256));u.mem_write(0x02003254,struct.pack('<I',0x02000800))
  for glob,p in [(0x020031e8,0x0200b000),(0x02003264,0x0200b040)]:u.mem_write(glob,struct.pack('<I',p));u.mem_write(p,bytes(0x40))
 def call(self,address,*args):
  u=self.u
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(address|1,0x03001000,count=500000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000,hex(u.reg_read(UC_ARM_REG_PC))
 def ctor(self,definition,xy=(120*256,350*256),flags=0):
  self.heap=0x02010000;u=self.u;u.mem_write(self.actor,bytes(0x1000));u.mem_write(0x02007000,struct.pack('<2i',*xy));u.mem_write(0x02007100,bytes([flags])+bytes(31));u.mem_write(0x0200324c,bytes(4));self.call(0x08013714,self.actor,definition,0x02007000,0x02007100)
  self.sprite=struct.unpack('<I',u.mem_read(self.actor+0x1c0,4))[0];self.component=struct.unpack('<I',u.mem_read(self.actor+0x1bc,4))[0];self.vm=struct.unpack('<I',u.mem_read(self.actor+0x1cc,4))[0]
 def seed(self,s):
  u=self.u
  for i,(off,fmt) in FIELDS.items():u.mem_write(self.actor+off,struct.pack('<'+fmt,s[i]))
  u.mem_write(self.component,struct.pack('<12i',*s[2:14]));u.mem_write(self.sprite,bytes([s[20]&255]));u.mem_write(self.sprite+4,struct.pack('<4i',s[21],s[47],s[22],s[23]));u.mem_write(self.sprite+0x14,struct.pack('<i',s[57]));u.mem_write(self.sprite+0x28,bytes([s[18],s[38]]));u.mem_write(self.actor+0xa8,struct.pack('<4i',*s[14:18]));u.mem_write(self.actor+0x14c,struct.pack('<4i',*s[64:68]))
 def snapshot(self):
  u=self.u;a=self.actor;sp=self.sprite;comp=self.component;anim=struct.unpack('<I',u.mem_read(sp+8,4))[0];raw=u.mem_read(anim,24);x,y,w,h=struct.unpack_from('<hhBB',raw,12)
  out={i:struct.unpack('<'+fmt,u.mem_read(a+off,struct.calcsize(fmt)))[0] for i,(off,fmt) in FIELDS.items()};out.update({i:v for i,v in enumerate(struct.unpack('<12i',u.mem_read(comp,48)),2)});out.update({18:u.mem_read(sp+0x28,1)[0],38:u.mem_read(sp+0x29,1)[0],20:u.mem_read(sp,1)[0],21:struct.unpack('<i',u.mem_read(sp+4,4))[0],22:struct.unpack('<i',u.mem_read(sp+12,4))[0],23:struct.unpack('<i',u.mem_read(sp+16,4))[0],47:anim,57:struct.unpack('<i',u.mem_read(sp+20,4))[0],72:x,73:y,74:w,75:h,76:raw[20],77:raw[21],78:raw[22]});return out
 def message(self,id,payload,tick):
  self.u.mem_write(0x02007200,struct.pack('<3i',8,id,payload));self.u.mem_write(0x0200324c,struct.pack('<i',tick));self.call(0x08013b8c,self.actor,0x02007200)
 def query(self,id):
  self.u.mem_write(0x02007400,struct.pack('<I',0x02007404));self.u.mem_write(0x02007404,struct.pack('<I',0xdeadbeef));self.message(id,0x02007400,0);return struct.unpack('<i',self.u.mem_read(0x02007404,4))[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);o=Original(r);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 @FC
 def fetch(p,out,n,ctx):
  if ROM_BASE<=p<=ROM_BASE+len(r.data)-n*4:raw=r.data[p-ROM_BASE:p-ROM_BASE+n*4]
  elif 0x02000000<=p<=0x02040000-n*4:raw=bytes(o.u.mem_read(p,n*4))
  else:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];msg=lib.s2_generic_message;msg.argtypes=[IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,FC,ctypes.c_void_p];query=lib.s2_generic_query;query.argtypes=[IP,ctypes.c_int,ctypes.c_int,IP]
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['39'];anim=binding['animation'];bank=json.loads((ROOT/'sprites'/binding['bank']/'bank.json').read_text());animations=[ROM_BASE+x['record_offset'] for x in bank['animations']];rng=random.Random(202610);messages=[0,1,3,4,5,6,7,8,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,40,41,42,43,44,45,51,52,53,54];queries=[59,60,61,62,63,64,65,66,67,68,69,70,73,75,76];mc=qc=0
 o.ctor(binding['definition'])
 for id in messages:
  for case in range(128):
   s=(ctypes.c_int32*80)();assert init((ctypes.c_int32*2)(120*256,350*256),case%4,anim,0,fetch,None,s)==0
   for i,(off,fmt) in FIELDS.items():s[i]=rng.randrange(256) if fmt=='B' else rng.randint(-10000,10000)
   for i in range(2,14):s[i]=rng.randint(-5000,5000)
   s[48]=rng.choice(animations);s[49]=rng.randrange(10);s[50]=0 if case%3==0 else rng.choice(animations);s[51]=0 if case%3==0 else rng.choice(animations);s[20]=case%2;s[21]=case%4;s[22]=rng.randrange(24);s[23]=rng.randint(-2000,3000);s[57]=rng.randint(-2000,3000)
   triple=[rng.randint(-5000,5000) for _ in range(3)];o.u.mem_write(0x02007300,struct.pack('<3i',*triple));payload=0x02007300 if id in [21,22,31,42] else (0 if case%3==0 else rng.choice(animations)) if id in [4,5,6,40,41] else rng.randint(-10000,10000);tick=rng.randint(-1000,2000)
   o.seed(s);o.message(id,payload,tick);assert msg(s,8,id,payload,tick,fetch,None)==0
   expected=o.snapshot();diff={i:(s[i],v) for i,v in expected.items() if s[i]!=v};assert not diff,(id,case,payload,diff);mc+=1
 for id in queries:
  for case in range(128):
   s=(ctypes.c_int32*80)();assert init((ctypes.c_int32*2)(120*256,350*256),case%4,anim,0,fetch,None,s)==0
   for i,(off,fmt) in FIELDS.items():s[i]=rng.randrange(256) if fmt=='B' else rng.randint(-10000,10000)
   s[20]=rng.randrange(256)
   for i in [5,11,*range(14,18),*range(64,68)]:s[i]=rng.randint(-5,5)
   o.seed(s);expect=o.query(id);out=(ctypes.c_int32*1)(0x12345678);assert query(s,8,id,out)==0;assert out[0]==expect,(id,case,out[0],expect);qc+=1
 result={'message_cases':mc,'query_cases':qc,'message_ids':messages,'query_ids':queries,'mismatches':0,'original_handler':'0x08013B8C; actual sprite/motion helpers and vtable calls','scope':'Selected generic fields, animation switches/save/restore/null-payload direction gates, motion triples, flags and contact queries. Other classes, registration, global effects and subclass overrides are unsupported.'}
 # Whole generic update: synthetic control programs drive actual ROM sprite data.
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 step=lib.s2_generic_runtime_step;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int];step.restype=ctypes.c_int
 @RC
 def random_value(ctx):return 37
 frames=0;scenarios=[]
 for flips in range(4):
  o.ctor(binding['definition'],flags=flips);s=(ctypes.c_int32*80)();assert init((ctypes.c_int32*2)(120*256,310*256),flips,anim,0,fetch,None,s)==0
  o.u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));o.u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));o.seed(s)
  program=0x02007800;nested=0x02007a00;predicate=0x02007700
  for p,data in [(0x02007600,[0,49,1792]),(0x02007610,[-900,49,1792]),(0x02007620,[256,0,256]),(0x02007630,[0,0,0]),(predicate,[8,64,0,2,1])]:o.u.mem_write(p,struct.pack('<'+'i'*len(data),*data))
  commands=[[8,30,1],[8,22,0x02007600],[5,10,predicate],[8,4,animations[32]],[8,22,0x02007610],[5,8,45],[8,0,1],[8,21,0x02007620],[5,8,50],[8,0,0],[8,21,0x02007630],[5,2,nested],[5,6,0]]
  subcommands=[[8,5,animations[0]],[5,8,20],[8,45,0],[5,6,0]]
  o.u.mem_write(program,b''.join(struct.pack('<3i',*x) for x in commands));o.u.mem_write(nested,b''.join(struct.pack('<3i',*x) for x in subcommands));o.call(0x08013344,o.vm,program);vm=(ctypes.c_int32*64)();start(program,vm)
  for tick in range(1,241):
   o.u.mem_write(0x0200324c,struct.pack('<i',tick));o.u.mem_write(0x020033e0,struct.pack('<i',tick));o.call(0x08018208,o.actor)
   assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,tick,3200*256,400*256,fetch,random_value,None,4096)==0,(flips,tick)
   expected=o.snapshot();diff={i:(s[i],v) for i,v in expected.items() if s[i]!=v};assert not diff,('frame',flips,tick,diff)
   actual_fields={'position':list(s[:2]),'motion':list(s[2:14]),'rect':list(s[32:36]),'previous':list(s[36:38]),'size':list(s[30:32]),'delta':list(s[60:62]),'contacts':list(s[68:72])}
   original_fields={'position':list(struct.unpack('<2i',o.u.mem_read(o.actor+0x178,8))),'motion':list(struct.unpack('<12i',o.u.mem_read(o.component,48))),'rect':list(struct.unpack('<4i',o.u.mem_read(o.actor+0x190,16))),'previous':list(struct.unpack('<2i',o.u.mem_read(o.actor+0x180,8))),'size':list(o.u.mem_read(o.actor+0x174,2)),'delta':list(struct.unpack('<2i',o.u.mem_read(o.actor+0x188,8))),'contacts':o.query_snapshot}
   assert actual_fields==original_fields,('physics',flips,tick,{k:(actual_fields[k],original_fields[k]) for k in actual_fields if actual_fields[k]!=original_fields[k]})
   v=struct.unpack('<4i',o.u.mem_read(o.vm+4,16));assert list(vm[:4])==list(v),('vm',flips,tick,list(vm[:4]),v)
   stack=struct.unpack('<I',o.u.mem_read(o.vm+0x18,4))[0]
   for depth in range(vm[2]+1):
    raw=o.u.mem_read(stack+depth*20,20);expected_frame=[*struct.unpack_from('<2i',raw),raw[8],*struct.unpack_from('<2i',raw,12)];assert list(vm[8+depth*5:13+depth*5])==expected_frame,('stack',flips,tick,depth)
   frames+=1
  scenarios.append({'flips':flips,'ticks':240,'final_position_q8':list(s[:2]),'finished_script':vm[2]==-1})
 # Unsupported routes and missing resources are explicit, not silent no-ops.
 before=list(s);assert msg(s,9,0,0,0,fetch,None)==-4 and list(s)==before
 assert msg(s,8,12,0,0,fetch,None)==-4 and list(s)==before
 assert msg(s,8,22,0,0,fetch,None)==-2 and list(s)==before
 out=(ctypes.c_int32*1)(123);assert query(s,8,72,out)==-4 and out[0]==123
 s[40]|=4;before=list(s);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,241,3200*256,400*256,fetch,random_value,None,4096)==-4 and list(s)==before
 result['native_error_checks']=5
 result['whole_actor_ticks']=frames;result['whole_actor_scenarios']=scenarios;result['whole_actor_scope']='Original 0x18208 runs animation, static physics, original generic message handler, interpreter, grounded motion reset and body changes together. Programs are test fixtures, not original game scripts; allocators and camera visibility are fixtures; no dynamic actors, registered callbacks, overlay, removal or sound.'
 (ROOT/'docs/generic_runtime_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
