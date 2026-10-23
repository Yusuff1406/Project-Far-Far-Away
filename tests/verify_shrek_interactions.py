#!/usr/bin/env python3
"""Run original E788/EBC0 and compare selected stable generic-target routes."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom,ROM_BASE
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();o=Original(Rom(args.rom));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202615)
 pair=lib.s2_shrek_contact_pair;pair.argtypes=[IP,IP,ctypes.c_int32,ctypes.c_uint32,ctypes.c_int,IP,IP,IP,FC,ctypes.c_void_p,IP]
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 held=0
 def hook(uc,address,size,data):
  if address==0x0800fadc:uc.reg_write(UC_ARM_REG_R0,held);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);target=o.actor;targetSprite=o.sprite;source=0x02005000;sourceSprite=0x0200c000;stack=struct.unpack('<I',u.mem_read(o.vm+0x14,4))[0];o.camera_fixture=False
 animations=[a for p in sorted((ROOT/'sprites').glob('*/bank.json')) for a in json.loads(p.read_text())['animations']];shrek=json.loads((ROOT/'sprites/shrek_ogre/bank.json').read_text())['animations']
 def seed(address,sprite,s,vt):
  u.mem_write(address,struct.pack('<I',vt));u.mem_write(address+8,struct.pack('<2i',*s[28:30]));u.mem_write(address+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(address+0x178,struct.pack('<2i',*s[:2]));u.mem_write(address+0x15c,bytes([s[40]]));u.mem_write(address+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(address+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite+8,struct.pack('<2i',s[47],s[22]));u.mem_write(sprite+0x28,bytes([s[18],s[38]]))
 totals=[0]*8;captures=0;cases=8000
 for case in range(cases):
  ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();e=(ctypes.c_int32*8)();start(0x08052c28,v)
  r[0]=2;r[2]=case%5==0;r[8:12]=[6,0x080531fc,8,0x08053240]
  for s,pool in [(ss,shrek),(ts,animations)]:
   a=rng.choice(pool);s[47]=ROM_BASE+a['record_offset'];s[22]=rng.randrange(a['sequence_count']);s[26],s[27],s[30],s[31]=a['bounds'];s[18]=rng.randrange(2);s[38]=rng.randrange(2);s[40]=rng.choice([0,8,16,24]);s[28]=17;s[29]=-19
  ss[0]=rng.randint(-100000,100000);ss[1]=rng.randint(-100000,100000);ts[0]=ss[0]+rng.randint(-10000,10000);ts[1]=ss[1]+rng.randint(-10000,10000)
  ss[41:44]=[rng.randrange(3),rng.choice([0,6,8,9]),-123];e[0]=rng.choice([0,2,4,6,8]);e[1]=rng.choice([0,3,5,7]);e[2]=rng.choice([0,16,32,48]);e[3]=77 if case%4==0 else 0;e[4:7]=[rng.randrange(3),rng.choice([0,6,8,9]),rng.randint(-2,2)];dy=rng.choice([-256,0,1,256,4096,20000]);category=rng.choice([0,3,3]);held=e[2]
  seed(source,sourceSprite,ss,0x020017cc);seed(target,targetSprite,ts,0x0200268c);u.mem_write(source+0x1d8,struct.pack('<i',e[0]));u.mem_write(source+0x258,struct.pack('<i',e[1]));u.mem_write(source+0x1ec,struct.pack('<I',0x02006000 if e[3] else 0));u.mem_write(source+0x21c,struct.pack('<3i',*e[4:7]));u.mem_write(source+0x18c,struct.pack('<i',dy));u.mem_write(target+0x168,struct.pack('<i',category));u.mem_write(target+0x250,struct.pack('<i',2));u.mem_write(target+0x1d0,struct.pack('<4i',*r[8:12]));u.mem_write(target+0x254,bytes([r[2]]));u.mem_write(target+0x2a0,bytes(8));u.mem_write(o.vm+4,struct.pack('<4i',*v[:4]));u.mem_write(o.vm+0x14,struct.pack('<I',stack));u.mem_write(stack,struct.pack('<5i',*v[8:13]))
  o.call(0x0800e788,source,target);d=(ctypes.c_int32*8)();assert pair(ss,e,dy,123,category,ts,v,r,fetch,None,d)==0
  carried=struct.unpack('<I',u.mem_read(source+0x1ec,4))[0];expectedCarry={0:0,target:123,0x02006000:77}[carried]
  actual=[ss[40],ss[43],e[3],list(ts[28:30]),r[2],list(r[3:5]),list(v[:4])];expected=[u.mem_read(source+0x15c,1)[0],struct.unpack('<i',u.mem_read(source+0x1a8,4))[0],expectedCarry,list(struct.unpack('<2i',u.mem_read(target+8,8))),u.mem_read(target+0x254,1)[0],list(struct.unpack('<2i',u.mem_read(target+0x2a0,8))),list(struct.unpack('<4i',u.mem_read(o.vm+4,16)))];assert actual==expected,(case,actual,expected,list(d))
  for depth in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+depth*20,20)));f[2]&=255;assert list(v[8+depth*5:13+depth*5])==f
  totals=[x+y for x,y in zip(totals,d)];captures+=e[3]==123
 # Refuse missing lifecycle support before any state mutation.
 for mode,flags in [(6,0),(0,4)]:
  e[1]=mode;ss[40]=flags;before=[list(x) for x in [ss,e,ts,v,r]];assert pair(ss,e,1,123,3,ts,v,r,fetch,None,(ctypes.c_int32*8)())==-4;assert before==[list(x) for x in [ss,e,ts,v,r]]
 result={'original_entry':'0x0800E788','original_outgoing_override':'0x0800EBC0','cases':cases,'hit_activation_counts':dict(zip(['base_hit','base_activated','left_hit','left_activated','right_hit','right_activated','falling_hit','falling_activated'],totals)),'successful_capture_cases':captures,'native_lifecycle_refusal_checks':2,'mismatches':0,'scope':'Real Shrek vtable pair/outgoing handlers and generic target hit/reaction/VM stack routines. All 26 Shrek animations, target animations across 16 banks, both flips, body/frame boxes, reaction guards, state-8 capture refusal, category gating and falling-strip ordering. Held-input getter is a fixture; mode-6 carried-object destruction, dynamic surfaces, incoming Shrek handler, constructor/default event configuration, full world loop and Android execution are excluded.'}
 assert all(totals[i]>0 for i in [0,1,2,3,4,5,6,7]) and captures>0
 (ROOT/'docs/shrek_interactions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
