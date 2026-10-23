#!/usr/bin/env python3
"""Original camera/screen initializers and removal through generic messages."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Rom(args.rom);o=Original(rom);u=o.u;rng=random.Random(202626);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 o.ctor(json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18']['definition']);cam=0x02006800;camGlobal=struct.unpack_from('<I',rom.data,0xa7c)[0];u.mem_write(camGlobal,struct.pack('<I',cam));screenGlobals=[struct.unpack_from('<I',rom.data,a)[0] for a in [0x1af5c,0x1af60,0x1af64,0x1af68]];maskAddress=0x02007600;maskGlobal=struct.unpack_from('<I',rom.data,0x9ce0)[0];u.mem_write(maskGlobal,struct.pack('<I',maskAddress))
 camera=lib.s2_camera_effect_begin;camera.argtypes=[IP,IP];screen=lib.s2_screen_effect_begin;screen.argtypes=[IP,ctypes.c_int32];world=lib.s2_generic_world_message;world.argtypes=[IP,ctypes.c_int,ctypes.c_int,ctypes.c_int32,FC,SINK,ctypes.c_void_p];mark=lib.s2_actor_mark_removed;mark.argtypes=[IP,ctypes.c_int32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t]
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 state=(ctypes.c_int32*80)();effects=(ctypes.c_int32*9)();mask=(ctypes.c_uint32*4)();requests=[]
 @SINK
 def sink(kind,address,scale,ctx):
  requests.append([kind,address,scale])
  if kind==16:
   p=(ctypes.c_int32*3)();assert fetch(address,p,3,None);return camera(effects,p)
  if kind==17:return screen(ctypes.cast(ctypes.byref(effects,5*4),IP),ctypes.c_int32(address).value)
  if kind==19:return mark(state,77,mask,4)
  raise AssertionError(kind)
 for ident in [46,47]:
  for case in range(4000):
   effects[:]=[rng.randint(-2147483648,2147483647) for _ in range(9)];u.mem_write(cam+0x20,struct.pack('<5i',*effects[:5]))
   for addr,value in zip(screenGlobals,effects[5:]):u.mem_write(addr,struct.pack('<i',value))
   payload=0x02007400 if ident==46 else rng.randint(-2147483648,2147483647)
   if ident==46:u.mem_write(payload,struct.pack('<3i',*[rng.randint(-2147483648,2147483647) for _ in range(3)]))
   requests.clear();o.message(ident,payload,case);assert world(state,8,ident,payload,fetch,sink,None)==0
   actual=list(effects);expected=list(struct.unpack('<5i',u.mem_read(cam+0x20,20)))+[struct.unpack('<i',u.mem_read(addr,4))[0] for addr in screenGlobals];assert actual==expected,(ident,case,actual,expected);assert requests==[[16 if ident==46 else 17,payload&0xffffffff,0]]
 for case in range(2000):
  state[40]=rng.randrange(256);mask[:]=[rng.getrandbits(32) for _ in range(4)];u.mem_write(o.actor+0x15c,bytes([state[40]]));u.mem_write(o.actor+0x160,struct.pack('<i',77));u.mem_write(maskAddress,struct.pack('<4I',*mask));o.message(11,0,case);assert world(state,8,11,0,fetch,sink,None)==0;assert state[40]==u.mem_read(o.actor+0x15c,1)[0] and list(mask)==list(struct.unpack('<4I',u.mem_read(maskAddress,16)))
 result={'camera_command46_cases':4000,'screen_command47_cases':4000,'owned_removal_command11_cases':2000,'mismatches':0,'scope':'Original generic13B8C -> 0A68 camera initialization, 1AF44 screen initialization and 5168/9CC0 removal mark. Owner/global memory supplied by fixture. Later camera/fade update, secondary spawning and full world destruction excluded.'};(ROOT/'docs/world_effect_requests_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
