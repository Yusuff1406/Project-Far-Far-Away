#!/usr/bin/env python3
"""Physical chapter NPC entry -> native bonus -> score/rewards -> same parent."""
import ctypes as C,json,struct,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
lib.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];lib.s2_session_create_level.restype=P
for name,args in [('destroy',[P]),('step',[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP]),('snapshot',[P,IP]),('minigame_snapshot',[P,IP]),('minigame_actor_snapshot',[P,I,IP]),('minigame_state',[P]),('set_bonus_results',[P,I]),('set_transitions',[P,I]),('set_viewport',[P,I,I]),('transition_snapshot',[P,IP]),('requests',[P,IP,C.c_size_t]),('bonus_best',[P])]:getattr(lib,'s2_session_'+name).argtypes=args
rom=Path(sys.argv[1]).read_bytes();results=[]
for width in [240,384]:
 with tempfile.TemporaryDirectory()as td:
  folder=Path(td);shutil=__import__('shutil');shutil.copytree(ROOT/'extracted/scene_01/minigame_01',folder/'minigame_01')
  data=bytearray((ROOT/'objects/scene_01/scene.s2ob').read_bytes());struct.pack_into('<HH',data,18+44,6000,0);rows=json.loads((ROOT/'objects/scene_01/objects.json').read_text())['objects'];npc=next(x for x in rows if x['type']==94);struct.pack_into('<HH',data,18+(npc['instance_id']-1)*44,3371,329);(folder/'objects.s2ob').write_bytes(data)
  err=I();paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',folder/'scene.s2lv',ROOT/'collision/scene_01/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',folder/'objects.s2ob'];shutil.copyfile(ROOT/'extracted/scene_01/scene.s2lv',paths[1]);h=lib.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert h,err.value;lib.s2_session_set_bonus_results(h,1);lib.s2_session_set_transitions(h,1);lib.s2_session_set_viewport(h,width,160)
  pix=(C.c_uint32*(width*160))();info=(I*8)();main=(I*320)();mini=(I*320)();board=(I*216)();tr=(I*8)();start=failed=returned=None;score=0;frozen=None;frames=0
  try:
   for t in range(2400):
    mode=lib.s2_session_minigame_state(h);buttons=0
    if start is None:buttons=2 if t==40 else 1 if t>60 and t%12==4 else 0
    elif failed is not None:buttons=1 if t>failed+30 else 0
    elif mode==1:
     lib.s2_session_minigame_snapshot(h,mini);lib.s2_session_minigame_actor_snapshot(h,2,board)
     if mini[316]<650:
      dx=board[0]-mini[0];buttons=16 if dx>512 else 32 if dx<-512 else 0
     else:buttons=16
    assert lib.s2_session_step(h,buttons,pix,len(pix),info)==0,(width,t,list(info));frames+=1;mode=lib.s2_session_minigame_state(h);lib.s2_session_snapshot(h,main);lib.s2_session_transition_snapshot(h,tr)
    if mode:
     if width==384 and tr[0]==0:assert all(pix[y*width+x]==0xff181818 for y in range(160)for x in [0,(width-240)//2-1,width-1]),'bonus centered at source240px'
     lib.s2_session_minigame_snapshot(h,mini)
     if start is None:start=t;frozen=list(main)
     assert list(main)==frozen,(t,'parent advanced during bonus')
     score=mini[312]
     if mode==2 and failed is None:failed=t
    elif start is not None and returned is None:
     returned=t;assert score>=10 and failed is not None and returned-failed<=18
     assert list(main)==frozen and tr[5]==score and lib.s2_session_bonus_best(h)==score
     p=struct.unpack_from('<I',rom,0x4d820+4)[0]-0x08000000;expected=[]
     for i in range(64):
      lo,hi,kind=struct.unpack_from('<3i',rom,p+i*12)
      if not kind:break
      if score>=lo and (score<=hi or hi<=lo):expected.append(kind)
     assert tr[7]==len(expected),(score,list(tr),expected)
    if returned is not None and t>returned+180:break
   assert start is not None and failed is not None and returned is not None
   requests=(I*(4096*8))();n=lib.s2_session_requests(h,requests,4096);assert n>=0
   awards=[list(requests[i*8:i*8+8])for i in range(n)if requests[i*8+1]==30];assert len(awards)==1 and awards[0][4:4+len(expected)]==expected,(awards,expected)
   results.append(dict(width=width,frames=frames,score=score,bonus_started=start,failed=failed,returned=returned,reward_types=expected,parent_frozen=True,source_reward_table=1))
  finally:lib.s2_session_destroy(h)
report=dict(runs=results,mismatches=0,device_tested=False,scope='Chapter01 NPC relocated beside original hero; intro trigger moved outside to isolate entry. Real B talk, dialogue, mosaic, scene07, tracking, physical fall, immediate return without death animation or result confirmation, original table1 awards and resumed NPC script. Same native parent, no Activity restart.')
(ROOT/'docs/donkey_bonus_flow_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
