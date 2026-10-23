import sys,ctypes,struct,json
from verify_generic_runtime import *
o=Original(Rom(sys.argv[1]));u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=l.s2_plain_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];step=l.s2_plain_runtime_step;step.argtypes=[IP,ctypes.c_int32]
@FC
def fetch(a,out,n,ctx):
 raw=u.mem_read(a,n*4)
 for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
 return 1
cases=0
for anim,xy in [(0x832a77c,(91,350)),(0x832a794,(413,341)),(0x832a7ac,(630,273))]:
 for flip in range(4):
  u.mem_write(0x0200324c,bytes(4));u.mem_write(0x020033e0,bytes(4));u.mem_write(o.actor,bytes(4096));u.mem_write(0x02007000,struct.pack('<2i',*(v*256 for v in xy)));u.mem_write(0x0203f000,bytes([(flip>>1)&1])+bytes(15));o.call(0x80180b0,o.actor,anim,0x02007000,flip&1);sp=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];s=(ctypes.c_int32*80)();assert init((ctypes.c_int32*2)(*(v*256 for v in xy)),flip,anim,0,fetch,None,s)==0
  def compare(t):
   wanted={0:struct.unpack('<i',u.mem_read(o.actor+0x178,4))[0],1:struct.unpack('<i',u.mem_read(o.actor+0x17c,4))[0],20:u.mem_read(sp,1)[0],21:struct.unpack('<i',u.mem_read(sp+4,4))[0],22:struct.unpack('<i',u.mem_read(sp+12,4))[0],23:struct.unpack('<i',u.mem_read(sp+16,4))[0],18:u.mem_read(sp+0x28,1)[0],38:u.mem_read(sp+0x29,1)[0],39:u.mem_read(o.actor+0x15d,1)[0],40:u.mem_read(o.actor+0x15c,1)[0],26:struct.unpack('<h',u.mem_read(o.actor+0x170,2))[0],27:struct.unpack('<h',u.mem_read(o.actor+0x172,2))[0],30:u.mem_read(o.actor+0x174,1)[0],31:u.mem_read(o.actor+0x175,1)[0]}
   for i,v in enumerate(struct.unpack('<4i',u.mem_read(o.actor+0x190,16)),32):wanted[i]=v
   diff={i:(s[i],v)for i,v in wanted.items()if s[i]!=v};assert not diff,(anim,flip,t,diff)
  compare(0)
  for tick in range(1,161):
   u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));o.call(0x8018208,o.actor);assert step(s,tick)==0;compare(tick);cases+=1
report={'original_animation_frames':cases,'animation_types':[130,134,135],'mismatches':0,'scope':'Original180B0 constructor and18208 frames, source position/bounds/flips/flags/animation against native plain actor. Factory pointers reflect startup RAM, not proof of scene-specific initialization. Camera visibility is a fixture; text/dialogue scripts excluded.'};(ROOT/'docs/plain_animation_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
