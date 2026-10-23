#!/usr/bin/env python3
"""Original71/72 arithmetic; owner target selection is an explicit fixture."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;target=0x02008000;present=False;calls=[]
 def hook(uc,a,size,data):
  if a==0x080078cc:calls.append(1);uc.reg_write(UC_ARM_REG_R0,target if present else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.ctor(0x0804db40)
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));query=lib.s2_actor_target_query;query.argtypes=[IP,IP,ctypes.c_int,IP]
 rng=random.Random(46);count=0
 for case in range(3000):
  actor=(ctypes.c_int32*80)();xy=(ctypes.c_int32*2)();out=(ctypes.c_int32*1)();actor[0]=rng.randrange(-1000000,1000000);actor[1]=rng.randrange(-1000000,1000000)
  xy[0]=ctypes.c_int32(actor[0]+rng.choice([-257,-256,-255,-1,0,1,255,256,257,rng.randrange(-10000000,10000000)])).value;xy[1]=rng.randrange(-10000000,10000000);present=bool(case%3);u.mem_write(o.actor+0x178,struct.pack('<2i',*actor[:2]));u.mem_write(target+0x178,struct.pack('<2i',*xy));u.mem_write(o.actor+0x2d4,bytes([case%2]))
  for ident in [71,72]:
   calls.clear();expected=o.query(ident);assert calls==[1]
   assert query(actor,xy if present else None,ident,out)==0 and out[0]==ctypes.c_int32(expected).value,(case,ident,out[0],expected)
   count+=1
 result={'original_query_cases':count,'mismatches':0,'scope':'Original13B8C query71 distance and query72 side, signed Q8 arithmetic and no-target defaults. Nearest eligible actor lookup78CC is an explicit fixture returning one supplied target; full category registry/filter activation excluded.'}
 (ROOT/'docs/target_query_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
