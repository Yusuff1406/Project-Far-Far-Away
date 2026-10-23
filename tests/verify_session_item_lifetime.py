#!/usr/bin/env python3
"""Held action releases item; removed actor stops updating; reset reinstates it."""
import ctypes,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32)
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p;destroy=lib.s2_session_destroy;destroy.argtypes=[ctypes.c_void_p];destroy.restype=None;step=lib.s2_session_step;step.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP];snapshot=lib.s2_session_snapshot;snapshot.argtypes=[ctypes.c_void_p,IP];effectFn=lib.s2_session_effect_state;effectFn.argtypes=[ctypes.c_void_p,IP];effectState=(ctypes.c_int32*9)();reset=lib.s2_session_reset;reset.argtypes=[ctypes.c_void_p];requests=lib.s2_session_requests;requests.argtypes=[ctypes.c_void_p,IP,ctypes.c_size_t]
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];error=ctypes.c_int32();h=create(*paths,ctypes.byref(error));assert h and not error.value;s=(ctypes.c_int32*320)();snapshot(h,s);initial=list(s);pixels=(ctypes.c_uint32*38400)();info=(ctypes.c_int32*8)();release=[];removedTick=0;previousId=0;frozen=None;frozenTicks=0
 try:
  for tick in range(1,401):
   held=4 if tick==80 else 16 if 125<=tick<130 else 2 if 130<=tick<=190 else 0
   assert step(h,held,pixels,len(pixels),info)==0;assert snapshot(h,s)==0
   assert effectFn(h,effectState)==0
   if tick==225:assert list(effectState)==[896,3,128,1,1,0,1,3,64]
   if tick==253:assert effectState[0]==0 and effectState[3]==29
   if tick>=289:assert effectState[7]==0 and effectState[8]==0
   if previousId and not info[3]:release.append(tick)
   previousId=info[3]
   if s[144]&1:
    if not removedTick:removedTick=tick;frozen=list(s[104:]);assert not s[83]
    else:assert frozen==list(s[104:]);frozenTicks+=1
  assert release==[160] and removedTick==252 and frozenTicks==148,(release,removedTick,frozenTicks)
  rows=(ctypes.c_int32*(256*8))();n=requests(h,rows,256);assert n==5;queue=[list(rows[i*8:i*8+8]) for i in range(n)];assert [x[1] for x in queue]==[1,11,16,17,19]
  before=list(rows);assert requests(h,rows,n-1)==-1 and list(rows)==before
  assert reset(h)==0;assert snapshot(h,s)==0 and list(s)==initial;assert requests(h,None,0)==0;assert effectFn(h,effectState)==0 and not any(effectState)
 finally:destroy(h)
 result={'ticks':400,'owner_release_ticks':release,'item_removed_tick':removedTick,'inactive_item_ticks_verified':frozenTicks,'request_kinds':[x[1] for x in queue],'reset_restored_all320_words':True,'reset_cleared_requests':True,'effect_phases_verified':[225,253,289],'reset_cleared_effect_state':True,'undersized_output_refusals':1,'scope':'Owned native session lifecycle; selected type77 action, inactive retained slot and reset. Global packets remain queued; no full heap destructor/world registry or Android execution.'};(ROOT/'docs/session_item_lifetime_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
