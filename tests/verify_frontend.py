#!/usr/bin/env python3
"""Exercise the shipped C++ frontend, source art and all campaign routes."""
import ctypes,json,hashlib,tempfile,struct,io
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_frontend_create;create.argtypes=[ctypes.c_char_p]*2;create.restype=ctypes.c_void_p
for name,args in [('sound',[ctypes.c_void_p]),('presentation',[ctypes.c_void_p,IP]),('text_boxes',[ctypes.c_void_p,IP,I]),('destroy',[ctypes.c_void_p]),('open',[ctypes.c_void_p,I,I]),('progress',[ctypes.c_void_p,IP]),('restore',[ctypes.c_void_p,IP]),('step',[ctypes.c_void_p,I]),('touch',[ctypes.c_void_p,I,I]),('action',[ctypes.c_void_p]),('snapshot',[ctypes.c_void_p,IP]),('render',[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t])]:getattr(l,'s2_frontend_'+name).argtypes=args
pack=ROOT/'android/app/src/main/assets/frontend/menu.s2ui';sp=ROOT/'sprites/bank_328294/bank.s2sp';h=create(str(pack).encode(),str(sp).encode());assert h;state=(I*9)();pix=(ctypes.c_uint32*38400)();shots=[];checks=0

nativeStep=l.s2_frontend_step;framesExercised=0
def countedStep(h,b):
 global framesExercised
 framesExercised+=1;return nativeStep(h,b)
l.s2_frontend_step=countedStep

def snap():assert l.s2_frontend_snapshot(h,state)==0;return list(state)
def presentation():
 row=(I*8)();assert l.s2_frontend_presentation(h,row)==0;return list(row)
def drain():
 for _ in range(33):l.s2_frontend_step(h,0)
def press(mask):
 assert l.s2_frontend_step(h,mask)==0;assert l.s2_frontend_step(h,0)==0;drain()

def shot(name):
 global checks
 assert l.s2_frontend_render(h,pix,len(pix))==0;im=Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA');background=Image.new('RGBA',im.size,(30,42,26,255));background.alpha_composite(im);im=background.convert('RGB');im.resize((720,480),Image.Resampling.NEAREST).save(ROOT/f'previews/frontend_{name}.png');shots.append((name,im));checks+=1
try:
 # Boot runs through each source logo automatically; skips commit only at black.
 seen=set()
 for _ in range(1400):
  page,cursor=snap()[:2]
  if page!=11:break
  seen.add(cursor);l.s2_frontend_step(h,0)
 assert seen=={0,1,2,3} and snap()[0]==1
 assert l.s2_frontend_action(h)==9 and l.s2_frontend_action(h)==0
 # Every original title frame remains byte-identical above the press-start footer.
 source=pack.read_bytes();_,w,hgt,nframes,ms=struct.unpack_from('<5I',source,28)
 title=[]
 for f in range(nframes):
  at=48+f*39424;palette=source[at:at+1024];title.append(b''.join(palette[v*4:v*4+4]for v in source[at+1024:at+39424]))
 l.s2_frontend_open(h,0,0)
 for tick in range(401):
  assert l.s2_frontend_render(h,pix,len(pix))==0;frame=min(nframes-1,max(0,tick-60)//((ms*60+999)//1000));assert bytes(pix)[:240*130*4]==title[frame][:240*130*4]
  if tick<400:l.s2_frontend_step(h,0)
 l.s2_frontend_open(h,0,0)
 assert snap()[0]==1;shot('main');press(1);assert snap()[0]==2;shot('slots');press(128);press(1);assert snap()[0:4]==[12,0,0,1];assert l.s2_frontend_action(h)==7 and l.s2_frontend_action(h)==0;shot('story');press(8);assert snap()[0]==3;shot('books');press(1);assert snap()[0:4]==[4,0,0,1];shot('chapters');press(1);assert l.s2_frontend_action(h)==1
 # One held A never double launches; release required, same as touch ownership.
 l.s2_frontend_step(h,1);assert l.s2_frontend_action(h)==0
 for _ in range(60):l.s2_frontend_step(h,1);assert l.s2_frontend_action(h)==0
 l.s2_frontend_step(h,0)
 l.s2_frontend_progress(h,(I*7)(7,0x1ffffff,0x1ffffff,0x1ffffff,40,12,31))
 catalog=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records'];routes=[]
 for book in range(6):
  l.s2_frontend_open(h,3,book);press(1);assert snap()[2]==book
  for chapter in range(5):
   l.s2_frontend_open(h,4,chapter);s=snap();expected=catalog[book*5+chapter]['scene'];assert s[5]==expected;press(1);a=l.s2_frontend_action(h)
   assert a==(1 if expected==0 else 11 if expected in [1,14,21,23] else 10) and snap()[0]==4;routes.append(dict(book=book,chapter=chapter,scene=expected,launched=bool(a)))
 l.s2_frontend_open(h,3,0);assert l.s2_frontend_touch(h,62,80)==0;drain();assert snap()[2]==1 and snap()[0]==4;shot('book2');l.s2_frontend_open(h,5,0);shot('pause');press(8);assert l.s2_frontend_action(h)==2
 # Original pause contains only Quit Game and Sleep. Start/B resume instantly.
 for choice in [0,1]:
  l.s2_frontend_open(h,5,choice);press(1);assert snap()[0]==6
  press(2);assert snap()[0]==5
  l.s2_frontend_open(h,5,choice);press(1);press(1)
  if choice==1:assert snap()[0]==10;press(1);assert snap()[0]==5
  else:assert l.s2_frontend_action(h)==4
 l.s2_frontend_open(h,5,0);press(64);assert snap()[1]==1;press(2);assert l.s2_frontend_action(h)==2
 # Three separate slots; erase only selected slot, cancel leaves records intact.
 l.s2_frontend_progress(h,(I*7)(7,1,0,1,40,12,31));l.s2_frontend_open(h,9,2);press(1);press(2);assert snap()[6:9]==[7,1,31];l.s2_frontend_open(h,9,2);press(1);press(1);assert l.s2_frontend_action(h)==6 and snap()[6:9]==[3,0,0];shot('erased_slot');l.s2_frontend_open(h,8,0)
 for _ in range(960):l.s2_frontend_step(h,0)
 shot('credits');press(2);assert snap()[0]==1
 # Process recreation restores book/slot/cursor, never a pending destructive confirmation.
 l.s2_frontend_open(h,3,4);press(1);l.s2_frontend_open(h,4,3);saved=(I*9)(*snap());l.s2_frontend_open(h,0,0);assert l.s2_frontend_restore(h,saved)==0 and snap()[:4]==list(saved)[:4];saved[0]=6;assert l.s2_frontend_restore(h,saved)==0 and snap()[0]==5
 # Coordinates outside the original centered menu cannot activate a choice.
 l.s2_frontend_open(h,4,0);assert l.s2_frontend_touch(h,-1,30)==-1 and l.s2_frontend_action(h)==0
 # Transitions are visible before the page commit; input cannot cross the fade.
 l.s2_frontend_open(h,0,0);l.s2_frontend_step(h,1);assert snap()[0]==1 and presentation()[0]==1
 for _ in range(15):l.s2_frontend_step(h,1)
 l.s2_frontend_render(h,pix,len(pix));assert len(set(pix))>1
 l.s2_frontend_step(h,1);l.s2_frontend_render(h,pix,len(pix));assert set(pix)=={0xff000000} and snap()[0]==2
 for _ in range(40):l.s2_frontend_step(h,1)
 assert snap()[0]==2;l.s2_frontend_step(h,0)
 l.s2_frontend_open(h,3,0);l.s2_frontend_step(h,1);assert presentation()[0]==2;drain();assert snap()[0]==4
 # Caption reveal, pagination and all four scenes have a complete route back to books.
 l.s2_frontend_open(h,12,0);introSeen=set()
 for _ in range(30):
  if snap()[0]!=12:break
  introSeen.add(snap()[1]);press(1)
 assert introSeen=={0,1,2,3} and snap()[0]==3
 # Record actual glyph ink rectangles, including the original font's overhang.
 boxesChecked=0
 for page in range(13):
  for cursor in range(6 if page==3 else 5 if page in[4,5]else 4 if page in[2,11,12]else 1):
   l.s2_frontend_open(h,page,cursor)
   for _ in range(12):l.s2_frontend_step(h,0)
   l.s2_frontend_render(h,pix,len(pix));boxes=(I*(8*100))();count=l.s2_frontend_text_boxes(h,boxes,100)
   for i in range(count):
    left,top,right,bottom,cl,ct,cr,cb=boxes[i*8:i*8+8];assert cl<=left<right<=cr and (max(ct,top)<min(bottom,cb) if page==8 else ct<=top<bottom<=cb),(page,cursor,list(boxes[i*8:i*8+8]));boxesChecked+=1
 for cursor in range(4):
  l.s2_frontend_open(h,12,cursor)
  for _ in range(200):l.s2_frontend_step(h,0)
  shot('intro_'+str(cursor))
 # Fresh progress shows only the first book; chapter completion opens the next.
 l.s2_frontend_progress(h,(I*7)(1,0,0,0,0,0,0));l.s2_frontend_open(h,3,0);press(16);assert snap()[1]==0;shot('books_locked')
 l.s2_frontend_progress(h,(I*7)(1,31,31,31,40,0,0));press(16);assert snap()[1]==1
 # Focused rows change palette without moving their glyphs. Cancel is a one-shot source sound.
 for page in[2,4]:
  l.s2_frontend_open(h,page,0);l.s2_frontend_render(h,pix,len(pix));first=bytes(pix)
  for _ in range(16):l.s2_frontend_step(h,0)
  l.s2_frontend_render(h,pix,len(pix));assert bytes(pix)!=first
 l.s2_frontend_open(h,2,0);l.s2_frontend_step(h,2);assert l.s2_frontend_sound(h)==8 and l.s2_frontend_sound(h)==0;drain()
 # Animated previews are rendered by the shipped frontend, without Android.
 animations=[]
 for page,cursor,button in[(11,1,0),(3,0,16),(0,0,1),(3,0,1),(12,1,0)]:
  l.s2_frontend_open(h,page,cursor)
  if button:l.s2_frontend_step(h,button)
  frames=[]
  for i in range(80):
   l.s2_frontend_render(h,pix,len(pix));frames.append(Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').convert('RGB'));l.s2_frontend_step(h,0)
  name=f'frontend_stage60_{page}_{button}.gif';frames[0].save(ROOT/'previews'/name,save_all=True,append_images=frames[1:],duration=34,loop=0,optimize=False,disposal=2);animations.append(name)
 # Loader rejects truncation instead of using an incomplete asset after upgrade.
 with tempfile.TemporaryDirectory()as td:
  p=Path(td)/'bad.s2ui'
  for data in [b'',pack.read_bytes()[:100],pack.read_bytes()[:-1]]:
   p.write_bytes(data);assert not create(str(p).encode(),str(sp).encode())
finally:l.s2_frontend_destroy(h)
sheet=Image.new('RGB',(720,((len(shots)+2)//3)*180),(25,25,25));d=ImageDraw.Draw(sheet)
for i,(name,im)in enumerate(shots):x=i%3*240;y=i//3*180;sheet.paste(im,(x,y));d.text((x+4,y+162),name,fill='white')
sheet.save(ROOT/'previews/frontend_contact.png');report=dict(campaign_routes=routes,playable_routes=sum(x['scene'] in [0,1,14,21,23] for x in routes),native_frames_exercised=framesExercised,boot_logos=4,story_panels=4,text_boxes_checked=boxesChecked,animations=animations,previews=len(shots),held_input_checked=True,three_slot_isolation=True,malformed_assets_rejected=True,mismatches=0,device_tested=False);(ROOT/'docs/frontend_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
