#!/usr/bin/env python3
"""Original selected entries and state8 dispatch including pending-byte reset."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--fire',action='store_true');ap.add_argument('--landing',action='store_true');ap.add_argument('--donkey',action='store_true');ap.add_argument('--attack',action='store_true');ap.add_argument('--air-attack',action='store_true');a=ap.parse_args();nativeTable=0x0804c1b4 if a.donkey else 0x0804b73c;o=Original(Rom(a.rom));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202619);binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);actor=o.actor;sp=o.sprite;component=o.component;held=0;originalFx=[];nativeFx=[]
 def hook(uc,addr,size,data):
  if addr==0x080163ac:
   originalFx.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if addr==0x0800fb2c:uc.reg_write(UC_ARM_REG_R0,0x02007400);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if addr==0x0800fadc:uc.reg_write(UC_ARM_REG_R0,held);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 enter=lib.s2_shrek_locomotion_enter;enter.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p];behavior=lib.s2_shrek_grab_behavior;behavior.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p]
 actions={0x158:0x0800f158,0x150:0x0800dcf8,0x160:0x0800f0f8,0x168:0x0800f0e0,0x170:0x0800f0b8,0x1d0:0x0800f00c};worldTick=animationTick=0;event=(ctypes.c_int32*3)();s=e=status=book=None
 def seed():
  nonlocal s,e,status,book,held,worldTick,animationTick,event
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();s[0]=120*256;s[1]=350*256;s[30]=16;s[31]=50;s[2:14]=[rng.randint(-10000,10000) for _ in range(12)];s[18]=rng.randrange(2);s[47]=0x0834f454;s[20:24]=[rng.choice([0,1,255]),rng.randrange(3),0,rng.randint(-10000,10000)];s[41:44]=[5,6,7];e[0]=rng.randrange(16);e[1]=rng.choice(list(range(8))+[-1]);e[3]=rng.choice([0,77,88]);status[3]=rng.randrange(256);book[:4]=[0,rng.randint(0,10000),rng.randint(-10000,10000),rng.randint(-10000,10000)];held=rng.choice([0,16,32,48,64,80,96,112] if a.attack or a.air_attack else [0,16,32,48]);worldTick=rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]);animationTick=rng.randint(-10000,10000);event=(ctypes.c_int32*3)(rng.randrange(5),rng.randint(-5,20),rng.randint(-100,100))
  u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x170,struct.pack('<hhBBH',-11,-24,16,50,0));u.mem_write(actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(component,struct.pack('<12i',*s[2:14]));u.mem_write(actor+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(actor+0x228,struct.pack('<3i',*event));u.mem_write(actor+0x1e8,struct.pack('<I',nativeTable-40));u.mem_write(actor+0x1d8,struct.pack('<i',e[0]));u.mem_write(actor+0x258,struct.pack('<i',e[1]));u.mem_write(actor+0x1ec,struct.pack('<i',e[3]));u.mem_write(actor+0x20c,bytes([status[3]]))
  for off,v in zip([0x260,0x25c,0x1dc,0x204],book[:4]):u.mem_write(actor+off,struct.pack('<i',v))
  u.mem_write(sp,bytes([s[20]]));u.mem_write(sp+4,struct.pack('<4i',*([s[21],s[47],s[22],s[23]])));u.mem_write(sp+0x28,bytes([s[18],0]));u.mem_write(0x020033e0,struct.pack('<i',worldTick));u.mem_write(0x0200324c,struct.pack('<i',animationTick))
 def compare(case):
  actual=[list(s[2:14]),s[18],s[47],list(s[20:24]),list(s[41:44]),e[0],e[1],e[3],status[3],list(book[:4])];expected=[list(struct.unpack('<12i',u.mem_read(component,48))),u.mem_read(sp+0x28,1)[0],struct.unpack('<i',u.mem_read(sp+8,4))[0],[u.mem_read(sp,1)[0],struct.unpack('<i',u.mem_read(sp+4,4))[0],*struct.unpack('<2i',u.mem_read(sp+12,8))],list(struct.unpack('<3i',u.mem_read(actor+0x1a0,12))),struct.unpack('<i',u.mem_read(actor+0x1d8,4))[0],struct.unpack('<i',u.mem_read(actor+0x258,4))[0],struct.unpack('<i',u.mem_read(actor+0x1ec,4))[0],u.mem_read(actor+0x20c,1)[0],[struct.unpack('<i',u.mem_read(actor+off,4))[0] for off in [0x260,0x25c,0x1dc,0x204]]];assert actual==expected,(case,actual,expected)
 if a.fire:
  fire=lib.s2_shrek_fire_enter;fire.argtypes=[IP,IP,IP,ctypes.c_int32,FC,ctypes.c_void_p]
  for case in range(160):
   seed();o.call(0x0800e258,actor);assert fire(s,e,book,animationTick,fetch,None)==0;compare(('fire',case))
  report=dict(source_fire_entries=160,mismatches=0,device_tested=False);(ROOT/'docs/shrek_fire_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report);return
 if a.landing:
  SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
  @SINK
  def sink(kind,address,scale,ctx):nativeFx.append([kind,address,scale]);return 0
  landing=lib.s2_shrek_landing_enter;landing.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,ctypes.c_void_p]
  clear=lib.s2_shrek_clear_contact_event;clear.argtypes=[IP]
  soundCases=0;boundaryCases=0
  for case in range(6000):
   seed();book[3]=rng.choice([-2147483648,2147483647,rng.randint(-100000,100000)])
   distance=rng.choice([25599,25600,25601,-1,0,2147483647,-2147483648,rng.randint(-100000,100000)])
   s[1]=ctypes.c_int32(book[3]+distance).value
   u.mem_write(actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(actor+0x204,struct.pack('<i',book[3]));originalFx.clear();nativeFx.clear()
   o.call(0x0800f030,actor)
   assert landing(s,e,book,held,animationTick,nativeTable,0x0804b708,fetch,sink,None)==0
   compare(('landing',case));assert originalFx==nativeFx,(case,originalFx,nativeFx)
   assert bool(nativeFx)==(distance>25600);soundCases+=bool(nativeFx);boundaryCases+=distance in [25599,25600,25601]
  for case in range(2000):
   seed();s[41:44]=[rng.randint(-2147483648,2147483647) for _ in range(3)];before=list(s);u.mem_write(actor+0x1a0,struct.pack('<3i',*s[41:44]));o.call(0x0800f600,actor);assert clear(s)==0
   assert list(s[41:44])==list(struct.unpack('<3i',u.mem_read(actor+0x1a0,12)));before[42]=0;assert list(s)==before
  descriptor=struct.unpack_from('<I',o.r.data,nativeTable-0x08000000+5*40+36)[0];soundId=struct.unpack_from('<i',o.r.data,descriptor-0x08000000)[0];assert soundId==(19 if a.donkey else 93)
  result={'hero':'Donkey'if a.donkey else'Shrek','native_motion_base':hex(nativeTable),'original_motion_base':hex(nativeTable-40),'heavy_landing_sound_id':soundId,'heavy_landing_descriptor':hex(descriptor),'landing_original_cases':6000,'heavy_landing_sound_requests':soundCases,'threshold_boundary_cases':boundaryCases,'clear_contact_event_original_cases':2000,'mismatches':0,'scope':'Original F030 landing entry and F600 event-ID clear. Real animation/motion helpers; held getter and low-level sound delivery are fixtures. This isolated harness excludes integrated world frames and Android execution.'}
  (ROOT/('docs/donkey_landing_validation.json'if a.donkey else'docs/shrek_landing_validation.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
 if a.air_attack:
  SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
  @SINK
  def sink(kind,address,scale,ctx):nativeFx.append([kind,address,scale]);return 0
  air=lib.s2_shrek_air_attack_behavior;air.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,SINK,ctypes.c_void_p]
  for case in range(6000):
   seed();u.mem_write(0x02007400,bytes([held])+bytes(15));o.call(0x0800d1b8,actor);action=0x10009 if held&64 else 0x10008
   assert enter(s,e,status,book,action,held,worldTick,animationTick,nativeTable,event,fetch,None)==0;compare(('air-entry',case))
  exits={};pulseCases=0
  for case in range(6000):
   seed();e[0]=16;s[47]=rng.choice([0x0834f304,0x0834f31c]);s[22]=rng.randrange(6);s[61]=rng.choice([-2147483648,2147483647,-699,-698,-697,-1,0,1,rng.randint(-2000,2000)]);s[14]=rng.randrange(3);s[64]=rng.randrange(3)
   u.mem_write(actor+0x1d8,struct.pack('<i',16));u.mem_write(actor+0x18c,struct.pack('<i',s[61]));u.mem_write(actor+0xa8,struct.pack('<4i',s[14],0,0,0));u.mem_write(actor+0x14c,struct.pack('<4i',s[64],0,0,0));u.mem_write(sp+8,struct.pack('<2i',s[47],s[22]));originalFx.clear();nativeFx.clear()
   pulseCases+=ctypes.c_int32(s[23]-animationTick).value<=1;o.call(0x0800d1e8,actor)
   assert air(s,e,status,book,held,worldTick,animationTick,nativeTable,event,fetch,sink,None)==0;compare(('air-behavior',case));assert originalFx==nativeFx;exits[e[0]]=exits.get(e[0],0)+1
  result={'air_attack_entry_cases':6000,'original_D1E8_state16_cases':6000,'pulse_metadata_checks':pulseCases,'final_states':exits,'mismatches':0,'scope':'Original D1B8 and D1E8 -> CF8C for ogre animations8/9; real motion/animation helpers, input and audio delivery fixtures. Delta-Y thresholds and pending-byte preservation checked. Ogre frame spawn-marker is zero; projectile-bearing other forms, carry attacks and enemy damage excluded.'};(ROOT/'docs/shrek_air_attack_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
 if a.attack:
  for case in range(6000):
   seed();u.mem_write(0x02007400,bytes([held])+bytes(15))
   o.call(0x0800d170,actor);assert enter(s,e,status,book,0x188,held,worldTick,animationTick,nativeTable,event,fetch,None)==0;compare(('attack-entry',case))
  attack=lib.s2_shrek_attack_behavior;attack.argtypes=behavior.argtypes
  for case in range(5000):
   seed();e[0]=7;u.mem_write(actor+0x1d8,struct.pack('<i',7));o.call(0x0800d5e0,actor);assert attack(s,e,status,book,held,worldTick,animationTick,nativeTable,event,fetch,None)==0;compare(('attack-behavior',case))
  result={'ground_attack_entry_cases':6000,'original_state7_dispatch_cases':5000,'mismatches':0,'scope':'Original D170 ground attack and D5E0 state7 -> F2BC, real animation/motion helpers, input getter fixture. Incoming damage, air state16 and carry attacks excluded.'};(ROOT/'docs/shrek_attack_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
 counts={}
 for action,entry in actions.items():
  for case in range(1000):
   seed();o.call(entry,actor);assert enter(s,e,status,book,action,held,worldTick,animationTick,nativeTable,event,fetch,None)==0;compare((hex(action),case))
  counts[hex(action)]=1000
 exits=waiting=0
 for case in range(5000):
  seed();e[0]=8;u.mem_write(actor+0x1d8,struct.pack('<i',8));shouldExit=bool(s[20] and (not e[3] or e[1]!=0));o.call(0x0800d5e0,actor);assert behavior(s,e,status,book,held,worldTick,animationTick,nativeTable,event,fetch,None)==0;compare(('state8',case));exits+=shouldExit;waiting+=not shouldExit
 result={'selected_entry_cases':6000,'cases_by_slot':counts,'state8_original_dispatch_cases':5000,'automatic_idle_exits':exits,'waiting_cases':waiting,'mismatches':0,'scope':'Original F158/DCF8/F0F8/F0E0/F0B8/F00C entries and D5E0 state8 -> actual vtable110 F1E4 dispatch, idle special pending byte and its post-behavior reset. Real sprite virtual flip and animation/motion helpers execute; held getter is a stable fixture. Canonical motion table; no full world update, landing audio, other behavior states, object lifetime or Android execution.'};(ROOT/'docs/shrek_locomotion_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
