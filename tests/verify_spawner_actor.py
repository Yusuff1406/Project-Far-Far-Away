#!/usr/bin/env python3
"""Type46 constructor, spawn gate/notices/counters against original Thumb."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(47);made=False;requests=[]
 def hook(uc,a,size,data):
  ret=None
  if a==0x080059d8:requests.append(uc.reg_read(UC_ARM_REG_R0));ret=0x02009000 if made else 0
  elif a in [0x08007ac4,0x08018208]:ret=0
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 init=lib.s2_spawner_init;init.argtypes=[IP,IP]
 gate=lib.s2_spawner_can_create;gate.argtypes=[IP]
 notice=lib.s2_spawner_notice;notice.argtypes=[IP,ctypes.c_int32,IP]
 created=lib.s2_spawner_created;created.argtypes=[IP]
 tagger=lib.s2_spawner_tag;tagger.argtypes=[ctypes.c_int32,ctypes.c_int32];tagger.restype=ctypes.c_int32
 def put(off,v):u.mem_write(o.actor+off,struct.pack('<i',ctypes.c_int32(v).value))
 def capture():return [*struct.unpack('<4i',u.mem_read(o.actor+0x2e4,16)),u.mem_read(o.actor+0x2f8,1)[0],u.mem_read(o.actor+0x2f9,1)[0],struct.unpack('<i',u.mem_read(o.actor+0x2fc,4))[0],0]
 def seed(s):
  for off,v in zip([0x2e4,0x2e8,0x2ec,0x2f0],s[:4]):put(off,v)
  u.mem_write(o.actor+0x2f8,bytes([s[4],s[5]]));put(0x2fc,s[6])
 for i in range(1000):
  params=(ctypes.c_int32*8)(rng.randrange(256),0,0,90,rng.choice([0,1,5,-1,2147483647]),rng.randrange(-100000,100000),0,rng.choice([0,1,999,-1,2147483647]))
  o.ctor(0x0804db20);u.mem_write(0x02007100,struct.pack('<8i',*params));o.call(0x0801b4a0,o.actor,0x0804db20,0x02007000,0x02007100)
  s=(ctypes.c_int32*8)();assert init(params,s)==0;assert list(s)==capture(),(i,list(s),capture())
 assert struct.unpack('<I',u.mem_read(o.actor,4))[0]==0x02002ce4
 for i in range(4000):
  s=(ctypes.c_int32*8)(*[rng.choice([-2147483648,-1,0,1,5,999,2147483647,rng.randrange(-10000,10000)])for _ in range(4)],rng.randrange(256),rng.randrange(256),0,0)
  seed(s);o.call(0x0801b438,o.actor);assert gate(s)==u.reg_read(UC_ARM_REG_R0),(i,list(s))
 for i in range(5000):
  s=(ctypes.c_int32*8)(5,999,rng.randrange(-100,100),rng.randrange(-100,100),rng.choice([0,1,255]),rng.choice([0,1,255]),0,0);tag=rng.choice([0,31,1031,2147483647,-2147483648]);payload=ctypes.c_int32(tag+1000+rng.choice([0,0,1,-1])).value;seed(s);put(0x164,tag);event=(ctypes.c_int32*3)(9,4,payload);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x0801b350,o.actor,0x02007200);assert notice(s,tag,event)>=0;assert list(s)==capture(),(i,list(s),capture())
 for i in range(2000):
  s=(ctypes.c_int32*8)(rng.choice([0,1,5]),rng.choice([0,1,999]),rng.randrange(-1,6),rng.randrange(-1,6),i%2,0,rng.choice([0,53,57]),0);made=bool(i%3);seed(s);put(0x164,1031);u.mem_write(0x02007300,struct.pack('<5i',53,1,0,0,0));requests.clear();allowed=gate(s);o.call(0x0801b3bc,o.actor,0x02007300)
  assert requests==([s[6]or 53]if allowed else []),(i,requests,list(s))
  if allowed and made:assert created(s)==0;assert struct.unpack('<i',u.mem_read(0x02009164,4))[0]==2031
  assert list(s)==capture(),(i,list(s),capture())
 for i in range(1000):
  tag=rng.choice([0,1,-1,2147483647]);ident=rng.choice([31,-2147483648,2147483647]);put(0x164,tag);put(0x160,ident);o.call(0x0801b478,o.actor);assert tagger(tag,ident)==struct.unpack('<i',u.mem_read(o.actor+0x164,4))[0]
 report={'constructor_cases':1000,'gate_cases':4000,'notice_cases':5000,'factory_counter_cases':2000,'tag_update_cases':1000,'mismatches':0,'scope':'Original1B4A0/1B438/1B350/1B3BC/1B478. Factory allocation/registration and base update are explicit fixtures; original subtype gate, override, child tag and success-only counters execute. Full script and native scene checked separately.'}
 (ROOT/'docs/spawner_actor_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
