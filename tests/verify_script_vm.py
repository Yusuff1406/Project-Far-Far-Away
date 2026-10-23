#!/usr/bin/env python3
"""Original VM scheduling, stack and effects with controlled actor/event fixtures."""
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000)
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ip,ctypes.c_int,ctypes.c_void_p);QC=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ip,ctypes.c_void_p);EC=ctypes.CFUNCTYPE(None,ctypes.c_int,ip,ctypes.c_void_p);RC=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p)
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,ip];start.restype=None;step=lib.s2_vm_step;step.argtypes=[ip,ctypes.c_int32,FC,QC,EC,RC,ctypes.c_void_p,ctypes.c_int];step.restype=ctypes.c_int
 vm=0x02004000;stack=0x02005000;actor=0x02006000;avtable=0x02006100;mode='step';effects=[];randvalue=0;queryValue=0;tick=0
 u.mem_write(actor,struct.pack('<I',avtable));u.mem_write(avtable+0x28,struct.pack('<2I',0,0x03001101))
 def hook(uc,address,size,data):
  ret=None
  if address==0x03001100:
   cmd=list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12)))
   # Query wrappers carry [result target, original payload]. Ordinary effects use ROM/RAM payload.
   if 0x0203e000<=cmd[2]<0x0203f000:
    target,payload=struct.unpack('<2I',uc.mem_read(cmd[2],8));uc.mem_write(target,struct.pack('<i',queryValue))
   else:effects.append((0,cmd))
   ret=0
  elif address==0x0800bec0:effects.append((1,[5,0,uc.reg_read(UC_ARM_REG_R0)]));ret=0
  elif address==0x0800021a:ret=randvalue&0xffffffff
  elif address in [0x0801afec,0x0801af94,0x0801b044]:effects.append(({0x0801afec:13,0x0801af94:14,0x0801b044:15}[address],[5,{0x0801afec:13,0x0801af94:14,0x0801b044:15}[address],uc.reg_read(UC_ARM_REG_R0)]));ret=0
  elif address==0x0801652c:ret=0x02007000
  elif address in [0x080163ac,0x080161b0]:op=11 if address==0x080163ac else 12;effects.append((op,[5,op,uc.reg_read(UC_ARM_REG_R1)]));ret=0
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 @FC
 def fetch(addr,out,n,ctx):
  try:
   values=struct.unpack('<'+'i'*n,u.mem_read(addr,n*4))
   for i,v in enumerate(values):out[i]=v
   return 1
  except Exception:return 0
 @QC
 def query(self,cls,id,payload,out,ctx):out[0]=queryValue
 nativeEffects=[]
 @EC
 def effect(kind,cmd,ctx):nativeEffects.append((kind,list(cmd[:3])))
 @RC
 def rngcb(ctx):return randvalue
 def run(addr,r0,r1=0):
  u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_R1,r1);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000
 def setup(program):
  u.mem_write(vm,bytes(40));u.mem_write(vm,struct.pack('<I',0x0200255c));u.mem_write(vm+0x18,struct.pack('<2I',stack,actor));u.mem_write(stack,bytes(200));u.mem_write(vm+0xc,struct.pack('<i',-1));run(0x08013344,vm,program);s=(ctypes.c_int32*64)();start(program,s);return s
 def check(s):
  raw=struct.unpack('<10i',u.mem_read(vm,40));assert list(s[:4])==[raw[1],raw[2],raw[3],raw[4]],(list(s[:4]),raw)
  for i in range(max(0,s[2]+1)):
   expect=list(struct.unpack('<5i',u.mem_read(stack+i*20,20)));expect[2]&=255;assert list(s[8+i*5:13+i*5])==expect,(i,list(s[8+i*5:13+i*5]),expect)
  assert nativeEffects==effects,(nativeEffects,effects)
 rng=random.Random(202609);cases=0
 # Programs exercise waits, branch/skip, nested calls, restart, interrupts,
 # naming, deadlines, signed random remainder and every external effect opcode.
 for _ in range(1200):
  p=0x02010000;sub=p+0x200;pred=p+0x400;interrupt=pred+32;limit=rng.randint(1,5);queryValue=rng.randint(-5,5);randvalue=rng.randint(-100000,100000)
  predicate=[8,77,123,rng.randint(0,4),rng.randint(-5,5)];u.mem_write(pred,struct.pack('<5i',*predicate));u.mem_write(interrupt,struct.pack('<5i',8,77,123,2,999))
  program=[[5,1,0x0802547c],[5,7,interrupt],[5,16,8],[5,17,0],[5,18,0],[5,2,sub],[5,3,pred],[8,42,123],[5,4,0],[8,43,456],[5,8,limit],[5,9,pred] if queryValue< -10 else [5,10,interrupt],[5,6,0]]
  # Avoid permanent waits for the finite program; flip the interrupt's false predicate after tick 3.
  program[11]=[5,8,1]
  subprogram=[[5,op,rng.randint(0,1000)] for op in [0,11,12,13,14,15]]+[[5,8,2],[5,6,0]]
  u.mem_write(p,b''.join(struct.pack('<3i',*cmd) for cmd in program));u.mem_write(sub,b''.join(struct.pack('<3i',*cmd) for cmd in subprogram));s=setup(p)
  for tick in range(1,21):
   u.mem_write(0x0200324c,struct.pack('<i',tick));effects=[];nativeEffects=[];run(0x08012f9c,vm);code=step(s,tick,fetch,query,effect,rngcb,None,4096);assert code>=0;check(s);cases+=1
   if s[2]<0:break
 branchCases=0
 for variant in range(120):
  p=0x02010000;pred=p+0x400;sub=p+0x200;queryValue=0;randvalue=-257
  # While-true/while-false predicates, restart, and true interrupt unwinding.
  kind=variant%4
  u.mem_write(pred,struct.pack('<5i',8,77,123,2,1))
  program=([[5,9,pred],[5,6,0]] if kind==0 else [[5,10,pred],[5,6,0]] if kind==1 else [[5,8,2],[8,42,123],[5,5,0]] if kind==2 else [[5,7,pred],[5,2,sub],[5,6,0]])
  subprogram=[[5,8,20],[5,6,0]];u.mem_write(p,b''.join(struct.pack('<3i',*cmd) for cmd in program));u.mem_write(sub,b''.join(struct.pack('<3i',*cmd) for cmd in subprogram));s=setup(p)
  for tick in range(1,10):
   queryValue=(1 if tick<4 else 0) if kind==0 else (0 if tick<4 else 1);u.mem_write(0x0200324c,struct.pack('<i',tick));effects=[];nativeEffects=[];run(0x08012f9c,vm);assert step(s,tick,fetch,query,effect,rngcb,None,4096)>=0;check(s);branchCases+=1
   if s[2]<0:break
 # Full stack: rejected eleventh call still resets current frame index.
 p=0x02010000
 for level in range(11):u.mem_write(p+level*32,struct.pack('<6i',5,2,p+(level+1)*32,5,6,0))
 s=setup(p);effects=[];nativeEffects=[];run(0x08012f9c,vm);assert step(s,tick,fetch,query,effect,rngcb,None,4096)>=0;check(s);branchCases+=1
 compare=lib.s2_vm_compare;compare.argtypes=[ctypes.c_int32,ctypes.c_int,ctypes.c_int32];compare.restype=ctypes.c_int;compareCases=0
 for _ in range(2000):
  queryValue=rng.choice([-2147483648,-1,0,1,2147483647,rng.randint(-1000000,1000000)]);rhs=rng.choice([-2147483648,-1,0,1,2147483647,rng.randint(-1000000,1000000)]);comparison=rng.randint(-1,6);pred=0x02010400;u.mem_write(pred,struct.pack('<5i',8,77,123,comparison,rhs));setup(p);run(0x08013198,vm,pred);expected=u.reg_read(UC_ARM_REG_R0);assert compare(queryValue,comparison,rhs)==expected;compareCases+=1
 # Real initial scripts, with fixture actor responses; stop at a bounded time.
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];sourceCases=0
 for typ in ['18','39','57','89']:
  definition=bindings[typ]['definition'];program=struct.unpack_from('<I',r.data,definition-ROM_BASE+4)[0];s=setup(program);queryValue=0;randvalue=37
  for tick in range(1,181):
   u.mem_write(0x0200324c,struct.pack('<i',tick));effects=[];nativeEffects=[];run(0x08012f9c,vm);code=step(s,tick,fetch,query,effect,rngcb,None,4096);assert code>=0,(typ,tick,code);check(s);sourceCases+=1
   if s[2]<0:break
 result={'synthetic_step_cases':cases,'branch_stack_steps':branchCases,'predicate_comparison_cases':compareCases,'source_script_steps':sourceCases,'source_types':[18,39,57,89],'mismatches':0,'scope':'Original interpreter and internal command bodies run; actor query/message, audio, random and global event targets mocked. Native fetch reads supplied resource memory. Whole object behavior depends on receiver handlers not implemented here.'};(ROOT/'docs/script_vm_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
