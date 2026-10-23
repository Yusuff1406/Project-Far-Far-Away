#!/usr/bin/env python3
"""Exercise real native movement/rendering on all 150 map/character pairs."""
import ctypes as C,json,random
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];P=C.c_void_p;I=C.c_int32;IP=C.POINTER(I)
lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
lib.s2_campaign_create.argtypes=[C.c_char_p];lib.s2_campaign_create.restype=P
for name,args in [('destroy',[P]),('select_scene',[P,I]),('mode',[P,I]),('can_walk',[P]),('character',[P,I]),('input',[P,I]),('option',[P,I,I]),('step',[P,I]),('info',[P,IP]),('save',[P,IP]),('restore',[P,IP]),('walk_info',[P,IP]),('walk_save',[P,IP]),('walk_restore',[P,IP]),('render',[P,I,P,C.c_size_t])]:getattr(lib,'s2_campaign_'+name).argtypes=args
root=ROOT/'android/app/src/main/assets/campaign';h=lib.s2_campaign_create(str(root).encode());assert h
rng=random.Random(64);frames=0;renders=0;states=set();cards=[];scenarios=[]
def walk():
 out=(I*10)();assert lib.s2_campaign_walk_info(h,out)==0;return list(out)
def snapshot():
 out=(I*100)();assert lib.s2_campaign_walk_save(h,out)==0;return list(out)
def browser():
 out=(I*12)();assert lib.s2_campaign_save(h,out)==0;return list(out)
def render():
 global renders
 pixels=(C.c_uint32*(426*160))();assert lib.s2_campaign_render(h,426,pixels,len(pixels))==0;renders+=1;return Image.frombytes('RGBA',(426,160),bytes(pixels),'raw','BGRA')
try:
 for scene in range(30):
  for kind in [3,6,4,5,7]:
   if scene in [6,7]:
    assert lib.s2_campaign_select_scene(h,scene)==0;assert lib.s2_campaign_mode(h,0)==0;state=browser();assert lib.s2_campaign_can_walk(h)==0 and lib.s2_campaign_mode(h,2)==-4;assert browser()==state;continue
   assert lib.s2_campaign_select_scene(h,scene)==0
   assert lib.s2_campaign_mode(h,0)==0 and lib.s2_campaign_mode(h,2)==0
   assert lib.s2_campaign_character(h,kind)==0
   seen=set();ground=0;kicks=0;before=walk()
   for tick in range(360):
    held=(16 if tick<240 else 32)|(1 if tick%80==0 else 0)|(2 if kind==6 and tick%80==12 else 0)
    assert lib.s2_campaign_input(h,held)==0
    assert lib.s2_campaign_step(h,1)==0,(scene,kind,tick,walk())
    w=walk();frames+=1;seen.add(w[3]);states.add(w[3]);ground+=w[6]>0;kicks+=w[3]==16
    assert w[0]==kind and 0<=w[4]<255
    if tick in [0,79,179,359]:render()
    if tick==179:
     saved=browser();body=snapshot();body[99]=0 # previous held clears on restoration
     assert lib.s2_campaign_input(h,0)==0
     body=snapshot();body[96]=0
     assert lib.s2_campaign_select_scene(h,(scene+1)%30)==0
     assert lib.s2_campaign_restore(h,(I*12)(*saved))==0
     assert lib.s2_campaign_walk_restore(h,(I*100)(*body))==0
     assert snapshot()==body,(scene,kind,'restore')
   lib.s2_campaign_input(h,0);paused=snapshot();lib.s2_campaign_option(h,0,1);lib.s2_campaign_step(h,4);assert snapshot()==paused;lib.s2_campaign_option(h,0,0)
   if scene in [0,1,4,8,13,17] and kind in [3,6,4,5,7]:cards.append((scene,kind,render()))
   scenarios.append(dict(scene=scene,type=kind,states=sorted(seen),ground_frames=ground,kick_frames=kicks,respawns=walk()[8],start=before[1:3],end=walk()[1:3]))
 assert 16 in states and all(s in states for s in range(6)),states
 # Reject malformed snapshots without changing state.
 baseline=snapshot()
 for at,value in [(0,0),(1,8),(2,99),(4,2147483647),(22,3),(26,999),(44,0),(51,0),(76,999),(84,99),(3,-1)]:
  broken=baseline.copy();broken[at]=value;assert lib.s2_campaign_walk_restore(h,(I*100)(*broken))==-1,(at,value);assert snapshot()==baseline
 # Five controlled protagonists can be switched at the same world position.
 for kind in [3,6,4,5,7,3]:
  old=snapshot();assert lib.s2_campaign_character(h,kind)==0;now=snapshot();assert old[5]+old[35]*128==now[5]+now[35]*128,'feet moved on character change';render()
finally:lib.s2_campaign_destroy(h)
sheet=Image.new('RGB',(426*5,184*6),(18,25,20));draw=ImageDraw.Draw(sheet)
for i,(scene,kind,im) in enumerate(cards):x=i%5*426;y=i//5*184;sheet.paste(im,(x,y));draw.text((x+8,y+165),f'Scene {scene:02} / Type {kind}',fill='white')
sheet.save(ROOT/'previews/campaign_traversal.png')
report=dict(map_character_pairs=len(scenarios),native_frames=frames,special_scenes_inspection_only=[6,7],rendered_frames=renders,states=sorted(states),mismatches=0,state_restore=True,invalid_restore_atomic=True,character_switch_preserves_feet=True,scenarios=scenarios,device_tested=False,scope='Static map collision, source protagonist locomotion, camera and sprite drawing. Does not validate AI, hazards, dynamic platforms, combat damage or chapter progression.')
(ROOT/'docs/campaign_traversal_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['scenarios','scope']})
