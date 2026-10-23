#!/usr/bin/env python3
"""Original E788 mode-6 contact -> removal of carried actor -> DC5C detach."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
from verify_shrek_carry import DSP,CONSUME
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(172026)
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);carried=0x02006000;u.mem_write(carried,bytes(u.mem_read(o.actor,0x1000)));carriedSprite=o.sprite;carriedVm=o.vm;carriedStack=struct.unpack('<I',u.mem_read(carriedVm+0x14,4))[0]
 # Allocate another generic target without reusing the carried actor's heap.
 o.call(0x08013714,o.actor,binding['definition'],0x02007000,0x02007100);target=o.actor;targetSprite=struct.unpack('<I',u.mem_read(target+0x1c0,4))[0];targetVm=struct.unpack('<I',u.mem_read(target+0x1cc,4))[0];targetStack=struct.unpack('<I',u.mem_read(targetVm+0x14,4))[0];source=0x02005000;sourceSprite=0x0200e000;maskAddress=0x02007800;u.mem_write(struct.unpack_from('<I',rom.data,0x9ce0)[0],struct.pack('<I',maskAddress));o.camera_fixture=False
 pair=lib.s2_shrek_contact_pair_carry;pair.argtypes=[IP,IP,ctypes.c_int32,ctypes.c_uint32,ctypes.c_int,IP,IP,IP,FC,ctypes.c_void_p,IP,CONSUME,IP];mark=lib.s2_actor_mark_removed;mark.argtypes=[IP,ctypes.c_int32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t];release=lib.s2_shrek_carry_release;release.argtypes=[IP,IP,ctypes.c_int32,IP,DSP,ctypes.c_void_p];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 held=0;originalOrder=[]
 def hook(uc,address,size,data):
  if address==0x0800fadc:uc.reg_write(UC_ARM_REG_R0,held);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif address==0x08005168:
   assert uc.reg_read(UC_ARM_REG_R0)==carried;originalOrder.append(['mark',u.mem_read(carried+0x15c,1)[0],(struct.unpack('<I',u.mem_read(maskAddress+8,4))[0]>>13)&1,struct.unpack('<i',u.mem_read(source+0x258,4))[0]])
  elif address==0x08013a54 and uc.reg_read(UC_ARM_REG_R0)==carried:
   originalOrder.append(['detach',u.mem_read(carried+0x15c,1)[0],(struct.unpack('<I',u.mem_read(maskAddress+8,4))[0]>>13)&1,struct.unpack('<i',u.mem_read(source+0x258,4))[0],*struct.unpack('<3i',u.mem_read(uc.reg_read(UC_ARM_REG_R1),12))])
 u.hook_add(UC_HOOK_CODE,hook)
 def seed(addr,sprite,s,vt):
  u.mem_write(addr,struct.pack('<I',vt));u.mem_write(addr+0x15c,bytes([s[40]]));u.mem_write(addr+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(addr+0x178,struct.pack('<2i',*s[:2]));u.mem_write(addr+8,struct.pack('<2i',*s[28:30]));u.mem_write(addr+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(addr+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite+8,struct.pack('<2i',s[47],s[22]));u.mem_write(sprite+0x28,bytes([s[18],s[38]]))
 def vm_seed(addr,vm,stack,v,r):
  u.mem_write(addr+0x250,struct.pack('<i',r[0]));u.mem_write(addr+0x1d0,struct.pack('<'+'i'*(2*r[0]),*r[8:8+2*r[0]]));u.mem_write(addr+0x254,bytes([r[2]]));u.mem_write(addr+0x2a0,bytes(8));u.mem_write(vm+4,struct.pack('<4i',*v[:4]));u.mem_write(vm+0x14,struct.pack('<I',stack));u.mem_write(stack,struct.pack('<5i',*v[8:13]))
 def compare(addr,vm,stack,v,r):
  assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(vm+4,16)));assert [r[2],r[3],r[4]]==[u.mem_read(addr+0x254,1)[0],*struct.unpack('<2i',u.mem_read(addr+0x2a0,8))]
  for depth in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+depth*20,20)));f[2]&=255;assert list(v[8+depth*5:13+depth*5])==f
 cases=2000;consumed=expandedHits=0;defaultDetach=(ctypes.c_int32*3)(0,11,0)
 for case in range(cases):
  ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();cs=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();cv=(ctypes.c_int32*64)();cr=(ctypes.c_int32*72)();mask=(ctypes.c_uint32*8)();start(0x08052c28,v);start(0x08052c28,cv);r[0]=2;r[8:12]=[15,0x080531fc,8,0x08053240];r[2]=case%4==0;cr[0]=1;cr[8:10]=[11,0x080531fc];cr[2]=case%3==0
  ss[0]=rng.randint(-100000,100000);ss[1]=rng.randint(-100000,100000);ss[30]=16;ss[31]=50;ss[40]=rng.choice([0,8,16,24]);ss[47]=0x0834f25c;ss[22]=0;ss[41:44]=[1,0,0];ts[0]=ss[0]+rng.randint(-6000,6000);ts[1]=ss[1]+rng.randint(-10000,10000);ts[30]=rng.randint(4,32);ts[31]=rng.randint(4,40);ts[40]=rng.choice([0,8]);ts[47]=binding['animation'];ts[22]=0;ts[28:30]=[19,-17];cs[40]=rng.randrange(256);e[0]=8;e[1]=6;e[2]=rng.choice([0,16,32,48]);e[3]=77;e[4:7]=[0,rng.choice([0,8]),0];dy=rng.choice([-256,0,256,4096]);status[4]=rng.randint(-10000,10000);status[5]=rng.randrange(256);tick=rng.randint(-10000,10000);held=e[2]
  seed(source,sourceSprite,ss,0x020017cc);seed(target,targetSprite,ts,0x0200268c);u.mem_write(carried+0x15c,bytes([cs[40]]));u.mem_write(carried+0x160,struct.pack('<i',77));u.mem_write(source+0x1d8,struct.pack('<i',e[0]));u.mem_write(source+0x258,struct.pack('<i',6));u.mem_write(source+0x1ec,struct.pack('<I',carried));u.mem_write(source+0x18c,struct.pack('<i',dy));u.mem_write(source+0x21c,struct.pack('<3i',*e[4:7]));u.mem_write(source+0x234,struct.pack('<3i',*defaultDetach));u.mem_write(source+0x1d0,struct.pack('<i',status[4]));u.mem_write(source+0x1c8,bytes([status[5]]));u.mem_write(target+0x168,struct.pack('<i',3));u.mem_write(maskAddress,bytes(32));u.mem_write(0x020033e0,struct.pack('<i',tick));vm_seed(target,targetVm,targetStack,v,r);vm_seed(carried,carriedVm,carriedStack,cv,cr);originalOrder.clear();nativeOrder=[]
  @DSP
  def dispatch(ident,event,ctx):
   assert ident==77;nativeOrder.append(['detach',cs[40],(mask[2]>>13)&1,e[1],*event[:3]]);activate(cv,cr,event);return 0
  @CONSUME
  def consume(ctx):
   nativeOrder.append(['mark',cs[40],(mask[2]>>13)&1,e[1]]);assert mark(cs,77,mask,8)==0;return release(e,status,tick,defaultDetach,dispatch,None)
  o.call(0x0800e788,source,target);diag=(ctypes.c_int32*8)();d=(ctypes.c_int32*2)();assert pair(ss,e,dy,123,3,ts,v,r,fetch,None,diag,consume,d)==0
  assert nativeOrder==originalOrder,(case,nativeOrder,originalOrder);assert [ss[40],ss[43],e[1],e[3],list(ts[28:30]),cs[40],list(mask)]==[u.mem_read(source+0x15c,1)[0],struct.unpack('<i',u.mem_read(source+0x1a8,4))[0],struct.unpack('<i',u.mem_read(source+0x258,4))[0],77 if struct.unpack('<I',u.mem_read(source+0x1ec,4))[0] else 0,list(struct.unpack('<2i',u.mem_read(target+8,8))),u.mem_read(carried+0x15c,1)[0],list(struct.unpack('<8I',u.mem_read(maskAddress,32)))];compare(target,targetVm,targetStack,v,r);compare(carried,carriedVm,carriedStack,cv,cr);expandedHits+=d[0];consumed+=d[1]
 assert expandedHits>consumed>0
 result={'cases':cases,'expanded_body_hits':expandedHits,'consumed_carried_actors':consumed,'mismatches':0,'scope':'Original full E788 category-3/mode-6 route including expanded body hit query, target event15, carried actor 5168 bitmap mark and DC5C event11 detach, followed by side and falling-strip queries. Two stable generic target actors with supplied listeners; held-input getter fixture. Actor destruction/unregistration, true target subclasses and full world scheduling remain separate.'};(ROOT/'docs/shrek_consume_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
