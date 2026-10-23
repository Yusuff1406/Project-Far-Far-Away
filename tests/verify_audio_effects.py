#!/usr/bin/env python3
"""Compare SFX requests, actor audio routes and real type-18 response."""
import argparse,ctypes,json,random,struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from verify_generic_runtime import Original,ROOT,IP,FC,RC,Rom,ROM_BASE
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);PLAY=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_void_p);VOL=ctypes.CFUNCTYPE(None,ctypes.c_int32,ctypes.c_uint32,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));manager=0x02020000;descriptor=0x02020100;returns=[0,0];originalCalls=[];nativeCalls=[];ogains=[];ngains=[];originalDescriptors=[];emitted=[]
 def hook(uc,addr,size,data):
  if addr==0x080163ac:originalDescriptors.append(uc.reg_read(UC_ARM_REG_R1))
  if addr==0x0801d234:
   args=[ctypes.c_int32(uc.reg_read(r)).value for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=returns[min(len(originalCalls),1)];originalCalls.append(args);uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif addr==0x0801da20 and volumeMock:
   ogains.append([ctypes.c_int32(uc.reg_read(UC_ARM_REG_R0)).value,uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);volumeMock=True;u.mem_write(0x02003210,struct.pack('<I',manager));u.mem_write(manager,bytes(0xc0));rng=random.Random(202612)
 @PLAY
 def play(id,channel,priority,sub,ctx):
  ret=returns[min(len(nativeCalls),1)];nativeCalls.append([id,channel,priority,sub]);return ret
 @VOL
 def volume(voice,gain,ctx):ngains.append([voice,gain])
 @FC
 def fetch(address,out,n,ctx):
  try:raw=u.mem_read(address,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 audio=lib.s2_audio_sfx;audio.argtypes=[IP,IP,ctypes.c_int32,PLAY,VOL,ctypes.c_void_p];audio.restype=ctypes.c_int;resource=lib.s2_audio_sfx_resource;resource.argtypes=[IP,ctypes.c_uint32,ctypes.c_int32,FC,PLAY,VOL,ctypes.c_void_p];route=lib.s2_generic_audio_message;route.argtypes=[IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,SINK,ctypes.c_void_p]
 def seed(m):
  u.mem_write(manager,struct.pack('<i',m[0]));u.mem_write(manager+0x1c,struct.pack('<i',m[2]));u.mem_write(manager+0x50,struct.pack('<2i',*m[3:5]));u.mem_write(0x0200032c,struct.pack('<i',m[1]))
 def check(m):
  expected=[struct.unpack('<i',u.mem_read(manager,4))[0],struct.unpack('<i',u.mem_read(0x0200032c,4))[0],struct.unpack('<i',u.mem_read(manager+0x1c,4))[0],*struct.unpack('<2i',u.mem_read(manager+0x50,8))];assert list(m[:5])==expected,(list(m[:5]),expected);assert nativeCalls==originalCalls,(nativeCalls,originalCalls);assert ngains==ogains,(ngains,ogains)
 m=(ctypes.c_int32*8)();sfxCases=0
 for case in range(3000):
  m[0]=case%3;m[1]=case%2;m[2]=rng.choice([0,256,-1,-2147483648,2147483647,rng.randint(-100000,100000)]);m[3]=71;m[4]=-5;d=(ctypes.c_int32*3)(rng.choice([0,59,-1,123]),rng.randint(-1000,1000),rng.choice([0,200,256,-1,2147483647]));scale=rng.choice([0,256,-1,-2147483648,2147483647]);returns=[[0,1],[-1,1],[-1,-1],[-2,0]][case%4];seed(m);u.mem_write(descriptor,struct.pack('<3i',*d));originalCalls.clear();nativeCalls.clear();ogains.clear();ngains.clear();o.call(0x080163ac,manager,descriptor,scale);code=audio(m,d,scale,play,volume,None);assert code>=0;check(m);sfxCases+=1
 @SINK
 def sink(kind,address,scale,ctx):emitted.append([kind,address,scale]);return 0
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);actor=(ctypes.c_int32*80)();actorCases=0
 for id in [34,35,36,37,38,39,56]:
  for case in range(256):
   actor[56]=case%256;actor[58]=0 if case%3==0 else 0x08053fb4;actor[59]=0 if case%3==0 else 0x08053fe4;actor[63]=0 if case%3==0 else 0x08053c6c
   u.mem_write(o.actor+0x10,bytes([actor[56]]));u.mem_write(o.actor+0x2b4,struct.pack('<3i',actor[58],actor[59],actor[63]));payload=0 if case%3==0 else 0x08053fb4;originalDescriptors.clear();emitted.clear();o.message(id,payload,1);assert route(actor,8,id,payload,sink,None)==0;expect=list(struct.unpack('<3i',u.mem_read(o.actor+0x2b4,12)));assert [actor[58],actor[59],actor[63]]==expect;assert emitted==[[11,address,256] for address in originalDescriptors];actorCases+=1
 # Original channel volume setter's unsigned clamp, all-channel and invalid voice paths.
 volumeMock=False;engine=0x02021000;channels=0x02022000;u.mem_write(0x02006300,struct.pack('<I',engine));u.mem_write(engine,bytes(0x100));u.mem_write(engine+0xc,struct.pack('<2I',channels,4));clamp=lib.s2_audio_volume_byte;clamp.argtypes=[ctypes.c_uint32];clamp.restype=ctypes.c_uint32;vc=0
 for case in range(1000):
  voice=[-2,-1,0,3,4,9][case%6];gain=rng.choice([0,255,256,65535,0xffffffff,rng.randrange(2**32)]);u.mem_write(channels,bytes([17])*0x140);o.call(0x0801da20,voice,gain);actual=[u.mem_read(channels+i*0x50+0xc,1)[0] for i in range(4)];expected=[clamp(gain) if voice==-1 or i==voice else 17 for i in range(4)];assert actual==expected;(vc:=vc+1)
 volumeMock=True
 # Real type-18 registration and reaction, including actual original 163AC requests.
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None;rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int32,IP];rinit.restype=None;activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP]
 @REG
 def registry(enabled,ctx):raise AssertionError('Original type 18 uses local registration only')
 @RC
 def rand(ctx):return 37
 @SINK
 def backend(kind,address,scale,ctx):
  if kind!=11:return -4
  emitted.append([kind,address,scale]);code=resource(m,address,scale,fetch,play,volume,None);return code if code<0 else 0
 o.ctor(binding['definition'],xy=(120*256,310*256));actor=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(120*256,310*256),0,binding['animation'],0,fetch,None,actor)==0;o.seed(actor);rinit(0,r);source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18);start(source['script'],v);o.call(0x08013344,o.vm,source['script']);m[0]=1;m[1]=0;m[2]=256;m[3]=m[4]=0;seed(m);returns=[0,1];ticks=0;triggers=[];allRequests=[]
 for tick in range(1,361):
  u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));originalDescriptors.clear();emitted.clear();originalCalls.clear();nativeCalls.clear();ogains.clear();ngains.clear()
  if tick in [40,140,240]:
   cmd=(ctypes.c_int32*3)(2,8,999);u.mem_write(0x02007200,struct.pack('<3i',*cmd));o.call(0x08013a54,o.actor,0x02007200);assert activate(v,r,cmd)==u.reg_read(UC_ARM_REG_R0)==1;triggers.append(tick)
  o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),actor,v,tick,3200*256,400*256,fetch,rand,None,4096,r,registry,backend)==0,(tick,list(v[:4]));check(m);assert emitted==[[11,address,256] for address in originalDescriptors]
  assert [actor[58],actor[59],actor[63]]==list(struct.unpack('<3i',u.mem_read(o.actor+0x2b4,12)))
  snapshot=o.snapshot();assert all(actor[i]==val for i,val in snapshot.items()),(tick,{i:(actor[i],val) for i,val in snapshot.items() if actor[i]!=val});assert list(actor[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));stack=struct.unpack('<I',u.mem_read(o.vm+0x18,4))[0]
  for d in range(v[2]+1):
   expected=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));expected[2]&=255;assert list(v[8+d*5:13+d*5])==expected
  allRequests.extend([[tick,*x] for x in emitted]);ticks+=1
 assert len(allRequests)==3 and all(x[2]==0x08053fb4 for x in allRequests)
 # Raw external VM effects are delegated in order; backend owns their semantics.
 delegatedOriginal=[];delegatedNative=[]
 def external_hook(uc,addr,size,data):
  kinds={0x0800bec0:1,0x080161b0:12,0x0801afec:13,0x0801af94:14,0x0801b044:15}
  if addr in kinds:
   k=kinds[addr];arg=uc.reg_read(UC_ARM_REG_R1 if k==12 else UC_ARM_REG_R0);delegatedOriginal.append([k,arg,0]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif addr==0x080163ac:delegatedOriginal.append([11,uc.reg_read(UC_ARM_REG_R1),256])
 u.hook_add(UC_HOOK_CODE,external_hook)
 @SINK
 def delegate(kind,address,scale,ctx):delegatedNative.append([kind,address,scale]);return 0
 program=0x02007800;cmds=[[5,op,0x08053fb4] for op in [0,11,12,13,14,15]]+[[5,6,0]];u.mem_write(program,b''.join(struct.pack('<3i',*cmd) for cmd in cmds));start(program,v);o.call(0x08013344,o.vm,program);u.mem_write(0x0200324c,struct.pack('<i',361));u.mem_write(0x020033e0,struct.pack('<i',361));o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),actor,v,361,3200*256,400*256,fetch,rand,None,4096,r,registry,delegate)==0;assert delegatedNative==delegatedOriginal and len(delegatedNative)==6
 @SINK
 def reject(kind,address,scale,ctx):return -7
 start(program,v);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),actor,v,362,3200*256,400*256,fetch,rand,None,4096,r,registry,reject)==-7
 # Inactive audio does not fetch its descriptor, but missing active data fails.
 m[0]=0;assert resource(m,0,256,fetch,play,volume,None)==0;m[0]=1;assert resource(m,0,256,fetch,play,volume,None)==-2
 result={'sfx_request_cases':sfxCases,'actor_audio_cases':actorCases,'volume_setter_cases':vc,'real_type18_actor_ticks':ticks,'real_type18_trigger_ticks':triggers,'real_type18_sound_requests':allRequests,'delegated_vm_effects':delegatedNative,'native_error_checks':3,'mismatches':0,'scope':'Original actor/VM/audio-request wrapper execute; low-level channel start and volume output are recorded fixtures. Exact request/fallback/volume/history/animation/script behavior, not sample decoding or audible output. Real local triggers are manually injected, not physically discovered.'};(ROOT/'docs/audio_effects_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
