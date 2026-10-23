#!/usr/bin/env python3
"""Dynamic candidate bounds and disabled-physics refusal before mutation."""
import ctypes,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from replay_generic_actor import Resources,IP,FC
from replay_shrek_controls import SINK,DSP
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));res=Resources();init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP]
 frame=lib.s2_shrek_player_step_dynamic;frame.argtypes=[ctypes.c_char_p,IP,IP,IP,IP,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,IP,IP,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,DSP,ctypes.c_void_p,IP,ctypes.c_int]
 @SINK
 def sink(k,r,g,c):raise AssertionError('Unexpected effect')
 @DSP
 def dispatch(i,event,c):raise AssertionError('Unexpected event')
 cases=0
 for count,present,flags,expected in [(-1,True,6,-1),(17,True,6,-1),(1,False,6,-1),(1,True,2,-4),(1,True,4,-4),(1,True,0,-4)]:
  s=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();assert init((ctypes.c_int32*2)(123*256,349*256),0,0x0834f25c,0,res.fetch,None,s)==0;s[40]=flags;before=[list(x) for x in [s,e,status,book]]
  surfaces=(ctypes.c_int32*(17*9))() if present else None
  code=frame(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,e,status,book,0,1,1,(ctypes.c_int32*3)(1,0,0),(ctypes.c_int32*9)(1,7,0,0,12,0,0,11,0),0x0804b73c,0x0804b708,res.fetch,sink,dispatch,None,surfaces,count)
  assert code==expected and before==[list(x) for x in [s,e,status,book]];cases+=1
 result={'preflight_refusal_cases':cases,'mutated_refused_frames':0};(ROOT/'docs/player_dynamic_contract_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
