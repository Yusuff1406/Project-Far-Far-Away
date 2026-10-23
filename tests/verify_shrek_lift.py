#!/usr/bin/env python3
"""Actual type3 lift phases and frame attachment versus original Thumb code."""
import ctypes,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;ctx=struct.unpack_from('<I',o.r.data,0x11230)[0];u.mem_write(ctx,bytes(32));u.mem_write(ctx+8,struct.pack('<I',0x02006000));u.mem_write(0x02006000,bytes(32));u.mem_write(0x02006015,bytes([4]));u.mem_write(0x0203f000,bytes(16));held=pressed=0;allowed=[True,True];accepted=1;nativeEvents=[];originalEvents=[]
 def hook(uc,a,size,data):
  value=None
  if a in (0x0800bec0,0x0800bf04):value=0
  elif a in (0x0800fadc,):value=held
  elif a==0x0800fb2c:value=0x02007400
  elif a==0x0800e0a4:value=int(allowed[0])
  elif a==0x0800e108:value=int(allowed[1])
  elif a==0x08013a54:originalEvents.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12))));value=accepted
  if value is not None:uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);o.call(0x080111cc,o.actor,0x0804b714,35*256,350*256);assert struct.unpack('<I',u.mem_read(o.actor,4))[0]==0x02001e6c;o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0]
 # A real generic target vtable supplies its local activation slot; return/guard are fixtures here.
 u.mem_write(0x02007100,struct.pack('<2i',35*256,358*256));u.mem_write(0x02007200,bytes(32));o.call(0x08013714,0x02008000,0x080526a4,0x02007100,0x02007200)
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];enter=lib.s2_shrek_lift_enter;enter.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_uint32,FC,ctypes.c_void_p];phase=lib.s2_shrek_lift_behavior;phase.argtypes=[IP,IP,IP,IP,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,IP,FC,SINK,ctypes.c_void_p];position=lib.s2_shrek_lift_position;position.argtypes=[IP,IP,IP,IP,FC,ctypes.c_void_p]
 @FC
 def fetch(a,out,n,ctx):
  try:raw=u.mem_read(a,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 @SINK
 def sink(kind,address,scale,ctx):assert kind==21 and address==44;nativeEvents.append([0,11,0]);return accepted
 rng=random.Random(40);events=(ctypes.c_int32*3)(1,7,0)
 def seed(state,animation=None):
  nonlocal held,pressed,allowed,accepted
  held=rng.choice([0,16,32,48,2,18,34]);pressed=rng.choice([0,2]);allowed=[bool(rng.randrange(2)),bool(rng.randrange(2))];accepted=rng.randrange(2);s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();at=rng.randrange(-1000,1000);anim=animation or {16:0x0834f3f4,17:0x0834f3c4,18:0x0834f3dc}.get(state,0x0834f25c);assert init((ctypes.c_int32*2)(123*256,350*256),rng.randrange(4),anim,at,fetch,None,s)==0;s[2:14]=[rng.randrange(-3000,3000)for _ in range(12)];s[20]=rng.choice([0,1,255]);s[22]=rng.randrange(s[77]);s[23]=at+rng.randrange(-3,5);s[14]=rng.randrange(2);s[64]=rng.randrange(2);s[15]=int(not allowed[0]);s[16]=int(not allowed[1]);s[41:44]=[1,7,1];e[0]=state;status[3]=0;book[6]=44 if state in (16,17,18)else 0;o.seed(s)
  u.mem_write(o.actor+0x178,struct.pack('<2i',*s[:2]));u.mem_write(o.actor+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(o.actor+0x1d8,struct.pack('<i',state));u.mem_write(o.actor+0x1e8,struct.pack('<I',0x0804b714));u.mem_write(o.actor+0x1ec,bytes(4));u.mem_write(o.actor+0x258,bytes(4));u.mem_write(o.actor+0x264,struct.pack('<I',0x02008000));u.mem_write(o.actor+0x260,bytes(4));u.mem_write(o.actor+0x25c,bytes(4));u.mem_write(o.actor+0x204,bytes(4));u.mem_write(o.actor+0x20c,bytes(1));u.mem_write(o.actor+0x228,struct.pack('<3i',*events));u.mem_write(0x0200324c,struct.pack('<i',at));u.mem_write(0x020033e0,struct.pack('<i',at));u.mem_write(0x02007400,bytes([held])+bytes(7)+bytes([pressed])+bytes(7));u.mem_write(0x020031a8,bytes(1));nativeEvents.clear();originalEvents.clear();return s,e,status,book,at
 def compare(data,label):
  s,e,status,book,at=data;expected=[list(struct.unpack('<12i',u.mem_read(o.component,48))),u.mem_read(o.sprite,1)[0],list(struct.unpack('<4i',u.mem_read(o.sprite+4,16))),list(struct.unpack('<3i',u.mem_read(o.actor+0x1a0,12))),struct.unpack('<i',u.mem_read(o.actor+0x1d8,4))[0],*[struct.unpack('<i',u.mem_read(o.actor+off,4))[0]for off in (0x260,0x25c,0x204)],44 if struct.unpack('<I',u.mem_read(o.actor+0x264,4))[0]else 0];actual=[list(s[2:14]),s[20],[s[21],s[47],s[22],s[23]],list(s[41:44]),e[0],book[0],book[1],book[3],book[6]];assert actual==expected,(label,actual,expected);assert originalEvents==nativeEvents,(label,originalEvents,nativeEvents)
 for i in range(1000):
  data=seed(0);s,e,status,book,at=data;o.call(0x080110c0,o.actor);assert enter(s,e,book,44,at,0x0804b73c,fetch,None)==0;compare(data,('enter',i))
 for state,code in [(16,0x08010f80),(17,0x08010aec),(18,0x08010958)]:
  for i in range(1000):
   data=seed(state);s,e,status,book,at=data;o.call(code,o.actor);assert phase(s,e,status,book,held,pressed,int(not allowed[0]),int(not allowed[1]),at,at,0x0804b73c,events,fetch,sink,None)==0;compare(data,(state,i))
 positions=0;bank=json.loads((ROOT/'sprites/shrek_ogre/bank.json').read_text());markerCases=0
 for anim in bank['animations']:
  for index in range(anim['sequence_count']):
   for flip in range(4):
    data=seed(18,0x08000000+anim['record_offset']);s,e,status,book,at=data;s[18]=flip&1;s[38]=(flip>>1)&1;s[22]=index;o.seed(s);target=(ctypes.c_int32*80)();target[30]=rng.randrange(8,80);target[31]=rng.randrange(8,80);u.mem_write(0x02008174,bytes([target[30],target[31]]));o.call(0x08010640,0x02007700,o.actor);expected=list(struct.unpack('<2i',u.mem_read(0x02007700,8)));assert position(s,target,book,e,fetch,None)==0;assert list(target[:2])==expected,(anim['index'],index,flip,list(target[:2]),expected);assert [book[7],e[7]]==expected;positions+=1
 report={'original_phase_cases':4000,'frame_position_cases':positions,'mismatches':0,'scope':'Real type3 ctor/vtable, lift entry110C0, phases16..18, release event11 and10640/18460 attachment geometry for every ogre animation/frame/facing. Input/probe answers and generic activation acceptance are fixtures; integrated pickup/script tests are separate. No Android/device execution.'};(ROOT/'docs/shrek_lift_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
