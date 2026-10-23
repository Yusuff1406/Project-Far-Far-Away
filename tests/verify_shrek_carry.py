#!/usr/bin/env python3
"""Original carry post-update, detach, removal bitmap and mode-6 contact route."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
DSP=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p)
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
CONSUME=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Rom(args.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202617)
 follow=lib.s2_shrek_carry_follow;follow.argtypes=[IP,IP,IP,IP,ctypes.c_int32,ctypes.c_int32,FC,SINK,DSP,ctypes.c_void_p];release=lib.s2_shrek_carry_release;release.argtypes=[IP,IP,ctypes.c_int32,IP,DSP,ctypes.c_void_p];mark=lib.s2_actor_mark_removed;mark.argtypes=[IP,ctypes.c_int32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];o.ctor(bindings['18']['definition']);target=o.actor;targetSprite=o.sprite;targetVm=o.vm;targetStack=struct.unpack('<I',u.mem_read(targetVm+0x14,4))[0];source=0x02005000;sourceSprite=0x0200e000;maskAddress=0x02007800;maskGlobal=struct.unpack_from('<I',rom.data,0x9ce0)[0];u.mem_write(maskGlobal,struct.pack('<I',maskAddress))
 originalFx=[];nativeFx=[];originalMessages=[];nativeMessages=[];held=0
 def hook(uc,address,size,data):
  ret=None
  if address in [0x0800f7d0,0x0800fa4c]:ret=0 # player base update / player-only sound condition
  elif address==0x0800fadc:ret=held
  elif address==0x080163ac:originalFx.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);ret=0
  elif address==0x08013a54:originalMessages.append([uc.reg_read(UC_ARM_REG_R0),*struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12))])
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 @SINK
 def sink(kind,resource,scale,ctx):nativeFx.append([kind,resource,scale]);return 0
 def seed_pose(addr,sprite,s,vt):
  u.mem_write(addr,struct.pack('<I',vt));u.mem_write(addr+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(addr+0x178,struct.pack('<2i',*s[:2]));u.mem_write(addr+0x15c,bytes([s[40]]));u.mem_write(addr+8,struct.pack('<2i',*s[28:30]));u.mem_write(addr+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(addr+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite,bytes([s[20]&255]));u.mem_write(sprite+4,struct.pack('<4i',s[21],s[47],s[22],s[23]));u.mem_write(sprite+0x28,bytes([s[18],s[38]]))
 def seed_player(e,status,carryPtr,tick,animTick):
  for off,value in [(0x1d8,e[0]),(0x258,e[1]),(0x1ec,carryPtr if e[3] else 0),(0x1d0,status[4]),(0x208,status[6])]:u.mem_write(source+off,struct.pack('<i',value))
  u.mem_write(source+0x1c8,bytes([status[5]]));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',animTick));u.mem_write(0x02007400,bytes([e[2]&255])+bytes(15))
 def seed_vm(addr,vmAddr,stack,v,r):
  u.mem_write(addr+0x250,struct.pack('<i',r[0]));u.mem_write(addr+0x1d0,struct.pack('<'+'i'*(r[0]*2),*r[8:8+r[0]*2]));u.mem_write(addr+0x254,bytes([r[2]]));u.mem_write(addr+0x2a0,struct.pack('<2i',*r[3:5]));u.mem_write(vmAddr+4,struct.pack('<4i',*v[:4]));u.mem_write(vmAddr+0x14,struct.pack('<I',stack));u.mem_write(stack,struct.pack('<5i',*v[8:13]))
 def compare_vm(addr,vmAddr,stack,v,r):
  assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(vmAddr+4,16)));assert [r[2],r[3],r[4]]==[u.mem_read(addr+0x254,1)[0],*struct.unpack('<2i',u.mem_read(addr+0x2a0,8))]
  for d in range(v[2]+1):
   frame=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));frame[2]&=255;assert list(v[8+d*5:13+d*5])==frame
 # Input pointer is supplied, but the original E9EC animation decisions run.
 def input_hook(uc,address,size,data):
  if address==0x0800fb2c:uc.reg_write(UC_ARM_REG_R0,0x02007400);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,input_hook)
 followCases=5000;throws=animationChanges=fxCount=0
 for case in range(followCases):
  ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();start(0x08052c28,v);r[0]=1;r[8:10]=[29,0x080531fc];r[2]=case%3==0
  for s in [ss,ts]:
   s[0]=rng.choice([-2147483648,2147483647,rng.randint(-100000,100000)]);s[1]=rng.choice([-2147483648,2147483647,rng.randint(-100000,100000)]);s[30]=rng.randrange(256);s[31]=rng.randrange(256);s[18]=rng.randrange(2);s[47]=bindings['18']['animation'];s[20]=rng.randrange(2);s[21]=rng.randrange(4);s[22]=0;s[23]=rng.randint(-10000,10000)
  ts[47]=rng.choice([0x08342dcc,0x08342db4,bindings['18']['animation']]);oldAnimation=ts[47];e[0]=8;e[1]=rng.choice(list(range(10))+[-1]);e[2]=rng.choice([0,2]);e[3]=0 if case%11==0 else 123;status[5]=rng.randrange(256);status[6]=rng.randint(-10000,10000);tick=rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]);animTick=rng.randint(-10000,10000)
  seed_pose(source,sourceSprite,ss,0x020017cc);seed_pose(target,targetSprite,ts,0x0200268c);seed_player(e,status,target,tick,animTick);seed_vm(target,targetVm,targetStack,v,r);originalFx.clear();nativeFx.clear();originalMessages.clear();nativeMessages.clear()
  @DSP
  def dispatch(ident,event,ctx):nativeMessages.append([target,*event[:3]]);assert ident==123;activate(v,r,event);return 0
  o.call(0x0800d484,source);assert follow(ss,e,status,ts,tick,animTick,fetch,sink,dispatch,None)==0
  expectedCarry=123 if struct.unpack('<I',u.mem_read(source+0x1ec,4))[0] else 0
  actual=[list(ts[:2]),ts[18],ts[47],list(ts[20:24]),e[1],e[3],status[5],status[6]];expected=[list(struct.unpack('<2i',u.mem_read(target+0x178,8))),u.mem_read(targetSprite+0x28,1)[0],struct.unpack('<i',u.mem_read(targetSprite+8,4))[0],[u.mem_read(targetSprite,1)[0],struct.unpack('<i',u.mem_read(targetSprite+4,4))[0],*struct.unpack('<2i',u.mem_read(targetSprite+12,8))],struct.unpack('<i',u.mem_read(source+0x258,4))[0],expectedCarry,u.mem_read(source+0x1c8,1)[0],struct.unpack('<i',u.mem_read(source+0x208,4))[0]];assert actual==expected,(case,actual,expected);assert nativeFx==originalFx;assert nativeMessages==originalMessages;compare_vm(target,targetVm,targetStack,v,r);throws+=bool(nativeMessages);animationChanges+=ts[47]!=oldAnimation;fxCount+=len(nativeFx)
 detachCases=4000;detachEvent=(ctypes.c_int32*3)()
 for case in range(detachCases):
  e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();start(0x08052c28,v);r[0]=2;r[8:12]=[11,0x080531fc,29,0x08053240];r[2]=case%3==0;e[1]=rng.choice(list(range(10))+[-1,-2147483648]);e[3]=123 if case%4 else 0;status[4]=rng.randint(-10000,10000);status[5]=rng.randrange(256);tick=rng.choice([-2147483648,2147483647,rng.randint(-10000,10000)]);detachEvent[:]=[rng.randrange(5),rng.choice([0,11,29]),rng.randint(-500,500)];seed_player(e,status,target,tick,0);seed_vm(target,targetVm,targetStack,v,r);u.mem_write(source+0x234,struct.pack('<3i',*detachEvent));originalMessages.clear();nativeMessages.clear()
  @DSP
  def dispatch(ident,event,ctx):nativeMessages.append([target,*event[:3]]);assert ident==123;activate(v,r,event);return 0
  o.call(0x0800dc5c,source);assert release(e,status,tick,detachEvent,dispatch,None)==0;assert nativeMessages==originalMessages;assert [e[1],e[3],status[4],status[5]]==[struct.unpack('<i',u.mem_read(source+0x258,4))[0],123 if struct.unpack('<I',u.mem_read(source+0x1ec,4))[0] else 0,struct.unpack('<i',u.mem_read(source+0x1d0,4))[0],u.mem_read(source+0x1c8,1)[0]];compare_vm(target,targetVm,targetStack,v,r)
 removalCases=2000
 for case in range(removalCases):
  state=(ctypes.c_int32*80)();state[40]=rng.randrange(256);ident=rng.randrange(-3,256);words=[rng.getrandbits(32) for _ in range(8)];mask=(ctypes.c_uint32*8)(*words);u.mem_write(target+0x15c,bytes([state[40]]));u.mem_write(target+0x160,struct.pack('<i',ident));u.mem_write(maskAddress,struct.pack('<8I',*words));o.call(0x08005168,target);assert mark(state,ident,mask,8)==0;assert state[40]==u.mem_read(target+0x15c,1)[0];assert list(mask)==list(struct.unpack('<8I',u.mem_read(maskAddress,32)))
 # Marking must feed the existing scene-spawn suppression bitmap directly.
 spawn=lib.s2_scene_spawn_plan_file;spawn.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP,ctypes.c_size_t];suppression=0
 for scene in range(30):
  records=json.loads((ROOT/f'objects/scene_{scene:02d}/objects.json').read_text())['objects'];n=len(records)
  for ident in sorted({1,(n+1)//2,n}) if n else []:
   mask=(ctypes.c_uint32*((n+32)//32))();state=(ctypes.c_int32*80)();assert mark(state,ident,mask,len(mask))==0;out=(ctypes.c_int32*(n*8))();assert spawn(str(ROOT/f'objects/scene_{scene:02d}/scene.s2ob').encode(),mask,len(mask),out,n)==n-1;assert set(out[i*8] for i in range(n-1))==set(range(1,n+1))-{ident};suppression+=1
 state=(ctypes.c_int32*80)();state[40]=8;mask=(ctypes.c_uint32*8)();assert mark(state,256,mask,8)==-1 and state[40]==8 and not any(mask)
 assert throws>0 and animationChanges>0 and fxCount>0
 result={'original_post_update_entry':'0x0800D484','post_update_cases':followCases,'carried_animation_switches':animationChanges,'throw_event_cases':throws,'flashing_sound_requests':fxCount,'original_detach_cases':detachCases,'original_removal_bitmap_cases':removalCases,'native_spawn_suppression_checks':suppression,'native_bitmap_bounds_refusals':1,'mismatches':0,'scope':'Original D484 carry tail, E9EC animation switching/EA98 throw, DC5C detach, 5168/9CC0 removal bitmap. Base player F7D0 update and player-only sound condition are fixtures; carried target uses its real sprite virtual flip setter and generic reaction/VM handler. Input getter and low-level audio delivery are fixtures. Full carry target subclasses, player entry FSM, world lifetime/destructors and Android execution remain separate.'};(ROOT/'docs/shrek_carry_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
