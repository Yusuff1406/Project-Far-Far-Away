#!/usr/bin/env python3
"""All ogre frame audio markers and deadline boundaries against original FA4C."""
import ctypes,json,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p)
def main():
 o=Original(Rom(sys.argv[1]));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];audio=lib.s2_shrek_stomp_audio;audio.argtypes=[IP,IP,ctypes.c_int32,FC,SINK,ctypes.c_void_p];requests=[]
 @FC
 def fetch(a,out,n,ctx):
  try:raw=u.mem_read(a,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 @SINK
 def sink(kind,address,scale,ctx):requests.append([kind,address,scale]);return 0
 cases=cues=0
 for animation in json.loads((ROOT/'sprites/shrek_ogre/bank.json').read_text())['animations']:
  address=0x08000000+animation['record_offset'];o.ctor(address)
  for frame in range(animation['sequence_count']):
   for delta in range(-3,5):
    for tick in (-2147483648,-1,0,2147483647):
     s=(ctypes.c_int32*80)();book=(ctypes.c_int32*8)();assert init((ctypes.c_int32*2)(0,0),0,address,tick,fetch,None,s)==0;s[22]=frame;s[23]=ctypes.c_int32(tick+delta).value;book[1]=0x08053cb4;o.seed(s);u.mem_write(0x0200324c,struct.pack('<i',tick));o.call(0x0800fa4c,o.actor)
     from unicorn.arm_const import UC_ARM_REG_R0
     cue=bool(u.reg_read(UC_ARM_REG_R0));requests.clear();assert audio(s,book,tick,fetch,sink,None)==0;assert requests==([[11,book[1],256]]if cue else []),(animation['index'],frame,delta,tick,requests,cue);cases+=1;cues+=cue
 report={'original_cases':cases,'positive_markers':cues,'mismatches':0,'scope':'All exported ogre animation frames, original FA4C predicate and native descriptor requests, including signed tick wrap. SoundPool playback/device listening excluded.'};(ROOT/'docs/player_audio_cue_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
