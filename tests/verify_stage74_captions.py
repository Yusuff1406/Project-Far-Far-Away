#!/usr/bin/env python3
"""Whole native caption frames compared with original page layout/render helpers."""
import ctypes as C,json,struct,sys
from pathlib import Path
from PIL import Image
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from extract_session_sfx import GaxOracle
rom=Path(sys.argv[1]).read_bytes();o=GaxOracle(rom);u=o.u;draws=[]
def hook(uc,a,n,c):
 if a==0x800bf04:uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 if a==0x8003678:
  font,begin,end,pos=[uc.reg_read(x)for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
  draws.append((bytes(uc.mem_read(begin,end-begin)),*struct.unpack('<2i',uc.mem_read(pos,8))))
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook);o.call(0x8019260);o.call(0x800ba9c);o.call(0x8017218,0x2030000,0x20030f0)
l=C.CDLL(str(R/'native/build/libshrek_scene.so'));I=C.c_int32;P=C.c_void_p
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,a in [('open',[P,I,I]),('step',[P,I]),('render',[P,P,C.c_size_t]),('destroy',[P]),('snapshot',[P,C.POINTER(I)]),('sound',[P])]:getattr(l,'s2_frontend_'+n).argtypes=a
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h
pix=(C.c_uint32*38400)();pack=(R/'android/app/src/main/assets/frontend/menu.s2ui').read_bytes();at=28;images={}
for _ in range(19):
 id,w,height,n,period=struct.unpack_from('<5I',pack,at);at+=20;pal=struct.unpack_from('<256I',pack,at);images[id]=[pal[x]for x in pack[at+1024:at+39424]];at+=n*39424
font=0x30fbac;index=rom[font+8:font+264];adv=rom[font+264:font+520];pal=[]
for v in struct.unpack_from('<16H',rom,0x30f9ac):pal.append(0xff000000|((v&31)*255//31<<16)|(((v>>5)&31)*255//31<<8)|((v>>10)&31)*255//31)
def ink(expected,txt,x,y):
 for ch in txt:
  if ch!=32:
   for yy in range(16):
    for xx in range(16):
     b=rom[font+520+index[ch]*128+(yy//8*2+xx//8)*32+(yy%8)*4+xx%8//2];v=(b>>((xx&1)*4))&15
     if v and 0<=x+xx<240 and 0<=y+yy<160:expected[(y+yy)*240+x+xx]=pal[v]
  x+=adv[ch]
results=[]
try:
 # Initials directions use the same source menu sound, once per edge.
 l.s2_frontend_open(h,13,0)
 for b in [16,32,64,128]:
  l.s2_frontend_step(h,b);assert l.s2_frontend_sound(h)==63
  l.s2_frontend_step(h,b);assert l.s2_frontend_sound(h)==0
  l.s2_frontend_step(h,0);assert l.s2_frontend_sound(h)==0
 for slide in range(4):
  ptr=0x80453c8+4*slide
  for _ in range(2):ptr=struct.unpack('<I',u.mem_read(ptr,4))[0]
  o.call(0x80171c0,0x2030000,ptr);l.s2_frontend_open(h,12,slide);page=0
  while True:
   draws.clear();o.call(0x8017154,0x2030000);expected=images[13+slide].copy()
   for txt,x,y in draws:ink(expected,txt,x,y)
   # Caption glyphs remain stable over time; no growing/recentering prefixes.
   for ticks in [0,1,29]:
    for _ in range(ticks):l.s2_frontend_step(h,0)
    assert l.s2_frontend_render(h,pix,len(pix))==0
    mismatches=sum(a!=b for a,b in zip(pix,expected));assert mismatches==0,(slide,page,ticks,mismatches,draws)
   results.append(dict(slide=slide,page=page,rows=[dict(text=t.decode(),x=x,y=y)for t,x,y in draws],compared_frames=3))
   if slide==0 and page==0:Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/'previews/stage74_caption.png')
   nextptr=struct.unpack('<I',u.mem_read(0x2030008,4))[0]
   if u.mem_read(nextptr,1)==b'\0':break
   o.call(0x8017198,0x2030000);l.s2_frontend_step(h,1);l.s2_frontend_step(h,0);page+=1;assert page<10
  # One A advances the finished slide; holding A cannot skip another.
  l.s2_frontend_step(h,1)
  for _ in range(40):l.s2_frontend_step(h,1)
  state=(I*9)();l.s2_frontend_snapshot(h,state);assert list(state)[:2]==([12,slide+1]if slide<3 else[3,0]),list(state)
 l.s2_frontend_open(h,12,0);l.s2_frontend_step(h,8)
 for _ in range(40):l.s2_frontend_step(h,0)
 l.s2_frontend_snapshot(h,state);assert state[0]==3
finally:l.s2_frontend_destroy(h)
report=dict(pages=results,initials_direction_sound=63,mismatches=0,device_tested=False,scope='Original 19260 fonts, BA9C rectangle, 17218 caption constructor, 17198/11CB0 pagination and 17154/11DA8 render layout execute under Unicorn. Subscription registration and glyph hardware delivery are intercepted. Independent ROM glyph ink over decoded original backgrounds compared to every native output pixel; full game hardware timing not modeled.')
(R/'docs/stage74_captions_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
