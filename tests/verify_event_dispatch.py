#!/usr/bin/env python3
import argparse,ctypes,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_map(0x03000000,0x2000)
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);up=ctypes.POINTER(ctypes.c_uint32);EC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ip,ctypes.c_void_p);DC=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_void_p)
 broad=lib.s2_event_broadcast;broad.argtypes=[up,ip,ctypes.c_int,ip,EC,ctypes.c_void_p];broad.restype=ctypes.c_int
 add=lib.s2_deferred_add;add.argtypes=[ctypes.c_uint32,up,ip];add.restype=ctypes.c_int;drain=lib.s2_deferred_run;drain.argtypes=[up,ip,DC,ctypes.c_void_p];drain.restype=ctypes.c_int
 manager=0x02004000;eventptr=0x02006000;receipts=[];deferred=[];extra=None
 countptr=struct.unpack_from('<I',r.data,0xbcc4)[0];itemptr=struct.unpack_from('<I',r.data,0xbcc8)[0]
 def hook(uc,address,size,data):
  if address==0x03001100:
   receipts.append((uc.reg_read(UC_ARM_REG_R0),list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12)))));uc.reg_write(UC_ARM_REG_R0,len(receipts)&1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif address==0x03001120:
   deferred.append(uc.reg_read(UC_ARM_REG_R0))
   if extra is not None and len(deferred)==1:
    n=struct.unpack('<i',uc.mem_read(countptr,4))[0]
    if n<8:uc.mem_write(itemptr+n*4,struct.pack('<I',extra));uc.mem_write(countptr,struct.pack('<i',n+1))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def run(addr,r0,r1=0):
  u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_R1,r1);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000
 rng=random.Random(202617);broadcastCases=0
 for _ in range(1000):
  n=rng.randint(0,16);event=[rng.randint(-10000,10000) for _ in range(3)];receivers=[0x02008000+rng.randint(0,15)*0x100 for _ in range(n)];adjustments={x:rng.randint(-32768,32767) for x in receivers};sentinel=manager+4;u.mem_write(manager+8,struct.pack('<I',0x02005000 if n else sentinel));u.mem_write(eventptr,struct.pack('<3i',*event))
  for i,x in enumerate(receivers):
   node=0x02005000+i*16;vt=0x0200b000+(x-0x02008000)//0x100*0x40;u.mem_write(node,struct.pack('<2I',x,node+16 if i<n-1 else sentinel));u.mem_write(x,struct.pack('<I',vt));u.mem_write(vt+0x28,struct.pack('<hHI',adjustments[x],0,0x03001101))
  receipts=[];run(0x0800bcf0,manager,eventptr);native=[]
  @EC
  def cb(receiver,e,context):native.append((receiver,list(e[:3])));return len(native)&1
  ids=(ctypes.c_uint32*n)(*receivers);adj=(ctypes.c_int32*n)(*(adjustments[x] for x in receivers));assert broad(ids,adj,n,(ctypes.c_int32*3)(*event),cb,None)==n;assert native==receipts;broadcastCases+=1
 addCases=0;drainCases=0
 for _ in range(500):
  items=(ctypes.c_uint32*8)();count=(ctypes.c_int32*1)(0);u.mem_write(countptr,struct.pack('<i',0));u.mem_write(itemptr,bytes(32))
  for i in range(rng.randint(0,14)):
   value=0x02008000+rng.randint(0,15)*0x100;run(0x0800bccc,value);add(value,items,count);assert count[0]==struct.unpack('<i',u.mem_read(countptr,4))[0] and list(items)==list(struct.unpack('<8I',u.mem_read(itemptr,32)));addCases+=1
  extra=0x02009000 if rng.randint(0,1) else None
  for x in set(list(items[:count[0]])+[extra or 0x02009000]):
   u.mem_write(x,struct.pack('<I',0x0200c000));u.mem_write(0x0200c000+0x20,struct.pack('<2I',0,0x03001121))
  deferred=[];run(0x0800bc94,0);native=[]
  @DC
  def callback(x,context):
   native.append(x)
   if extra is not None and len(native)==1:add(extra,items,count)
  drain(items,count,callback,None);assert native==deferred and count[0]==0 and struct.unpack('<i',u.mem_read(countptr,4))[0]==0;drainCases+=1
 result={'broadcast_cases':broadcastCases,'deferred_add_cases':addCases,'deferred_drain_cases':drainCases,'mismatches':0,'original_functions':['0x0800BCF0','0x0800BCCC','0x0800BC94'],'scope':'Stable listener-list broadcast, preserving duplicates, signed this-adjustment and callback order; callback return ignored. Eight-slot pending calls including append during drain. List registration/removal/mutation and concrete game event handlers not ported.'}
 (ROOT/'docs/event_dispatch_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
