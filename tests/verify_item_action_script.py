#!/usr/bin/env python3
"""Execute original type77 event29 up to its deferred removal mark."""
import argparse,ctypes,json,struct
from verify_generic_runtime import Original,ROOT,IP,FC,RC,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Rom(args.rom);o=Original(rom);u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));spec=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==77);o.ctor(spec['definition'],xy=(120*256,340*256));original=[];native=[]
 cam=0x02006800;u.mem_write(struct.unpack_from('<I',rom.data,0xa7c)[0],struct.pack('<I',cam));screenGlobals=[struct.unpack_from('<I',rom.data,a)[0] for a in [0x1af5c,0x1af60,0x1af64,0x1af68]];maskAddress=0x02007600;u.mem_write(struct.unpack_from('<I',rom.data,0x9ce0)[0],struct.pack('<I',maskAddress));u.mem_write(maskAddress,bytes(16));u.mem_write(o.actor+0x160,struct.pack('<i',77))
 def hook(uc,address,size,data):
  ret=None
  if address==0x0800bec0:original.append([1,*struct.unpack('<4i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),16))]);ret=0
  elif address==0x080163ac:original.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);ret=0
  elif address==0x08000a68:original.append([16,*[ctypes.c_int32(uc.reg_read(reg)).value for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]])
  elif address==0x0801af44:original.append([17,ctypes.c_int32(uc.reg_read(UC_ARM_REG_R0)).value])
  elif address==0x08005168:original.append([19,77])
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();effects=(ctypes.c_int32*9)();mask=(ctypes.c_uint32*4)();init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];assert init((ctypes.c_int32*2)(120*256,340*256),0,spec['initial_animation'],0,fetch,None,s)==0;o.seed(s);u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*s[32:36]));u.mem_write(o.actor+0x148,bytes(4));start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start(spec['script'],v);o.call(0x08013344,o.vm,spec['script']);stack=struct.unpack('<I',u.mem_read(o.vm+0x14,4))[0]
 camera=lib.s2_camera_effect_begin;camera.argtypes=[IP,IP];screen=lib.s2_screen_effect_begin;screen.argtypes=[IP,ctypes.c_int32];mark=lib.s2_actor_mark_removed;mark.argtypes=[IP,ctypes.c_int32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t];activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP]
 @REG
 def registry(enabled,ctx):raise AssertionError('Unexpected broadcast')
 @RC
 def random(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):
  if kind==1:p=(ctypes.c_int32*4)();assert fetch(address,p,4,None);native.append([1,*p]);return 0
  if kind==11:native.append([11,address,scale]);return 0
  if kind==16:p=(ctypes.c_int32*3)();assert fetch(address,p,3,None);native.append([16,*p]);return camera(effects,p)
  if kind==17:value=ctypes.c_int32(address).value;native.append([17,value]);return screen(ctypes.cast(ctypes.byref(effects,20),IP),value)
  if kind==19:native.append([19,77]);return mark(s,77,mask,4)
  raise AssertionError(kind)
 step=lib.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK]
 for tick in range(1,481):
  if tick==120:
   event=(ctypes.c_int32*3)(0,29,0);u.mem_write(0x02007300,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007300);assert activate(v,r,event)==1
  original.clear();native.clear();u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,v,tick,3200*256,400*256,fetch,random,None,4096,r,registry,sink)==0
  snap=o.snapshot();assert all(s[i]==value for i,value in snap.items()),(tick,{i:(s[i],value) for i,value in snap.items() if s[i]!=value});assert original==native,(tick,original,native);assert list(v[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));assert s[79]==struct.unpack('<i',u.mem_read(o.actor+0x2dc,4))[0]==0
  for d in range(v[2]+1):
   f=list(struct.unpack('<5i',u.mem_read(stack+d*20,20)));f[2]&=255;assert list(v[8+d*5:13+d*5])==f
  assert [r[0],r[2],r[3],r[4]]==[struct.unpack('<i',u.mem_read(o.actor+0x250,4))[0],u.mem_read(o.actor+0x254,1)[0],*struct.unpack('<2i',u.mem_read(o.actor+0x2a0,8))]
  if r[0]:assert list(r[8:8+r[0]*2])==list(struct.unpack('<'+'i'*(r[0]*2),u.mem_read(o.actor+0x1d0,r[0]*8)))
  assert list(effects)==list(struct.unpack('<5i',u.mem_read(cam+0x20,20)))+[struct.unpack('<i',u.mem_read(a,4))[0] for a in screenGlobals]
  assert list(mask)==list(struct.unpack('<4I',u.mem_read(maskAddress,16)))
  if s[40]&1:break
 else:raise AssertionError('Item not marked for removal')
 result={'original_type77_ticks':tick,'event29_trigger_tick':120,'removed_scene_id':77,'effects_at_last_tick':native,'mismatches':0,'scope':'Original type77 18208 startup/event29 VM through removal11; actor fields, VM/active stacks, callback requests, camera/screen initialization and removal bitmap. Global BEC0 packet/audio delivery are acknowledged fixtures. No global game effect execution, camera/fade progression, secondary spawning, destruction or Android execution.'};(ROOT/'docs/item_action_script_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
