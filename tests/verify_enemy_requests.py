#!/usr/bin/env python3
"""Enemy command transport through the real C++ VM; no original CPU/device run."""
import ctypes, hashlib, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
I=ctypes.c_int32; IP=ctypes.POINTER(I)
FETCH=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_int,ctypes.c_void_p)
RANDOM=ctypes.CFUNCTYPE(I,ctypes.c_void_p)
REGISTRY=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p)
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,I,ctypes.c_void_p)
def main():
 raw=Path(sys.argv[1]).read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='2ec32cb8c69ff8bbe01b7039ee001105f92ee686b251d26060f9bdb6751f3b80'
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 program=0x02007800; memory={}; requests=[]; failure=0
 @FETCH
 def fetch(addr,out,n,ctx):
  if 0x08000000<=addr<=0x08000000+len(raw)-n*4:data=raw[addr-0x08000000:addr-0x08000000+n*4]
  elif program<=addr and addr+n*4<=program+len(memory.get('program',b'')):data=memory['program'][addr-program:addr-program+n*4]
  else:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,data)):out[i]=v
  return 1
 @RANDOM
 def random(ctx):return 37
 @REGISTRY
 def registry(enabled,ctx):raise AssertionError('No registration in this fixture')
 @SINK
 def sink(kind,address,scale,ctx):
  count=2 if kind==22 else 5 if kind==23 else 0
  descriptor=(I*count)()
  if count and not fetch(address,descriptor,count,None):return -2
  requests.append([kind,address,scale,list(descriptor)])
  return failure
 world=lib.s2_generic_world_message;world.argtypes=[IP,ctypes.c_int,ctypes.c_int,I,FETCH,SINK,ctypes.c_void_p]
 message=lib.s2_generic_message;message.argtypes=[IP,ctypes.c_int,ctypes.c_int,I,I,FETCH,ctypes.c_void_p]
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,I,FETCH,ctypes.c_void_p,IP]
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP]
 step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,I,I,I,FETCH,RANDOM,ctypes.c_void_p,ctypes.c_int,IP,REGISTRY,SINK]
 pose=(I*80)();baseline=list(pose)
 assert world(pose,8,16,0x08050f70,fetch,sink,None)==0
 assert requests.pop()==[22,0x08050f70,0,[9,4]]
 assert world(pose,8,48,0x08050f7c,fetch,sink,None)==0
 assert requests.pop()==[23,0x08050f7c,0,[71,1,0,0,0]]
 for ident in [16,48]:
  assert world(pose,8,ident,0x01000000,fetch,sink,None)==-2
  assert not requests
 assert world(pose,8,49,123,fetch,sink,None)==0 and not requests
 assert list(pose)==baseline
 cases=0
 for secondary in [0,90]:
  for failure in [0,-7]:
   for tick in range(1,65):
    requests.clear();pose=(I*80)();vm=(I*64)();reactions=(I*72)()
    assert init((I*2)(1007*256,227*256),1,0x0831de48,0,fetch,None,pose)==0
    pose[79]=secondary;pose[71]=123 # last ceiling contact is not an auxiliary child
    commands=[[8,55,0],[8,16,0x08050f70],[8,48,0x08050f7c],[8,49,0],[5,6,0]]
    memory['program']=b''.join(struct.pack('<3i',*c) for c in commands)
    start(program,vm)
    result=step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),pose,vm,tick,3200*256,400*256,fetch,random,None,4096,reactions,registry,sink)
    assert result==failure,(secondary,failure,tick,result)
    expected=[[22,0x08050f70,0,[9,4]]]
    if not failure:
     expected.append([23,0x08050f7c,0,[71,1,0,0,0]])
     if secondary:expected.append([24,90,0,[]])
    assert requests==expected,(requests,expected)
    cases+=1
 assert message(pose,8,55,1,0,fetch,None)==-4
 report={'vm_transport_cases':cases,'mismatches':0,'source_packets':{'broadcast':[9,4],'reward':[71,1,0,0,0]},'scope':'Native VM transport and owner-error propagation using real ROM descriptors and enemy animation. No original ARM execution, recipient delivery, spawned actor, combat, Android build or device test.'}
 (ROOT/'docs/enemy_request_transport_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
