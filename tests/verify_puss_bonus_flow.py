#!/usr/bin/env python3
"""Physical Puss NPC -> scene06 -> loss/results -> original rewards -> parent."""
import ctypes as C,json,struct,sys,tempfile,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('destroy',[P]),('step',[P,I,C.c_void_p,C.c_size_t,IP]),('snapshot',[P,IP]),('minigame_snapshot',[P,IP]),('minigame_state',[P]),('transition_snapshot',[P,IP]),('set_viewport',[P,I,I]),('set_bonus_results',[P,I]),('set_transitions',[P,I]),('requests',[P,IP,C.c_size_t]),('bonus_best',[P])]:getattr(l,'s2_session_'+n).argtypes=a
rom=Path(sys.argv[1]).read_bytes();runs=[]
for width,isolated in [(240,False),(384,True)]:
 with tempfile.TemporaryDirectory()as td:
  folder=Path(td);shutil.copyfile(ROOT/'extracted/scene_23/scene.s2lv',folder/'scene.s2lv');shutil.copytree(ROOT/'extracted/scene_23/minigame_02',folder/'minigame_02')
  data=bytearray((ROOT/'objects/scene_23/scene.s2ob').read_bytes());rows=json.loads((ROOT/'objects/scene_23/objects.json').read_text())['objects']
  for r in rows:
   if r['type']==94:x,y=873,1721
   elif r['type']==151 or 53<=r['type']<=62 or 91<=r['type']<=111:x,y=12000,0
   else:continue
   struct.pack_into('<HH',data,18+(r['instance_id']-1)*44,x,y)
  (folder/'objects.s2ob').write_bytes(data)
  if isolated:
   p=folder/'minigame_02/scene.s2ob';d=bytearray(p.read_bytes());struct.pack_into('<HH',d,18+44,12000,0);p.write_bytes(d)
  err=I();h=l.s2_session_create_level(*[str(p).encode()for p in [ROOT/'android/app/src/main/assets/session/resources.s2pk',folder/'scene.s2lv',ROOT/'collision/scene_23/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',folder/'objects.s2ob']],C.byref(err));assert h,err.value
  l.s2_session_set_viewport(h,width,160);l.s2_session_set_transitions(h,1);l.s2_session_set_bonus_results(h,1);pix=(C.c_uint32*(width*160))();info=(I*8)();main=(I*320)();mini=(I*320)();tr=(I*8)();start=failed=returned=None;frozen=None;direction=16;previous=0;score=0;playerStates=set();maxscore=0;lossRequested=False;screenshotSaved=False
  try:
   for t in range(3800):
    mode=l.s2_session_minigame_state(h);buttons=0
    if start is None:buttons=2 if t==40 else 64 if t>60 and t%2==0 else 0
    elif failed is not None:buttons=1 if t>failed+30 else 0
    elif mode==1:
     l.s2_session_minigame_snapshot(h,mini);x=mini[0]/256;st=mini[80]
     if x>195:direction=32
     elif x<45:direction=16
     buttons=direction|(1 if(st==16 or st==18)and not(previous&1)else 0) if isolated else 16|(1 if mini[316]%25==0 else 0)
     if (isolated and mini[312]>=16)or(not isolated and mini[316]>500):lossRequested=True;buttons=1 if st==16 and not(previous&1)else 0
    assert l.s2_session_step(h,buttons,pix,len(pix),info)==0,(width,t,list(info));previous=buttons;mode=l.s2_session_minigame_state(h);l.s2_session_snapshot(h,main);l.s2_session_transition_snapshot(h,tr)
    if mode:
     assert mode in [1,2],('wrong child',mode);l.s2_session_minigame_snapshot(h,mini)
     if start is None:start=t;frozen=list(main)
     assert list(main)==frozen,'parent advanced';score=mini[312];maxscore=max(maxscore,score);playerStates.add(mini[80])
     if isolated and score==16 and mode==1 and not screenshotSaved:Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').resize((width*3,480),Image.Resampling.NEAREST).save(ROOT/'previews/puss_bonus69.png');screenshotSaved=True
     if width==384 and tr[0]==0:assert all(pix[y*width+x]==0xff181818 for y in range(160)for x in [0,71,383])
     if mode==2 and failed is None:failed=t
    elif start is not None:
     returned=t;assert failed is not None and returned>failed+30;assert list(main)==frozen;assert tr[5]==score and l.s2_session_bonus_best(h)==score
     break
   assert start is not None and failed is not None and returned is not None,(width,start,failed,returned,score,list(mini[:14]),mini[80])
   assert score>=(16 if isolated else 1),(width,score)
   p=struct.unpack_from('<I',rom,0x4d820+2*4)[0]-0x08000000;expected=[]
   for i in range(64):
    lo,hi,kind=struct.unpack_from('<3i',rom,p+i*12)
    if not kind:break
    if score>=lo and (score<=hi or hi<=lo):expected.append(kind)
   assert tr[7]==len(expected),(score,list(tr),expected)
   for _ in range(180):assert l.s2_session_step(h,0,pix,len(pix),info)==0
   q=(I*(4096*8))();n=l.s2_session_requests(h,q,4096);assert n>=0;awards=[list(q[i*8:i*8+8])for i in range(n)if q[i*8+1]==30];assert len(awards)==1 and awards[0][4:4+len(expected)]==expected,(awards,expected)
   runs.append(dict(width=width,isolated_hazard=isolated,score=score,entry=start,loss=failed,returned=returned,reward_types=expected,states=sorted(playerStates),parent_frozen=True))
  finally:l.s2_session_destroy(h)
report=dict(runs=runs,mismatches=0,device_tested=False,scope='Physical B/dialogue64 entry using relocated NPC and suppressed intro/nearby hostiles. First run retains original bonus hazard; second moves only hazard147 outside to isolate16 crossings and table2 reward. Player uses actual buttons without position/state injection. Not full chapter route.')
(ROOT/'docs/puss_bonus_flow_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
