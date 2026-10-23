#!/usr/bin/env python3
"""Original rectangles, reflection, frame box resources and reaction chain."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom,ROM_BASE
from unicorn.arm_const import UC_ARM_REG_R0

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202613)
 @FC
 def fetch(address,out,n,ctx):
  try:raw=u.mem_read(address,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 overlap=lib.s2_rect_overlap_xywh;overlap.argtypes=[IP,IP];center=lib.s2_rect_intersection_center;center.argtypes=[IP,IP,IP];center.restype=None;transform=lib.s2_actor_box_q8;transform.argtypes=[IP,IP,IP];pair=lib.s2_generic_contact_pair;pair.argtypes=[IP,IP,IP,IP,FC,ctypes.c_void_p,IP];pair.restype=ctypes.c_int
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];o.ctor(bindings['18']['definition']);sourceAddress=0x02005000;sourceSprite=0x0200c000;target=o.actor;targetSprite=o.sprite;stack=struct.unpack('<I',u.mem_read(o.vm+0x18,4))[0];o.camera_fixture=False
 rectCases=transformCases=contactCases=0
 for i in range(5000):
  values=lambda:[rng.choice([-2147483648,2147483647,0,rng.randint(-1000000,1000000)]) for _ in range(4)]
  aa=values();bb=values();u.mem_write(0x02007300,struct.pack('<4i',*aa));u.mem_write(0x02007320,struct.pack('<4i',*bb));o.call(0x080007e0,0x02007300,0x02007320);assert overlap((ctypes.c_int32*4)(*aa),(ctypes.c_int32*4)(*bb))==u.reg_read(UC_ARM_REG_R0)
  o.call(0x08000708,0x02007340,0x02007300,0x02007320);expected=list(struct.unpack('<2i',u.mem_read(0x02007340,8)));point=(ctypes.c_int32*2)();center((ctypes.c_int32*4)(*aa),(ctypes.c_int32*4)(*bb),point);assert list(point)==expected,(aa,bb,list(point),expected);rectCases+=1
 def seed_actor(address,sprite,s):
  u.mem_write(address,struct.pack('<I',0x0200268c));u.mem_write(address+8,struct.pack('<2i',s[28],s[29]));u.mem_write(address+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(address+0x178,struct.pack('<2i',*s[:2]));u.mem_write(address+0x15c,bytes([s[40]]));u.mem_write(address+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(address+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite+8,struct.pack('<2i',s[47],s[22]));u.mem_write(sprite+0x28,bytes([s[18],s[38]]))
 for i in range(3000):
  s=(ctypes.c_int32*80)();s[0]=rng.choice([-2147483648,2147483647,rng.randint(-1000000,1000000)]);s[1]=rng.choice([-2147483648,2147483647,rng.randint(-1000000,1000000)]);s[26]=rng.randint(-32768,32767);s[27]=rng.randint(-32768,32767);s[30]=rng.randrange(256);s[31]=rng.randrange(256);s[18]=i%2;s[38]=(i//2)%2;seed_actor(sourceAddress,sourceSprite,s)
  box=[rng.randint(-32768,32767),rng.randint(-32768,32767),rng.randrange(256),rng.randrange(256)];u.mem_write(0x02007300,struct.pack('<hhBBH',*box,0));o.call(0x08018460,sourceAddress,0x02007300,0x02007320);out=(ctypes.c_int32*4)();assert transform(s,(ctypes.c_int32*4)(*box),out)==0;assert list(out)==list(struct.unpack('<4i',u.mem_read(0x02007320,16)));transformCases+=1
 banks=[json.loads(path.read_text()) for path in sorted((ROOT/'sprites').glob('*/bank.json'))];animations=[anim for bank in banks for anim in bank['animations']];hits=activated=0
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 for case in range(6000):
  ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();r[0]=1;r[2]=case%3==0;r[8]=8;r[9]=0x080531fc;start(0x08052c28,v)
  for s in [ss,ts]:
   anim=rng.choice(animations);s[47]=ROM_BASE+anim['record_offset'];s[22]=rng.randrange(anim['sequence_count']);s[26],s[27],s[30],s[31]=anim['bounds'];s[18]=rng.randrange(2);s[38]=rng.randrange(2);s[40]=rng.choice([0,8,16,24]);s[0]=rng.randint(-10000,10000);s[1]=rng.randint(-10000,10000);s[28]=17;s[29]=-19
  if case%2:ts[0]=ss[0]+rng.randint(-4000,4000);ts[1]=ss[1]+rng.randint(-4000,4000)
  ss[41]=rng.randint(-2,2);ss[42]=rng.choice([0,8,9]);ss[43]=-123;seed_actor(sourceAddress,sourceSprite,ss);seed_actor(target,targetSprite,ts)
  u.mem_write(target+0x250,struct.pack('<i',1));u.mem_write(target+0x1d0,struct.pack('<2i',8,0x080531fc));u.mem_write(target+0x254,bytes([r[2]]));u.mem_write(target+0x2a0,bytes(8));u.mem_write(o.vm+4,struct.pack('<4i',*v[:4]));u.mem_write(o.vm+0x14,struct.pack('<I',stack));u.mem_write(stack,struct.pack('<5i',*v[8:13]));o.call(0x080184f8,sourceAddress,target)
  diag=(ctypes.c_int32*4)();assert pair(ss,ts,v,r,fetch,None,diag)==0
  expectedSourceFlags=u.mem_read(sourceAddress+0x15c,1)[0];expectedSide=struct.unpack('<i',u.mem_read(sourceAddress+0x1a8,4))[0];expectedPoint=list(struct.unpack('<2i',u.mem_read(target+8,8)));expectedGuard=u.mem_read(target+0x254,1)[0];expectedMeta=list(struct.unpack('<2i',u.mem_read(target+0x2a0,8)));expectedVM=list(struct.unpack('<4i',u.mem_read(o.vm+4,16)))
  actual=[ss[40],ss[43],list(ts[28:30]),r[2],list(r[3:5]),list(v[:4])];expected=[expectedSourceFlags,expectedSide,expectedPoint,expectedGuard,expectedMeta,expectedVM];assert actual==expected,(case,ss[47],ts[47],actual,expected)
  for d in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));f[2]&=255;assert list(v[8+d*5:13+d*5])==f
  hits+=diag[0];activated+=diag[1];contactCases+=1
 result={'rectangle_and_center_cases':rectCases,'box_transform_cases':transformCases,'original_generic_pair_cases':contactCases,'overlapping_cases':hits,'activated_cases':activated,'mismatches':0,'scope':'Original 184F8 generic pair processing, 18900/1889C/body overlap, 18460 transforms, 525C direction/event dispatch and 13A54 activation execute with real frame resources. Stable candidate pairs and generic vtables; dynamic-surface append, subclass overrides and world candidate discovery are excluded.'}
 # Full target update after a candidate source crosses it; pair supplies the event.
 from unicorn import UC_HOOK_CODE
 from unicorn.arm_const import UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
 from verify_generic_runtime import RC
 REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
 originalEffects=[];nativeEffects=[]
 def audio_hook(uc,address,size,data):
  if address==0x080163ac:originalEffects.append([11,uc.reg_read(UC_ARM_REG_R1),256]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,audio_hook)
 @REG
 def registry(enabled,ctx):raise AssertionError('local-only script')
 @RC
 def rand(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):nativeEffects.append([kind,address,scale]);return 0
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK]
 o.camera_fixture=True;o.ctor(bindings['18']['definition'],xy=(160*256,320*256));targetSprite=o.sprite;stack=struct.unpack('<I',u.mem_read(o.vm+0x18,4))[0];ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(0,320*256),0,0x0834f274,0,fetch,None,ss)==0;ss[40]=0;ss[41]=1;ss[42]=8;assert init((ctypes.c_int32*2)(160*256,320*256),0,bindings['18']['animation'],0,fetch,None,ts)==0;o.seed(ts);source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18);start(source['script'],v);o.call(0x08013344,o.vm,source['script']);allEffects=[];wholeHits=wholeActivations=0
 for tick in range(1,481):
  # Controlled moving source, but no manually constructed target event.
  phase=tick%160;x=(phase if phase<=80 else 160-phase)*4;ss[0]=(x-3)*256;ss[1]=321*256;ss[40]&=~16;seed_actor(sourceAddress,sourceSprite,ss);o.camera_fixture=False
  u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));originalEffects.clear();nativeEffects.clear()
  for repeat in range(2):
   o.call(0x080184f8,sourceAddress,target);diag=(ctypes.c_int32*4)();assert pair(ss,ts,v,r,fetch,None,diag)==0;wholeHits+=diag[0];wholeActivations+=diag[1];assert ss[40]==u.mem_read(sourceAddress+0x15c,1)[0];assert ss[43]==struct.unpack('<i',u.mem_read(sourceAddress+0x1a8,4))[0];assert list(ts[28:30])==list(struct.unpack('<2i',u.mem_read(target+8,8)))
  o.camera_fixture=True;o.call(0x08018208,target);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),ts,v,tick,3200*256,400*256,fetch,rand,None,4096,r,registry,sink)==0,(tick,list(v[:4]));assert nativeEffects==originalEffects;allEffects.extend([[tick,*e] for e in nativeEffects]);snapshot=o.snapshot();assert all(ts[i]==value for i,value in snapshot.items()),(tick,{i:(ts[i],value) for i,value in snapshot.items() if ts[i]!=value});assert list(ts[:2])==list(struct.unpack('<2i',u.mem_read(target+0x178,8)));assert list(ts[30:32])==list(u.mem_read(target+0x174,2));assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)))
  assert [r[0],r[2],r[3],r[4]]==[struct.unpack('<i',u.mem_read(target+0x250,4))[0],u.mem_read(target+0x254,1)[0],*struct.unpack('<2i',u.mem_read(target+0x2a0,8))]
  for d in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));f[2]&=255;assert list(v[8+d*5:13+d*5])==f
 assert wholeActivations>0 and len(allEffects)==wholeActivations
 # Explicit refusal/missing-resource/zero-attacker-box paths.
 before=list(ss);ss[40]|=4;assert pair(ss,ts,v,r,fetch,None,(ctypes.c_int32*4)())==-4;ss[:]=before
 ss[40]=8;ss[47]=0;assert pair(ss,ts,v,r,fetch,None,(ctypes.c_int32*4)())==-2
 ss[47]=bindings['18']['animation'];ss[22]=0;ts[47]=0;ts[40]|=8;assert pair(ss,ts,v,r,fetch,None,(ctypes.c_int32*4)())==0
 result['native_error_or_empty_box_checks']=3
 result['whole_target_ticks']=480;result['whole_pair_overlaps']=wholeHits;result['whole_pair_activations']=wholeActivations;result['whole_sound_effects']=len(allEffects);result['whole_scope']='Original pair handler generates events from geometry before target 18208 update. Real type-18 script/response, two repeated pair calls per tick, controlled source path, camera/allocator/audio-output fixtures. Stable pair candidate selection, no original world broadphase or Shrek subclass interactions.'
 (ROOT/'docs/actor_interactions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
