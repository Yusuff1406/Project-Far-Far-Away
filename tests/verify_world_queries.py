#!/usr/bin/env python3
"""Original endpoint maintenance/sweep callback order and nearest list scan."""
import argparse,ctypes,json,random,struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from verify_generic_runtime import Original,ROOT,IP,FC,Rom,ROM_BASE
BND=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p);PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p);EX=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202614);ep=0x02030000;activeBuf=0x02031000;vt=0x02008000;data={};excludeValues={};calls=[];nativeCalls=[];filterCalls=[];nativeFilterCalls=[]
 u.mem_write(0x02003200,struct.pack('<I',ep));u.mem_write(0x020031f0,struct.pack('<4I',0,activeBuf,16,0));u.mem_write(vt+0x48,struct.pack('<2I',0,0x03001101));u.mem_write(0x03001100,b'\x70\x47');u.mem_write(0x03001200,b'\x70\x47')
 def hook(uc,addr,size,data):
  if addr==0x03001100:calls.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif addr==0x03001200:
   ident=uc.reg_read(UC_ARM_REG_R0);filterCalls.append(ident);uc.reg_write(UC_ARM_REG_R0,excludeValues[ident]&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif addr==0x08020178:
   src=uc.reg_read(UC_ARM_REG_R0);dst=uc.reg_read(UC_ARM_REG_R1);control=uc.reg_read(UC_ARM_REG_R2);n=(control&0x1fffff)*4;raw=uc.mem_read(src,n);uc.mem_write(dst,bytes(raw));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @BND
 def bounds(ident,out,ctx):
  if ident not in data:return 0
  for i,x in enumerate(data[ident]):out[i]=x
  return 1
 @PAIR
 def pair(a,b,ctx):nativeCalls.append([a,b])
 @EX
 def exclude(ident,ctx):nativeFilterCalls.append(ident);return excludeValues[ident]
 add=lib.s2_sweep_add;add.argtypes=[ctypes.c_uint32,IP,IP,IP];remove=lib.s2_sweep_remove;remove.argtypes=[ctypes.c_uint32,IP,IP];sort=lib.s2_sweep_sort;sort.argtypes=[IP,ctypes.c_int];frame=lib.s2_sweep_frame;frame.argtypes=[IP,ctypes.c_int,BND,PAIR,ctypes.c_void_p];near=lib.s2_world_nearest;near.argtypes=[IP,IP,ctypes.c_int,EX,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 endpoints=(ctypes.c_int32*(128*3))();count=(ctypes.c_int32*1)();adds=removes=sorts=sweeps=nearest=0;maxCalls=0
 def actor(ident,b):
  data[ident]=b;u.mem_write(ident,struct.pack('<I',vt));u.mem_write(ident+0x1ac,struct.pack('<4i',b[1],b[0],b[2],b[3]))
 def seed():u.mem_write(0x02003204,struct.pack('<i',count[0]));u.mem_write(ep,struct.pack('<384i',*endpoints));u.mem_write(0x020031f0+12,bytes(4))
 def check_endpoints():
  assert count[0]==struct.unpack('<i',u.mem_read(0x02003204,4))[0];assert list(endpoints[:count[0]*3])==list(struct.unpack('<'+'i'*(count[0]*3),u.mem_read(ep,count[0]*12)))
 for case in range(600):
  count[0]=0;data.clear();n=case%65;seed()
  for i in range(n):
   ident=0x02010000+i*0x400;x=rng.randint(-5000,5000);y=rng.randint(-5000,5000);b=[x,y,x+rng.randint(1,2000),y+rng.randint(1,2000)];actor(ident,b);o.call(0x08015c24,ident);assert add(ident,(ctypes.c_int32*4)(*b),endpoints,count)==1;check_endpoints();adds+=1
  # Inactive endpoint row budget is exactly 128, even for dense scenes.
  if n==64:o.call(0x08015c24,0x02010000);assert add(0x02010000,(ctypes.c_int32*4)(*data[0x02010000]),endpoints,count)==0;check_endpoints();adds+=1
  seed();o.call(0x08015cdc);assert sort(endpoints,count[0])==0;check_endpoints();sorts+=1
  for tick in range(3):
   for ident,b in list(data.items()):
    dx=rng.randint(-300,300);dy=rng.randint(-300,300);b=[b[0]+dx,b[1]+dy,b[2]+dx,b[3]+dy]
    if case%17==0:b=[0,0,1000,1000] # active-list capacity and equal-key stability
    actor(ident,b)
   calls.clear();nativeCalls.clear();seed();o.call(0x08015c90);code=frame(endpoints,count[0],bounds,pair,None);assert code==len(calls) and nativeCalls==calls,(case,tick,code,len(calls),nativeCalls[:20],calls[:20]);check_endpoints();assert struct.unpack('<i',u.mem_read(0x020031f0+12,4))[0]==0;sweeps+=1;maxCalls=max(maxCalls,len(calls))
  for ident in list(data)[::3]:
   seed();before=count[0];o.call(0x08015f50,ident);removed=remove(ident,endpoints,count);assert removed==2 and count[0]==before-2;check_endpoints();removes+=1
 # Envelope compared with original full base/generic actor update for real poses.
 envelope=lib.s2_actor_envelope_q8;envelope.argtypes=[IP,FC,ctypes.c_void_p,IP];envelope.restype=ctypes.c_int
 @FC
 def fetch(address,out,n,ctx):
  try:raw=u.mem_read(address,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];definition=bindings['39']['definition'];poses=0
 for path in sorted((ROOT/'sprites').glob('*/bank.json')):
  bank=json.loads(path.read_text())
  for anim in bank['animations']:
   for flip in range(4):
    o.ctor(definition,xy=(1000*256,200*256),flags=flip);s=(ctypes.c_int32*80)();s[0]=1000*256;s[1]=200*256;s[26],s[27],s[30],s[31]=anim['bounds'];s[18]=flip&1;s[38]=flip>>1;s[47]=ROM_BASE+anim['record_offset'];s[22]=rng.randrange(anim['sequence_count'])
    u.mem_write(o.actor+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.sprite+8,struct.pack('<3i',s[47],s[22],999));u.mem_write(o.vm+0xc,struct.pack('<i',-1));u.mem_write(0x0200324c,struct.pack('<i',1));u.mem_write(0x020033e0,struct.pack('<i',1));o.call(0x08018208,o.actor);out=(ctypes.c_int32*4)();assert envelope(s,fetch,None,out)==0
    top,left,right,bottom=struct.unpack('<4i',u.mem_read(o.actor+0x1ac,16));assert list(out)==[left,top,right,bottom],(path.parent.name,anim['index'],flip,list(out),[left,top,right,bottom]);poses+=1
 # Nearest scan over original active list (category 0 uses world+4).
 world=0x02009000;group=0x02009100;vector=0x02009200;items=0x02009300;u.mem_write(0x02002e94,struct.pack('<I',world));u.mem_write(world+4,struct.pack('<I',group));u.mem_write(group+4,struct.pack('<I',vector));u.mem_write(vector+4,struct.pack('<I',items))
 for case in range(2500):
  n=case%33;rows=[];excludeValues.clear();point=[rng.choice([0,2147483647,-2147483648,rng.randint(-10000,10000)]) for _ in range(2)]
  for i in range(n):
   ident=0x02010000+i*0x400;x,y=[rng.choice([-2147483648,2147483647,rng.randint(-1000000,1000000)]) for _ in range(2)];rows.extend([ident,x,y]);u.mem_write(ident+0x178,struct.pack('<2i',x,y));excludeValues[ident]=rng.choice([0,1,255,256,-1]);u.mem_write(items+i*4,struct.pack('<I',ident))
  u.mem_write(vector+12,struct.pack('<i',n));u.mem_write(0x02007300,struct.pack('<2i',*point));filterCalls.clear();nativeFilterCalls.clear()
  try:o.call(0x08007580,0x02007300,0,0x03001201)
  except Exception as error:raise AssertionError(('nearest case',case,'pc',hex(u.reg_read(UC_ARM_REG_PC)),'r2',hex(u.reg_read(UC_ARM_REG_R2)),'world',bytes(u.mem_read(0x02002e94,4)).hex(),'group',bytes(u.mem_read(world,40)).hex(),'vector',bytes(u.mem_read(vector,16)).hex())) from error
  expected=u.reg_read(UC_ARM_REG_R0);selected=(ctypes.c_uint32*1)();assert near((ctypes.c_int32*2)(*point),(ctypes.c_int32*len(rows))(*rows),n,exclude,None,selected)==0;assert selected[0]==expected and nativeFilterCalls==filterCalls,(case,selected[0],expected);nearest+=1
 result={'endpoint_add_cases':adds,'stable_sort_cases':sorts,'sweep_frames':sweeps,'endpoint_remove_cases':removes,'envelope_pose_cases':poses,'nearest_cases':nearest,'maximum_callbacks_per_frame':maxCalls,'mismatches':0,'scope':'Original add/refresh/stable sort/sweep/remove and nearest active-list scan execute. Pair/filter callbacks and DMA memmove are fixtures; valid balanced 128 endpoint rows, original 16-entry active scratch capacity, stable object lifetime. No full world category update/activation or subtype callback effects.'};(ROOT/'docs/world_queries_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
