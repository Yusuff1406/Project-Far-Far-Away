#!/usr/bin/env python3
"""Original19024 and dialogue VM branches; UI readiness is an explicit fixture."""
import ctypes,struct,json,sys
from verify_generic_runtime import *
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));lookup=l.s2_dialogue_lookup;lookup.argtypes=[ctypes.c_int32,FC,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];start=l.s2_dialogue_start;start.argtypes=[ctypes.c_uint32,IP];step=l.s2_dialogue_step;step.argtypes=[IP,ctypes.c_int32,ctypes.c_int,ctypes.c_int,FC,ctypes.c_void_p]
 vm=0x2004000;stack=0x2005000;actor=0x2006000;vtable=0x2006100;pressed=0;done=1;expected=[0,0,0,0,0,0]
 u.mem_write(actor,struct.pack('<I',vtable));u.mem_write(vtable+0x28,struct.pack('<2I',0,0x3001101))
 def hook(uc,a,size,data):
  if a==0x800bec0:
   packet=list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12)));assert packet==[0,13,0],packet;expected[5]=1;uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if a!=0x3001100:return
  cmd=list(struct.unpack('<3I',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12)))
  if 0x203e000<=cmd[2]<0x203f000:
   target,payload=struct.unpack('<2I',uc.mem_read(cmd[2],8));assert(cmd[0],cmd[1])in[(4,1),(7,5)];uc.mem_write(target,struct.pack('<i',pressed if cmd[0]==4 else done))
  elif cmd[:2]==[10,0]:expected[0]=cmd[2];expected[4]=0
  elif cmd[:2]==[10,1]:expected[4]=1
  elif cmd[:2]==[7,2]:expected[1]=cmd[2];expected[2]+=1
  elif cmd[:2]==[7,3]:expected[3]+=1
  else:raise AssertionError(cmd)
  uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
  return 1
 lookups=0;frames=0;scenarios=[]
 for ident in range(-10,111):
  o.call(0x8019024,ident);out=ctypes.c_uint32();assert lookup(ident,fetch,None,ctypes.byref(out))==0 and out.value==u.reg_read(UC_ARM_REG_R0);lookups+=1
 for ident in [1,61,67,68,69]:
  for pattern in ['complete','partial','cancel','hold']:
   program=ctypes.c_uint32();assert lookup(ident,fetch,None,ctypes.byref(program))==0;s=(ctypes.c_int32*80)();assert start(program.value,s)==0;expected[:]=[0]*6
   u.mem_write(vm,bytes(40));u.mem_write(vm,struct.pack('<I',0x200255c));u.mem_write(vm+0x18,struct.pack('<2I',stack,actor));u.mem_write(vm+0xc,struct.pack('<i',-1));u.mem_write(stack,bytes(200));o.call(0x8013344,vm,program.value)
   for tick in range(180):
    pressed=(8 if tick==2 else 0)if pattern=='cancel'else 1 if(pattern!='hold'and tick%8==4)or(pattern=='hold'and tick==4)else 0;done=not(pattern=='partial'and tick<30);u.mem_write(0x200324c,struct.pack('<i',tick));o.call(0x8012f9c,vm);assert step(s,tick,pressed,done,fetch,None)==0
    assert list(s[:4])==list(struct.unpack('<4i',u.mem_read(vm+4,16))),(ident,pattern,tick,list(s[:4]))
    for depth in range(s[2]+1):
     frame=list(struct.unpack('<5i',u.mem_read(stack+depth*20,20)));frame[2]&=255;assert list(s[8+depth*5:13+depth*5])==frame
    assert[s[65],s[66],s[67],s[72],s[79],s[73]]==expected,(ident,pattern,tick)
    assert s[64]==(s[2]>=0);frames+=1
    if not s[64]:break
   if pattern=='hold'and ident in [61,68,69]:assert s[64]
   elif pattern!='hold':assert not s[64],(ident,pattern)
   scenarios.append({'dialogue_id':ident,'pattern':pattern,'last_tick':tick,'text_messages':s[67]})
 report={'lookup_cases':lookups,'original_vm_frames':frames,'scenarios':scenarios,'mismatches':0,'scope':'Original19024 table/default and12F9C interpreter/stack with original1/61/67/68/69 scripts and0/13 bonus packet. Input and text-completion queries, portrait/text handlers are explicit UI fixtures; native presentation speed/pagination and Android execution excluded.'};(ROOT/'docs/dialogue_vm_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
