#!/usr/bin/env python3
"""Viewport activation, prop/enemy layering and square mosaic, on the native host."""
import ctypes,json,struct,tempfile,sys
from pathlib import Path
from PIL import Image,ImageChops
from session_fixtures import without_intro
from verify_generic_runtime import Rom
from extract_sprites import bank,frame_image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
 for n,a in [('destroy',[ctypes.c_void_p]),('reset',[ctypes.c_void_p]),('snapshot',[ctypes.c_void_p,IP]),('actor_snapshot',[ctypes.c_void_p,I,IP]),('set_viewport',[ctypes.c_void_p,I,I]),('step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,'s2_session_'+n).argtypes=a
 l.s2_actor_anchor_q8.argtypes=[IP,IP,I,I,IP];l.s2_mosaic_argb.argtypes=[I,ctypes.POINTER(ctypes.c_uint32),I,I]
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());info=(I*8)();hero=(I*320)();a=(I*216)();err=I();r=Rom(sys.argv[1]);atlases={};runs=[];overlaps={};mosaicCases=0
 def sprite(pose,w):
  # Source bank headers, independently decoded from the user's ROM.
  for root in [0x31dda4,0x34ab54,0x34f248]:
   if root not in atlases:atlases[root]=bank(r,root)
   atlas=atlases[root];anim=next((x for x in atlas['animations']if x['record_offset']==pose[47]-0x8000000),None)
   if anim:break
  assert anim,hex(pose[47]);anchor=(I*2)();l.s2_actor_anchor_q8(ctypes.cast(ctypes.byref(pose,72*4),IP),pose,pose[18],pose[38],anchor)
  # Fixture actors face right; source pieces retain their internal flags.
  assert not pose[38],pose[38]
  cx=max(0,min(3200-w,(hero[0]>>8)-w//2));cy=max(0,min(240,(hero[1]>>8)-95))
  tile=frame_image(atlas['frames'][anim['frame_indices'][pose[22]]],anim['palette'],(256,256),(128,128))
  if pose[18]:tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  image=Image.new('RGBA',(w,160));image.alpha_composite(tile,((anchor[0]>>8)-cx-128,(anchor[1]>>8)-cy-128));return image
 with tempfile.TemporaryDirectory()as td:
  f=Path(td)/'fixture.s2ob'
  def open_(data,w=240):
   f.write_bytes(data);h=c(*[str(p).encode()for p in paths],str(f).encode(),ctypes.byref(err));assert h,err.value;l.s2_session_set_viewport(h,w,160);return h
  # No AI, movement, VM timers or contacts before the actor enters the viewport.
  for ident in [63,9,31]:
   data=bytearray(raw);struct.pack_into('<HH',data,18+(ident-1)*44,360,350);h=open_(data);pix=(ctypes.c_uint32*76800)()
   try:
    l.s2_session_actor_snapshot(h,ident,a);initial=bytes(a)
    for t in range(400):
     assert l.s2_session_step(h,0,pix,38400,info)==0;l.s2_session_actor_snapshot(h,ident,a);assert bytes(a)==initial,(ident,t,'premature activation')
    l.s2_session_set_viewport(h,480,160)
    for t in range(20):assert l.s2_session_step(h,0,pix,76800,info)==0
    l.s2_session_actor_snapshot(h,ident,a);assert bytes(a)!=initial,'wide viewport did not activate visible AI'
    l.s2_session_set_viewport(h,240,160)
    l.s2_session_actor_snapshot(h,ident,a);initial=bytes(a)
    for t in range(200):
     assert l.s2_session_step(h,0,pix,38400,info)==0;l.s2_session_actor_snapshot(h,ident,a);assert bytes(a)==initial
    l.s2_session_destroy(h);h=None
    # A fresh source-position fixture places the hero inside the240px window.
    # Changing display width alone must never replace this source condition.
    struct.pack_into('<HH',data,18+(70-1)*44,300,350);h=open_(data,480)
    l.s2_session_actor_snapshot(h,ident,a);fresh_initial=bytes(a)
    for t in range(20):assert l.s2_session_step(h,0,pix,76800,info)==0
    l.s2_session_actor_snapshot(h,ident,a);assert bytes(a)!=fresh_initial,(ident,'visible actor did not activate')
    l.s2_session_reset(h);l.s2_session_actor_snapshot(h,ident,a);assert bytes(a)==fresh_initial
    runs.append(dict(actor=ident,initial_window=240,before_visible_frozen_frames=400,wide_view_active_frames=20,after_resize_frozen_frames=200,visible_position_fixture=True,reset=True))
   finally:
    if h:l.s2_session_destroy(h)
  # Held mushroom/stump pixels must cover Shrek, including lift animation frames.
  for ident,name in [(27,'mushroom'),(44,'stump'),(63,'pumpkin'),(9,'bandit'),(27,'mushroom_standing'),(44,'stump_standing')]:
   data=bytearray(raw);struct.pack_into('<HH',data,18+(ident-1)*44,35,358 if ident in [27,44]else 350);h=open_(data);pix=(ctypes.c_uint32*38400)();checked=0;frames=[]
   try:
    for t in range(1,85 if ident in [27,44] and not name.endswith('_standing')else 2):
     assert l.s2_session_step(h,2 if t==1 and ident in [27,44] and not name.endswith('_standing')else 0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,ident,a)
     if a[40]&1:continue
     fg=sprite(a,240);shrek=sprite(hero,240);im=Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA')
     for y in range(40,160):
      for x in range(240):
       expected=fg.getpixel((x,y))
       if expected[3] and shrek.getpixel((x,y))[3]:assert im.getpixel((x,y))==expected,(name,t,x,y,im.getpixel((x,y)),expected);checked+=1
     if t%4==0:frames.append(im.resize((960,640),Image.Resampling.NEAREST))
    assert checked>20,(name,checked);overlaps[name]=checked
    im.resize((960,640),Image.Resampling.NEAREST).save(ROOT/f'previews/native_foreground_{name}.png')
    if frames:frames[0].save(ROOT/f'previews/native_foreground_{name}.gif',save_all=True,append_images=frames[1:],duration=67,loop=0)
   finally:l.s2_session_destroy(h)
 # Independent pixel-grid oracle: every block is its source top-left, including edges.
 for w in [240,480,639]:
  for amount in range(65):
   source=[0xff000000|((x*13+y*71)&0xffffff)for y in range(160)for x in range(w)];pix=(ctypes.c_uint32*len(source))(*source);assert l.s2_mosaic_argb(amount,pix,w,160)==0;b=1+amount*15//64
   assert all(pix[y*w+x]==source[(y//b*b)*w+(x//b*b)]for y in range(160)for x in range(w));mosaicCases+=1
 report=dict(viewport_runs=runs,foreground_overlap_pixels=overlaps,mosaic_oracle_cases=mosaicCases,mismatches=0,device_tested=False);(ROOT/'docs/stage57_presentation_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
