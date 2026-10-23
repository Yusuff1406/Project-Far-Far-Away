#!/usr/bin/env python3
"""Compare real01688 construction and0159C overlap/category/removal against native."""
import ctypes,json,struct,sys
from verify_generic_runtime import *
def main():
 o=Original(Rom(sys.argv[1]));o.camera_fixture=False;u=o.u;l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=l.s2_dialogue_trigger_init;init.argtypes=[IP,FC,ctypes.c_void_p,IP];contact=l.s2_dialogue_trigger_contact;contact.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,FC,ctypes.c_void_p,IP]
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
  return 1
 packets=[];removals=[]
 def hook(uc,a,size,data):
  if a==0x800bec0:packets.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12))))
  elif a==0x8009cc0:removals.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
  else:return
  uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);constructors=cases=accepted=0
 for xy in [(31*256,311*256),(0,0),(-256,400*256),(2999*256,0)]:
  u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x2007000,struct.pack('<2i',*xy));o.call(0x8001688,o.actor,0x2007000);s=(ctypes.c_int32*80)();assert init((ctypes.c_int32*2)(*xy),fetch,None,s)==0
  expected=list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert list(s[:2])==expected and list(s[30:32])==list(u.mem_read(o.actor+0x174,2))==[64,128];constructors+=1
  target=0x2008000
  # Exact touching edges, oneQ8 unit either side, interior and distant points.
  for dx in [-73*256,-40*256,-40*256+1,0,40*256-1,40*256,73*256]:
   for dy in [-90*256,-89*256,-89*256+1,0,89*256-1,89*256,90*256]:
    for category in [0,1,11]:
     for removed in [0,1]:
      p=(ctypes.c_int32*80)();p[0]=s[0]+dx;p[1]=s[1]+dy;p[30]=16;p[31]=50;s[40]=removed
      u.mem_write(target,bytes(0x200));u.mem_write(target+0x168,struct.pack('<i',category));u.mem_write(target+0x178,struct.pack('<2i',*p[:2]));u.mem_write(target+0x174,bytes([16,50]));u.mem_write(o.actor+0x15c,bytes([removed]));u.mem_write(o.actor+0x164,struct.pack('<i',1));u.mem_write(o.actor+0x160,struct.pack('<i',71));packets.clear();removals.clear();o.call(0x800159c,o.actor,target)
      packet=(ctypes.c_int32*3)();got=contact(s,p,category,1,fetch,None,packet);assert got==bool(packets),(xy,dx,dy,category,removed,got,packets)
      if got:assert list(packet)==packets[0]==[0,3,0x802598c] and removals==[(71,1)]
      assert u.mem_read(o.actor+0x15c,1)[0]==(removed|bool(packets));accepted+=got;cases+=1
 report={'source_ctor_cases':constructors,'source_contact_cases':cases,'accepted':accepted,'mismatches':0,'scope':'Actual01688/05350 constructor dimensions/center; actual0159C and007E0 boundary/category/removed gates; actual19024 lookup and05168 removal. Only broadcastBEC0 and removal bitmap9CC0 are intercepted to capture packets/notices. World update ordering and Android excluded.'};(ROOT/'docs/intro_trigger_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
