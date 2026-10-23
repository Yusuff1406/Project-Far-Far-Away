#!/usr/bin/env python3
"""Recorded reference coordinates/speeds, intro input, quit confirmation and audio."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'));pix=(C.c_uint32*38400)();state=(I*9)();info=(I*8)()
for prefix,items in [('frontend',[('create',[C.c_char_p]*2),('destroy',[P]),('open',[P,I,I]),('step',[P,I]),('snapshot',[P,IP]),('action',[P]),('render',[P,P,C.c_size_t]),('progress',[P,IP])]),('session',[('create_level',[C.c_char_p]*5+[IP]),('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('dialogue_snapshot',[P,IP]),('snapshot',[P,IP]),('requests',[P,IP,C.c_size_t]),('player_type',[P])])]:
 for name,args in items:getattr(l,'s2_'+prefix+'_'+name).argtypes=args
l.s2_frontend_create.restype=P;l.s2_session_create_level.restype=P
pack=(R/'android/app/src/main/assets/frontend/menu.s2ui').read_bytes();at=28
for _ in range(19):n=struct.unpack_from('<I',pack,at+12)[0];at+=20+n*39424
w,h,g,n=struct.unpack_from('<4I',pack,at);at+=16;index=pack[at:at+256];advance=pack[at+256:at+512];colors=struct.unpack_from('<48I',pack,at+512);tiles=pack[at+704:at+704+n]
def assert_text(txt,x,y,palette=0):
 count=0
 for ch in txt:
  if ch!=32:
   for yy in range(16):
    for xx in range(16):
     a=index[ch]*128+(yy//8*2+xx//8)*32+(yy%8)*4+xx%8//2;c=(tiles[a]>>((xx&1)*4))&15
     if c:assert pix[(y+yy)*240+x+xx]==colors[palette*16+c],(txt,x+xx,y+yy);count+=1
  x+=advance[ch]
 return count
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h
report={'device_tested':False}
def frames(n,b=0):
 for _ in range(n):assert l.s2_frontend_step(h,b)==0

def press(b):frames(1,b);frames(40)
def snap():l.s2_frontend_snapshot(h,state);return list(state)
def shot(name):
 assert l.s2_frontend_render(h,pix,len(pix))==0
 Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/f'previews/stage73_{name}.png')
try:
 l.s2_frontend_progress(h,(I*7)(1,0,0,0,24,0,0));l.s2_frontend_open(h,4,0);shot('chapter_menu');counter=assert_text(b'24/40',20,120);back=assert_text(b'\x81 back',140,120)
 for cursor in range(4):
  l.s2_frontend_open(h,11,cursor);press(1);s=snap();assert (s[0],s[1])==((11,cursor+1)if cursor<3 else(1,0)),s
  l.s2_frontend_open(h,11,cursor);press(8);assert snap()[0]==1
 l.s2_frontend_open(h,11,0);frames(80,1);assert snap()[:2]==[11,1],'held A skipped more than one slide'
 l.s2_frontend_open(h,11,0);press(2);assert snap()[:2]==[11,0]
 l.s2_frontend_open(h,5,1);press(1);assert snap()[:2]==[6,0] and l.s2_frontend_action(h)==0;shot('quit_level_confirm');header=assert_text(b'Quit Level?',78,30)
 press(1);assert snap()[:2]==[5,1] and l.s2_frontend_action(h)==0
 press(1);press(2);assert snap()[:2]==[5,1]
 press(1);press(128);frames(1,1);assert l.s2_frontend_action(h)==0;frames(16);assert l.s2_frontend_action(h)==3
 speeds=[]
 for button,seconds,pixels,expected_y in [(0,2,60,124),(1,1,60,124)]:
  l.s2_frontend_open(h,8,0);frames(seconds*60,button);shot('credits_fast'if button else 'credits_normal');n=assert_text(b'Vicarious Visions',55,expected_y);speeds.append({'button':button,'seconds':seconds,'pixels':pixels,'ink_pixels':n})
 report['frontend']={'chapter_counter_anchor':[20,120],'chapter_back_anchor':[140,120],'counter_ink_pixels':counter,'back_ink_pixels':back,'boot_A_one_slide_Start_main':True,'held_A_single_skip':True,'quit_confirm_Cancel_default':True,'quit_header_pixels':header,'credits_normal_px_s':30,'credits_fast_px_s':60,'credits_alignment_x':55,'scroll_cases':speeds}
finally:l.s2_frontend_destroy(h)
reactions=[]
for scene in [0,1,2,13,14,21]:
 for pattern in ['finish_A','skip_Start']:
  paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',R/f'objects/scene_{scene:02}/scene.s2ob'];err=I();session=l.s2_session_create_level(*[str(p).encode()for p in paths],C.byref(err));assert session,(scene,err.value);dlg=(I*80)();closed=False;active=False;typ=l.s2_session_player_type(session)
  try:
   for t in range(400):
    l.s2_session_dialogue_snapshot(session,dlg);was=bool(dlg[64]);active|=was;b=(64 if pattern=='skip_Start'else 1)if was and t%4==2 else 0
    e=l.s2_session_step(session,b,pix,len(pix),info);assert e==0,(scene,pattern,t,e,list(info));l.s2_session_dialogue_snapshot(session,dlg)
    if was and not dlg[64]:closed=True;tag=dlg[78];break
   assert active and closed,(scene,pattern)
   for _ in range(12):assert l.s2_session_step(session,0,pix,len(pix),info)==0
   rows=(I*(1024*8))();n=l.s2_session_requests(session,rows,1024);expected=0x08053d5c if typ==6 else 0x08053cf0;actual=[rows[j*8+2]for j in range(n)if rows[j*8+1]==11 and rows[j*8+2]in[0x08053cf0,0x08053d5c]];assert actual==[expected],(scene,pattern,actual)
   reactions.append({'scene':scene,'tag':tag,'pattern':pattern,'hero':typ,'sound':83 if typ==6 else 86,'emissions':len(actual)})
  finally:l.s2_session_destroy(session)
report['intro_reactions']=reactions
(R/'docs/stage73_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
