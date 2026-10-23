"""144 native ctor/notice/step versus original16EDC/16E80/16E08."""
import ctypes as C,struct,json,sys,random
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
o=Original(Rom(sys.argv[1]));u=o.u;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32
init=l.s2_target_generator_init;init.argtypes=[IP,I,IP,IP];step=l.s2_target_generator_step;step.argtypes=[IP];notice=l.s2_target_generator_notice;notice.argtypes=[IP,IP]
# A real generic child provides the original sprite/motion interface. Allocation
# and owner registration are hooks; the actual generator functions run intact.
child=0x02008000;anchor=0x02007000;flags=0x02007100
u.mem_write(anchor,struct.pack('<2i',13*256,54*256));u.mem_write(flags,bytes(32));o.call(0x08013714,child,0x0804a4e8,anchor,flags)
requests=[];registrations=[]
def hook(uc,a,size,ctx):
 ret=None
 if a==0x080059d8:requests.append((uc.reg_read(UC_ARM_REG_R0),*struct.unpack('<2i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8))));ret=child
 elif a==0x0800bf04:registrations.append(1);ret=0
 elif a in[0x08007ac4,0x08009358,0x08009284]:ret=0
 if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook);cases=0
for variant in[0,1]:
 u.mem_write(o.actor,bytes(468));registrations.clear();o.call(0x08016edc,o.actor,anchor,variant,0);state=(I*5)();xy=(I*2)();assert init((I*2)(13*256,54*256),variant,xy,state)==0
 assert list(xy)==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)));assert registrations==([1]if variant else [])
 def compare():
  expected=list(struct.unpack('<4i',u.mem_read(o.actor+0x1c0,16)))+[u.mem_read(o.actor+0x1d0,1)[0]]
  assert list(state)==expected,(list(state),expected)
 compare();cases+=1
 for tick in range(1,1201):
  if tick%13==0:
   packet=[2,3 if tick%26 else 9,0];u.mem_write(0x02007200,struct.pack('<3i',*packet));o.call(0x08016e80,o.actor,0x02007200);assert notice(state,(I*3)(*packet))==0;compare();cases+=1
  requests.clear();o.call(0x08016e08,o.actor);kind=step(state);compare()
  assert requests==([(kind,*xy)]if kind else []),(variant,tick,kind,requests)
  if kind:
   component=struct.unpack('<I',u.mem_read(child+0x1bc,4))[0];triple=list(struct.unpack('<3i',u.mem_read(component+12,12)));expected=[-state[0]if variant else state[0],state[1],-state[2]if variant else state[2]];assert triple==expected
  cases+=1
report=dict(original_cases=cases,variants=2,mismatches=0,scope='144 ctor edge spawn, first/60-frame cadence, source speed triple, score-notice filtering and639 threshold. Real child interface; allocation and registration owner hooks.')
(ROOT/'docs/target_generator_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
