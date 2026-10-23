#!/usr/bin/env python3
"""Compare recovered decisions and entry effects with original Thumb routines."""
import ctypes,itertools,json,random,struct,sys,argparse
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x08000000,len(r.data));u.mem_write(0x08000000,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000)
 actor=0x02004000;component=0x02008000;sprite=0x02009000;svtable=0x02009100
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32)
 decide=lib.s2_player_decide;decide.argtypes=[ctypes.c_int,ip,ip,ip];decide.restype=ctypes.c_int
 enter=lib.s2_player_enter;enter.argtypes=[ctypes.c_int]*4+[ip,ip];enter.restype=ctypes.c_int
 inp=None;actions=[];facing=0;mode='decisions';animation=None
 callback_slots=[0x150,0x158,0x160,0x168,0x170,0x178,0x188,0x190,0x1a0,0x1a8,0x1d0,0x1d8]
 # Dedicated return-only fixtures represent observable callback invocations.
 for slot in callback_slots:
  u.mem_write(0x020017cc+slot+4,struct.pack('<I',0x03001201+slot))
 def hook(uc,address,size,data):
  nonlocal facing,animation
  ret=None
  if mode=='decisions':
   if address==0x03001120:facing=uc.reg_read(UC_ARM_REG_R1);ret=0
   elif address in [0x03001200+s for s in callback_slots]:actions.append(address-0x03001200);ret=0
   elif address==0x0800fadc:ret=inp[0]
   elif address in [0x0800ef48,0x0800ef58,0x0800eeec,0x0800eefc]:ret={0x0800ef48:inp[1]&1,0x0800ef58:(inp[1]>>1)&1,0x0800eeec:(inp[1]>>2)&1,0x0800eefc:inp[0]&1}[address]
   elif address in [0x0800e0a4,0x0800e108,0x08004f08,0x08004ec8,0x08004ea8,0x0800df9c,0x0800dffc]:ret=inp[{0x0800e0a4:5,0x0800e108:6,0x08004f08:2,0x08004ec8:3,0x08004ea8:4,0x0800df9c:9,0x0800dffc:10}[address]]
   elif address==0x0800fb2c:ret=0x02009200
   elif address==0x0800fb54:ret=inp[11] # only other state's handler uses this
   elif address==0x0800de8c:actions.append(0x10000);ret=0
   elif address==0x08004e94:actions.append(0x10001);ret=0
   elif address==0x0800edb4:ret=inp[13]==4
   elif address==0x0800ede4:ret=inp[13]==2
   elif address==0x0800ecec:actions.append(0x10000+uc.reg_read(UC_ARM_REG_R1));ret=0
  else:
   if address==0x03001120:ret=0
   elif address==0x08016960:animation=uc.reg_read(UC_ARM_REG_R1);ret=0
   elif address==0x0800fadc:ret=inp[0]
  if ret is not None:
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def setup():
  u.mem_write(0x02009200,bytes([inp[0]])+bytes(7)+bytes([inp[1] if len(inp)>1 else 0]));u.mem_write(actor,bytes(0x400));u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x1bc,struct.pack('<I',component));u.mem_write(actor+0x1c0,struct.pack('<I',sprite));u.mem_write(actor+0x1e8,struct.pack('<I',0x0804b73c));u.mem_write(sprite,bytes(0x40));u.mem_write(sprite+0x2c,struct.pack('<I',svtable));u.mem_write(svtable+0x18,struct.pack('<2I',0,0x03001121))
 def run(addr):
  u.reg_write(UC_ARM_REG_R0,actor);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=100000)
  if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original did not return')
 cases=0
 # Exhaustive Boolean predicates and button combinations for grounded handlers.
 for state in [0,1]:
  for held,pressed,bits in itertools.product([0,16,32,48,128,144,160,176],range(8),itertools.product(range(2),repeat=8)):
   ground,left,right,face,clear,drop,active,timer=bits
   inp=[held,pressed,ground,left,right,1-left,1-right,face,active,clear,drop,timer,0,0,0];setup();actions=[];facing=face
   u.mem_write(actor+0x1d4,bytes([active]));u.mem_write(sprite+0x28,bytes([face]));u.mem_write(actor+0x1dc,struct.pack('<i',0));u.mem_write(0x020033e0,struct.pack('<i',100000 if timer else 0))
   run(0x0800d6e0 if state==0 else 0x0800da7c);out=(ctypes.c_int32*16)();nf=(ctypes.c_int32*1)();n=decide(state,(ctypes.c_int32*15)(*inp),out,nf)
   if list(out[:n])!=actions or nf[0]!=facing:raise AssertionError((state,inp,list(out[:n]),actions,nf[0],facing))
   cases+=1
 for state in [2,3,4,5]:
  for held,pressed,ground,vy,finished in itertools.product([0,1,16,32,48,64],range(8),range(2),[-1011,-699,-698,-697,-1,0,1,1792],range(2)):
   inp=[held,pressed,ground,0,0,1,1,0,1,1,0,0,finished,0,vy];setup();actions=[];facing=0;u.mem_write(sprite,bytes([finished]));u.mem_write(component+0x24,struct.pack('<i',vy));run({2:0x0800d12c,3:0x0800d0e8,4:0x0800d0a4,5:0x0800f368}[state]);out=(ctypes.c_int32*16)();nf=(ctypes.c_int32*1)();n=decide(state,(ctypes.c_int32*15)(*inp),out,nf)
   if list(out[:n])!=actions:raise AssertionError((state,inp,list(out[:n]),actions))
   cases+=1
 # Restore original virtual entries for whole entry-routine verification.
 u.mem_write(0x020017cc,r.data[0x708bdc+0x17cc:0x708bdc+0x17cc+0x1e0]);mode='entries';rng=random.Random(202605);entries=0
 for action,buttons,carried in itertools.product([0x150,0x158,0x160,0x168,0x170,0x178,0x1d0],[0,16,32,48],[0,4]):
  for _ in range(10):
   inp=[buttons];setup();values=[rng.randint(-2000,2000) for _ in range(12)];u.mem_write(component,struct.pack('<12i',*values));y=350*256;u.mem_write(actor+0x17c,struct.pack('<i',y));u.mem_write(actor+0x204,struct.pack('<i',y));u.mem_write(actor+0x258,struct.pack('<i',carried));u.mem_write(actor+0x1d8,struct.pack('<i',0));animation=None
   addr=struct.unpack_from('<I',r.data,0x708bdc+0x17cc+action+4)[0];run(addr)
   expected=list(struct.unpack('<12i',u.mem_read(component,48)));fsm=struct.unpack('<i',u.mem_read(actor+0x1d8,4))[0];saved=struct.unpack('<i',u.mem_read(actor+0x204,4))[0]
   p=(ctypes.c_int32*12)(*values);out=(ctypes.c_int32*3)(0,0,y);assert enter(action,buttons,carried,y,p,out)==0
   root=0x34f248;expected_anim=(animation-(0x08000000+root+20))//24
   if list(p)!=expected or out[0]!=fsm or out[1]!=expected_anim or out[2]!=saved:raise AssertionError((hex(action),buttons,carried,list(p),expected,list(out),fsm,expected_anim,saved,hex(animation or 0)))
   entries+=1
 result={'decision_cases':cases,'entry_cases':entries,'mismatches':0,'scope':'Original decision branches with predicate/callback fixtures; entry routines execute original state lookup and axis helpers, sprite selection mocked. Airborne carried-object adjustment omitted (carried state 2). Metadata, sound, idle specials and combat not integrated.'}
 (ROOT/'docs/player_states_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
