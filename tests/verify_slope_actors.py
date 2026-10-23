#!/usr/bin/env python3
"""Original1730 constructors and17C8 emitted segments for types23/24."""
import ctypes as C,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
r=Rom(sys.argv[1]);o=Original(r);u=o.u;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32;P=C.c_void_p;rng=random.Random(67)
@FC
def fetch(a,out,n,ctx):
 try:raw=u.mem_read(a,n*4)
 except Exception:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
 return 1
init=l.s2_slope_runtime_init;init.argtypes=[IP,I,C.c_uint32,I,FC,P,IP,IP];surface=l.s2_slope_surfaces;surface.argtypes=[IP,I,IP,IP]
constructorCases=0
for definition in [0x08024ab8,0x08024ac4]:
 for flips in range(4):
  for case in range(30):
   xy=[rng.randint(-1000,10000)*256,rng.randint(-100,1000)*256];tick=rng.randint(0,10000);u.mem_write(0x02007000,struct.pack('<2i',*xy));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x0203f000,struct.pack('<I',flips>>1));o.call(0x08001730,o.actor,definition,0x02007000,flips&1)
   o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];o.vm=struct.unpack('<I',u.mem_read(o.actor+0x1cc,4))[0]
   s=(I*80)();vm=(I*64)();assert init((I*2)(*xy),flips,definition,tick,fetch,None,s,vm)==0
   diff={i:(s[i],v)for i,v in o.snapshot().items()if s[i]!=v};assert not diff,(hex(definition),flips,diff)
   assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(s[30:32])==list(u.mem_read(o.actor+0x174,2));constructorCases+=1
surfaceCases=0
for case in range(4000):
 s=(I*80)();s[0:2]=[rng.randint(-1000000,1000000)for _ in range(2)];s[30:32]=[rng.randrange(256),rng.randrange(256)];s[18]=rng.randrange(2);s[39]=rng.randrange(256);s[60:62]=[rng.randint(-2000,2000)for _ in range(2)];existing=rng.randrange(17);o.heap=0x02010000
 u.mem_write(o.actor+0x174,bytes(s[30:32]));u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x188,struct.pack('<2i',*s[60:62]));u.mem_write(o.actor+0x15d,bytes([s[39]]));u.mem_write(o.sprite+0x28,bytes([s[18]]));u.mem_write(0x0200a000,bytes(0x100));u.mem_write(0x0200a090,struct.pack('<i',existing));o.call(0x080017c8,o.actor,0x0200a000)
 n=struct.unpack('<i',u.mem_read(0x0200a090,4))[0]-existing;expected=[]
 for i in range(existing,existing+n):
  p,owner=struct.unpack('<2I',u.mem_read(0x0200a000+i*8,8));assert owner==o.actor;values=list(struct.unpack('<6i',u.mem_read(p,24)));aux=values.pop();expected+=values+[int(bool(aux))]+(list(struct.unpack('<2i',u.mem_read(aux,8)))+[u.mem_read(aux+8,1)[0]]if aux else[0,0,0])
 flags=I(s[39]);out=(I*36)();actual=surface(s,existing,C.byref(flags),out);assert actual==n and list(out[:actual*9])==expected and flags.value==u.mem_read(o.actor+0x15d,1)[0],(case,s[18],s[39],expected,list(out[:actual*9]));surfaceCases+=1
report=dict(original_constructor_cases=constructorCases,original_surface_cases=surfaceCases,mismatches=0,scope='1730 exact anchor/body/animation/flip/flags plus17C8 source special and flat-surface geometry, motion auxiliary fields and16-segment cap. Allocator is a fixture; full chapter route not certified.')
(ROOT/'docs/slope_actors_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
