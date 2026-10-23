#!/usr/bin/env python3
"""Selected effects compared with full original ogre ctor and incoming E3A0."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();o=Original(Rom(args.rom));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(202616)
 init=lib.s2_shrek_reactions_init;init.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32];receive=lib.s2_shrek_receive;receive.argtypes=[IP,IP,IP,ctypes.c_int32];defaults=lib.s2_shrek_event_defaults;defaults.argtypes=[IP];events=(ctypes.c_int32*18)();assert defaults(events)==0
 broadcasts=[]
 def hook(uc,address,size,data):
  if address==0x0800bec0:
   broadcasts.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12))));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);ctorCases=0
 for count in range(256):
  for flips in range(4):
   for tick in [0,12345]:
    o.heap=0x02010000;u.mem_write(o.actor,bytes(0x1000));u.mem_write(0x02003160,bytes(32));u.mem_write(0x02003168,struct.pack('<I',0x02006000));u.mem_write(0x02006000,bytes(32));u.mem_write(0x02006015,bytes([count]));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0203f000,bytes([flips&1,0,0,0,(flips>>1)&1])+bytes(11));broadcasts.clear()
    o.call(0x0800d24c,o.actor,0x0804b73c,rng.randint(40,400)*256,rng.randint(60,350)*256)
    s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)(*[77]*8);status=(ctypes.c_int32*8)(*[99]*8);assert init(s,e,status,count,tick)==0
    actual=[list(s[41:44]),e[0],e[1],e[3],list(e[4:7]),list(status[:6])];expected=[list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x258,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x1ec,4))[0],list(struct.unpack('<3i',u.mem_read(o.actor+0x21c,12))),[struct.unpack('<i',u.mem_read(o.actor+0x200,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x1fc,4))[0],u.mem_read(o.actor+0x1e4,1)[0],u.mem_read(o.actor+0x20c,1)[0],struct.unpack('<i',u.mem_read(o.actor+0x1d0,4))[0],u.mem_read(o.actor+0x1c8,1)[0]]];assert actual==expected,(count,flips,tick,actual,expected)
    assert list(events)==list(struct.unpack('<18i',u.mem_read(o.actor+0x210,72)));assert broadcasts==[[2,2,0x02003160]];ctorCases+=1
 accepted=0;ids=list(range(15,24))+[25,27,29,33,34,35,36,-1,0,14,42,2147483647,-2147483648];incomingCases=10000
 for case in range(incomingCases):
  e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();e[0]=rng.choice(list(range(18))+[-1,-2147483648]);e[1]=rng.randrange(9);e[3]=77 if case%3 else 0;status[0]=rng.choice([-2147483648,-1,0,3,2147483647]);status[1]=rng.choice([-2147483648,-1,0,3,2147483647]);status[2]=rng.randrange(256);status[3]=rng.randrange(256);status[4]=rng.randint(-10000,10000);status[5]=rng.randrange(256);tick=rng.randint(-10000,10000);event=(ctypes.c_int32*3)(rng.randint(-5,10),rng.choice(ids),rng.randint(-10000,10000))
  for off,value in [(0x1d8,e[0]),(0x258,e[1]),(0x1ec,0x02006000 if e[3] else 0),(0x200,status[0]),(0x1fc,status[1]),(0x1d0,status[4])]:u.mem_write(o.actor+off,struct.pack('<i',value))
  u.mem_write(o.actor+0x1c8,bytes([status[5]]));u.mem_write(o.actor+0x1e4,bytes([status[2]]));u.mem_write(o.actor+0x20c,bytes([status[3]]));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x02007300,struct.pack('<3i',*event));o.call(0x0800e3a0,o.actor,0x02007300);result=receive(e,status,event,tick)
  expected=[u.reg_read(UC_ARM_REG_R0),struct.unpack('<i',u.mem_read(o.actor+0x258,4))[0],struct.unpack('<i',u.mem_read(o.actor+0x1fc,4))[0],u.mem_read(o.actor+0x1e4,1)[0],u.mem_read(o.actor+0x20c,1)[0],struct.unpack('<i',u.mem_read(o.actor+0x1d0,4))[0],u.mem_read(o.actor+0x1c8,1)[0]];actual=[result,e[1],status[1],status[2],status[3],status[4],status[5]];assert actual==expected,(case,list(event),actual,expected,e[0]);accepted+=result
 # Supported early refusals in branches whose later actions remain unported.
 gated=0
 for id,state,mode,immune,tick in [(24,13,0,0,0),(26,12,0,0,0),(31,0,5,0,0),*[(id,0,0,50,49) for id in [37,38,39,41]],*[(id,6,0,0,0) for id in range(15,42) if id!=40]]:
  e=(ctypes.c_int32*8)(state,mode,0,0,0,0,0,0);status=(ctypes.c_int32*8)(0,0,0,0,immune,0,0,0);u.mem_write(o.actor+0x1d8,struct.pack('<i',state));u.mem_write(o.actor+0x258,struct.pack('<i',mode));u.mem_write(o.actor+0x1d0,struct.pack('<i',immune));u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x02007300,struct.pack('<3i',0,id,0));o.call(0x0800e3a0,o.actor,0x02007300);assert receive(e,status,(ctypes.c_int32*3)(0,id,0),tick)==u.reg_read(UC_ARM_REG_R0)==0;gated+=1
 unsupported=0
 for id in [24,26,28,30,31,32,37,38,39,40,41]:
  e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();before=[list(e),list(status)];assert receive(e,status,(ctypes.c_int32*3)(0,id,0),0)==-4;assert before==[list(e),list(status)];unsupported+=1
 result={'full_original_ogre_constructor_cases':ctorCases,'incoming_original_cases':incomingCases,'incoming_accepted':accepted,'original_early_refusal_cases':gated,'native_unported_action_refusals':unsupported,'mismatches':0,'constructor_scope':'Full D24C/D294 executes with original base constructor, animation/motion allocation, event setters and descriptor life values. Allocator, camera and broadcast delivery are fixtures. Native comparison covers six default event triples, base event, logical state, mode, carried ID, life counters, bytes +1E4/+20C/+1C8 and immunity deadline; other constructor/global/lifetime effects are not ported.','incoming_scope':'Original E3A0 ID-only dispatch, state-6 guard, carry handshake IDs15..21, life-counter messages22/23, pending flag25 and ignored IDs; selected original early refusals also execute. Later virtual actions, full incoming damage behavior, group broadcasts and carry release remain unsupported.'};(ROOT/'docs/shrek_reactions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
