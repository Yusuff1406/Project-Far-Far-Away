#!/usr/bin/env python3
"""Original selected entries and state8 dispatch including pending-byte reset."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--landing',action='store_true');ap.add_argument('--attack',action='store_true');ap.add_argument('--air-attack',action='store_true');a=ap.parse_args();o=Original(Rom(a.rom));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202619);binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);actor=o.actor;sp=o.sprite;component=o.component;held=0;originalFx=[];nativeFx=[]
 def hook(uc,addr,size,data):
  if addr==0x08003a2c:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if addr==0x080163ac:
   originalFx.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if addr==0x0800fb2c:uc.reg_write(UC_ARM_REG_R0,0x02007400);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  if addr==0x0800fadc:uc.reg_write(UC_ARM_REG_R0,held);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 packed=(ROOT/'android/app/src/main/assets/campaign/player.s2pm').read_bytes();magic,version,count=struct.unpack_from('<4sII',packed);assert magic==b'S2PM' and version==1;at=12
 for i in range(count):
  address,size=struct.unpack_from('<II',packed,at);at+=8;assert packed[at:at+size]==o.r.data[address-0x08000000:address-0x08000000+size];at+=size
 assert at==len(packed)
 for scene in range(30):assert (ROOT/f'android/app/src/main/assets/campaign/scenes/scene_{scene:02}.s2cl').read_bytes()==(ROOT/f'collision/scene_{scene:02}/scene.s2cl').read_bytes()

 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 enter=lib.s2_shrek_locomotion_enter;enter.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p];behavior=lib.s2_shrek_grab_behavior;behavior.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,ctypes.c_void_p]
 actions={0x158:0x0800f158,0x150:0x0800dcf8,0x160:0x0800f0f8,0x168:0x0800f0e0,0x170:0x0800f0b8,0x1d0:0x0800f00c};table=0x0804c1b4;worldTick=animationTick=0;event=(ctypes.c_int32*3)();s=e=status=book=None
 def seed():
  nonlocal s,e,status,book,held,worldTick,animationTick,event
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();s[0]=120*256;s[1]=350*256;s[30]=16;s[31]=50;s[2:14]=[rng.randint(-10000,10000) for _ in range(12)];s[18]=rng.randrange(2);s[47]=0x0834f454;s[20:24]=[rng.choice([0,1,255]),rng.randrange(3),0,rng.randint(-10000,10000)];s[41:44]=[5,6,7];e[0]=rng.randrange(16);e[1]=0;e[3]=0;status[3]=rng.randrange(256);book[:4]=[0,rng.randint(0,10000),rng.randint(-10000,10000),rng.randint(-10000,10000)];held=rng.choice([0,16,32,48,64,80,96,112] if a.attack or a.air_attack else [0,16,32,48]);worldTick=rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]);animationTick=rng.randint(-10000,10000);event=(ctypes.c_int32*3)(rng.randrange(5),rng.randint(-5,20),rng.randint(-100,100))
  u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x170,struct.pack('<hhBBH',-11,-24,16,50,0));u.mem_write(actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(component,struct.pack('<12i',*s[2:14]));u.mem_write(actor+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(actor+0x228,struct.pack('<3i',*event));u.mem_write(actor+0x1e8,struct.pack('<I',table));u.mem_write(actor+0x1d8,struct.pack('<i',e[0]));u.mem_write(actor+0x258,struct.pack('<i',e[1]));u.mem_write(actor+0x1ec,struct.pack('<i',e[3]));u.mem_write(actor+0x20c,bytes([status[3]]))
  for off,v in zip([0x260,0x25c,0x1dc,0x204],book[:4]):u.mem_write(actor+off,struct.pack('<i',v))
  u.mem_write(sp,bytes([s[20]]));u.mem_write(sp+4,struct.pack('<4i',*([s[21],s[47],s[22],s[23]])));u.mem_write(sp+0x28,bytes([s[18],0]));u.mem_write(0x020033e0,struct.pack('<i',worldTick));u.mem_write(0x0200324c,struct.pack('<i',animationTick))
 def compare(case):
  actual=[list(s[2:14]),s[18],s[47],list(s[20:24]),list(s[41:44]),e[0],e[1],e[3],status[3],list(book[:4])];expected=[list(struct.unpack('<12i',u.mem_read(component,48))),u.mem_read(sp+0x28,1)[0],struct.unpack('<i',u.mem_read(sp+8,4))[0],[u.mem_read(sp,1)[0],struct.unpack('<i',u.mem_read(sp+4,4))[0],*struct.unpack('<2i',u.mem_read(sp+12,8))],list(struct.unpack('<3i',u.mem_read(actor+0x1a0,12))),struct.unpack('<i',u.mem_read(actor+0x1d8,4))[0],struct.unpack('<i',u.mem_read(actor+0x258,4))[0],struct.unpack('<i',u.mem_read(actor+0x1ec,4))[0],u.mem_read(actor+0x20c,1)[0],[struct.unpack('<i',u.mem_read(actor+off,4))[0] for off in [0x260,0x25c,0x1dc,0x204]]];assert actual==expected,(case,actual,expected)
 o.call(0x0800cd0c);descriptor=list(struct.unpack('<5I',u.mem_read(0x02003148,20)));assert descriptor[0]==0x08328308 and descriptor[2]==0x083283e0;assert o.r.data[descriptor[2]-0x08000000+21]-1==4
 ground=lib.s2_donkey_ground_attack;ground.argtypes=[IP,IP,IP,ctypes.c_int32,FC,ctypes.c_void_p]
 terminal=lib.s2_donkey_terminal_enter;terminal.argtypes=[ctypes.c_int,IP,IP,IP,ctypes.c_int32,FC,ctypes.c_void_p]
 for case in range(2000):
  seed();s[19]=rng.randint(0,10000);u.mem_write(actor+0x1e0,struct.pack('<i',s[19]));u.mem_write(actor+0x210,struct.pack('<3i',3,2,0));o.call(0x0800f25c,actor);assert ground(s,e,book,animationTick,fetch,None)==0;compare(('ground-kick',case));assert s[19]==struct.unpack('<i',u.mem_read(actor+0x1e0,4))[0]
 for state,entry in [(12,0x0800f554),(13,0x0800f534),(14,0x0800e168),(15,0x0800e258)]:
  for case in range(1000):
   seed();worldTick=animationTick;u.mem_write(0x020033e0,struct.pack('<i',worldTick));u.mem_write(actor+0x228,struct.pack('<3i',1,7,0));o.call(entry,actor);assert terminal(state,s,e,book,animationTick,fetch,None)==0;compare(('terminal',state,case))
 result=dict(ground_kick_original_cases=2000,terminal_original_cases=4000,states=[12,13,14,15],original_hud_descriptor=descriptor,original_max_health=4,mismatches=0,scope='Original F25C with Donkey table/event and F554/F534/E168/E258. Input/audio/global finish fixtures; carrying and climbing excluded.')
 (ROOT/'docs/donkey_actions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
