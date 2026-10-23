#!/usr/bin/env python3
"""Actual13600 NPC constructor/135E0 script versus selected native frames."""
import ctypes,json,struct,sys
from verify_generic_runtime import *
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 r=Rom(sys.argv[1]);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=l.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=l.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];react=l.s2_reactions_init;react.argtypes=[ctypes.c_int32,IP]
 step=l.s2_generic_runtime_step_empty_dynamic;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK]
 l.s2_dialogue_lookup.argtypes=[ctypes.c_int32,FC,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 defs={92:0x8024f48,100:0x8024f88,101:0x8024f80};frames=0;requests=[]
 for row in [x for x in json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects']if x['type']in defs]:
  for flip in range(2):
   for accepted in [False,True]:
    o=Original(r);u=o.u;expected=[];actual=[]
    def hook(uc,a,size,data):
     ret=None
     if a==0x800bec0:
      expected.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12))));ret=0
     if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);xy=tuple(v*256 for v in row['anchor_px']);u.mem_write(0x2007000,struct.pack('<2i',*xy));u.mem_write(0x203f000,struct.pack('<I',flip>>1));o.call(0x8013600,o.actor,defs[row['type']],0x2007000,flip&1)
    o.sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];o.component=struct.unpack('<I',u.mem_read(o.actor+0x1bc,4))[0];o.vm=struct.unpack('<I',u.mem_read(o.actor+0x1cc,4))[0]
    @FC
    def fetch(a,out,n,ctx):
     for i,v in enumerate(struct.unpack('<'+'i'*n,u.mem_read(a,n*4))):out[i]=v
     return 1
    @RC
    def rnd(ctx):return 37
    @REG
    def reg(value,ctx):raise AssertionError('unexpected registration')
    @SINK
    def sink(kind,address,scale,ctx):
     assert kind==26;out=ctypes.c_uint32();assert l.s2_dialogue_lookup(ctypes.c_int32(address),fetch,None,ctypes.byref(out))==0;actual.append([0,3,out.value]);return 0
    s=(ctypes.c_int32*80)();vm=(ctypes.c_int32*64)();reactions=(ctypes.c_int32*72)();anim=struct.unpack_from('<I',r.data,defs[row['type']]-ROM_BASE)[0];assert init((ctypes.c_int32*2)(*xy),flip,anim,0,fetch,None,s)==0;react(row['word8_actor_tag'],reactions);start(0x8025000,vm);u.mem_write(o.actor+0x164,struct.pack('<i',reactions[5]))
    for t in range(1,181):
     if accepted and t==100:s[40]|=16;u.mem_write(o.actor+0x15c,bytes([u.mem_read(o.actor+0x15c,1)[0]|16]))
     for a in [0x200324c,0x20033e0]:u.mem_write(a,struct.pack('<i',t))
     expected.clear();actual.clear();o.call(0x80135e0,o.actor);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,t,3200*256,400*256,fetch,rnd,None,4096,reactions,reg,sink)==0,(row['instance_id'],flip,t)
     diff={i:(s[i],v)for i,v in o.snapshot().items()if s[i]!=v};assert not diff,(row['instance_id'],flip,t,diff)
     assert list(s[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)))
     assert list(vm[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)));assert actual==expected,(t,actual,expected);requests.extend(actual);frames+=1
    assert bool(requests)or not accepted
 report={'original_npc_frames':frames,'types':list(defs),'dialogue_requests':len(requests),'mismatches':0,'scope':'Real13600/135E0 constructors, static physics, VM, animation and17->19024->BEC0 packets. Accepted-contact pending flag supplied on tick100 as a fixture; player/UI manager/whole-world contacts excluded.'};(ROOT/'docs/npc_script_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
