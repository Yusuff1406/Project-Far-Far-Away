#!/usr/bin/env python3
"""Type57 bandit script runtime versus original Thumb, isolated owners."""
import ctypes,json,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC,RC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p)
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 rom=Rom(sys.argv[1]);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
 init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP]
 start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP]
 react=lib.s2_reactions_init;react.argtypes=[ctypes.c_int32,IP]
 activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP]
 point=lib.s2_actor_spawn_point_q8;point.argtypes=[IP,FC,ctypes.c_void_p,IP]
 step=lib.s2_generic_runtime_step_target;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK,IP,ctypes.POINTER(ctypes.c_bool)]
 rows=[x for x in json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'] if x['type']==57]
 scenarios=[];total=0;audio=set()
 for row in rows:
  for flip in [0,1]:
   for mode in ['far','near','hit']:
    hit=mode=='hit'
    o=Original(rom);u=o.u;target=(ctypes.c_int32*2)((row['anchor_px'][0]-32)*256,row['anchor_px'][1]*256)
    if mode=='far':target[:]=[35*256,350*256]
    expected=[];actual=[];auxiliary=ctypes.c_bool(False);originalAux=[False];oreg=[];nreg=[];tick=0
    def hook(uc,a,size,data):
     ret=None
     if a==0x08013910:
      animation=uc.reg_read(UC_ARM_REG_R1)
      if animation or originalAux[0]:expected.append([25,animation])
      originalAux[0]=bool(animation);ret=0
     elif a==0x080078cc:ret=0x02008000
     elif a in [0x0800bf04,0x0800bee8]:oreg.append(1 if a==0x0800bf04 else 0);ret=0
     elif a==0x080163ac:expected.append([11,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);ret=0
     elif a==0x0800bec0:expected.append([22,*struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12))]);ret=0
     elif a==0x080059d8:
      kind=uc.reg_read(UC_ARM_REG_R0);xy=list(struct.unpack('<2i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8)))
      if kind==71:expected.append([23,kind,*xy,*struct.unpack('<4i',uc.mem_read(uc.reg_read(UC_ARM_REG_R2),16))])
      else:expected.append([24,kind,*xy])
      ret=0
     elif a==0x08005168:
      expected.append([19]);uc.mem_write(o.actor+0x15c,bytes([uc.mem_read(o.actor+0x15c,1)[0]|1]));ret=0
     if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    xy=tuple(x*256 for x in row['anchor_px']);o.ctor(0x0804db40,xy,flip)
    pose=(ctypes.c_int32*80)();vm=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)()
    @FC
    def fetch(a,out,n,ctx):
     try:data=u.mem_read(a,n*4)
     except Exception:return 0
     for i,v in enumerate(struct.unpack('<'+'i'*n,data)):out[i]=v
     return 1
    @REG
    def registry(enabled,ctx):nreg.append(enabled)
    @RC
    def random(ctx):return 37
    @SINK
    def sink(kind,address,scale,ctx):
     if kind==25:actual.append([25,address]);auxiliary.value=address!=0
     elif kind==11:actual.append([11,address,scale]);audio.add(address)
     elif kind==22:
      p=(ctypes.c_int32*2)();assert fetch(address,p,2,None);actual.append([22,*p,r[5]])
     elif kind==23:
      p=(ctypes.c_int32*5)();xy=(ctypes.c_int32*2)();assert fetch(address,p,5,None);assert point(pose,fetch,None,xy)==0;actual.append([23,p[0],*xy,*p[1:]])
     elif kind==24:actual.append([24,address,*pose[:2]])
     elif kind==19:actual.append([19]);pose[40]|=1
     else:raise AssertionError(kind)
     return 0
    assert init((ctypes.c_int32*2)(*xy),flip,0x0831e0b8,0,fetch,None,pose)==0
    pose[79]=90;o.seed(pose);u.mem_write(o.actor+0x178,struct.pack('<2i',*pose[:2]));u.mem_write(o.actor+0x190,struct.pack('<4i',*pose[32:36]));u.mem_write(o.actor+0x2dc,struct.pack('<i',90));u.mem_write(o.actor+0x164,bytes(4))
    react(0,r);start(0x0804e22c,vm);o.call(0x08013344,o.vm,0x0804e22c)
    hpTrace=[]
    for tick in range(1,481):
     u.mem_write(0x02008178,struct.pack('<2i',*target))
     if hit and tick in [20,100,180,260,340,420]:
      event=(ctypes.c_int32*3)(3,1,1 if flip==0 else 2);u.mem_write(0x02007200,struct.pack('<3i',*event));o.call(0x08013a54,o.actor,0x02007200);assert activate(vm,r,event)==u.reg_read(UC_ARM_REG_R0)==1
     expected.clear();actual.clear();oreg.clear();nreg.clear()
     for a in [0x0200324c,0x020033e0]:u.mem_write(a,struct.pack('<i',tick))
     o.call(0x08018208,o.actor)
     result=step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),pose,vm,tick,3200*256,400*256,fetch,random,None,4096,r,registry,sink,target,ctypes.byref(auxiliary))
     assert result==0,(row['instance_id'],flip,hit,tick,result,list(pose[39:57]))
     diff={i:(pose[i],v) for i,v in o.snapshot().items() if pose[i]!=v};assert not diff,(row['instance_id'],flip,hit,tick,diff)
     assert list(pose[:2])==list(struct.unpack('<2i',u.mem_read(o.actor+0x178,8)))
     assert list(vm[:4])==list(struct.unpack('<4i',u.mem_read(o.vm+4,16)))
     assert actual==expected,(tick,actual,expected)
     assert nreg==oreg,(tick,nreg,oreg)
     if not hpTrace or hpTrace[-1][1]!=pose[52]:hpTrace.append([tick,pose[52],list(pose[2:14])])
     total+=1
     if pose[40]&1:break
    assert not hit or pose[40]&1,(mode,tick)
    scenarios.append({'actor_id':row['instance_id'],'flip':flip,'mode':mode,'ticks':tick,'hp_trace':hpTrace})
 report={'audio_descriptors':sorted(audio),'original_actor_frames':total,'scenarios':scenarios,'mismatches':0,'scope':'Real type57 ctor, generic update18208, original script804E22C with explicit target fixture, animation/motion, normal scene-Shrek event [3,1,side] and native marker point. Auxiliary child creation/replacement, target selection, registry/audio/global broadcast/removal and factory allocation are explicit owner fixtures. Requests71/90 compared; no actor creation, hero damage, full world, Android build or device execution.'}
 (ROOT/'docs/bandit_strong_script_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
