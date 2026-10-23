#!/usr/bin/env python3
"""Real water contacts, reset, HUD edges, source palette pixels and actor layering."""
import ctypes,json,struct,sys,tempfile
from PIL import Image
from verify_generic_runtime import Rom,ROOT,IP
from session_fixtures import without_intro
from extract_sprites import bank,frame_image
from pathlib import Path
I=ctypes.c_int32
def main():
 r=Rom(sys.argv[1]);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p;l.s2_session_set_auto_restart.argtypes=[ctypes.c_void_p,I]
 for n,a in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_health',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,I,I]),('s2_session_player_event',[ctypes.c_void_p,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_actor_anchor_q8',[IP,IP,I,I,IP]),('s2_session_step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,n).argtypes=a
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());hero=(I*320)();info=(I*8)();err=I();atlas=bank(r,0x34f248);red=next(a['palette']for a in atlas['animations']if a['record_offset']==0x34f43c);frames=[];cases=[];paletteChecks=layerChecks=0
 def image(pix,w):return Image.frombytes('RGBA',(w,160),bytes(pix),'raw','BGRA')
 def expected(palette=None,w=240):
  a=next(a for a in atlas['animations']if a['record_offset']==hero[47]-0x8000000);anchor=(I*2)();l.s2_actor_anchor_q8(ctypes.cast(ctypes.byref(hero,72*4),IP),hero,hero[18],hero[38],anchor)
  cx=max(0,min(3200-w,(hero[0]>>8)-w//2));cy=max(0,min(240,(hero[1]>>8)-95));assert not hero[18] and not hero[38]
  return frame_image(atlas['frames'][a['frame_indices'][hero[22]]],palette or a['palette'],(w,160),((anchor[0]>>8)-cx,(anchor[1]>>8)-cy))
 def check(im,sprite):
  count=0
  for y in range(40,160):
   for x in range(im.width):
    pixel=sprite.getpixel((x,y))
    if pixel[3]:assert im.getpixel((x,y))==pixel,(x,y,im.getpixel((x,y)),pixel);count+=1
  assert count>100;return count
 with tempfile.TemporaryDirectory()as tmp:
  f=Path(tmp)/'fixture.s2ob'
  def open_(data,width=240):
   f.write_bytes(data);h=create(*[str(x).encode()for x in paths],str(f).encode(),ctypes.byref(err));assert h,err.value;l.s2_session_set_auto_restart(h,0);assert l.s2_session_set_viewport(h,width,160)==0;return h,(ctypes.c_uint32*(width*160))()
  for x in [2415,2543]:
   for width in [240,480]:
    b=bytearray(raw);struct.pack_into('<HH',b,18+69*44,x,150);h,pix=open_(b,width)
    try:
     traces=[]
     for replay in range(2):
      if replay:assert l.s2_session_reset(h)==0
      first=finished=None;indices=set();trace=[]
      for t in range(1,121):
       buttons=3 if first and t%3 else 0
       assert l.s2_session_step(h,buttons,pix,len(pix),info)==0,(x,width,t,list(info));assert l.s2_session_snapshot(h,hero)==0
       trace.append(list(hero))
       if hero[80]==14:
        if first is None:first=t
        assert hero[47]==0x834f46c;indices.add(hero[22])
        if hero[20]&255 and finished is None:finished=t
       elif first is not None:raise AssertionError(('escaped drowning',x,t,hero[80]))
       if x==2415 and width==240 and replay==0 and t%2==0:frames.append(image(pix,width).convert('RGB').resize((960,640),Image.Resampling.NEAREST))
      assert first and finished and finished-first==30 and len(indices)==10,(x,width,first,finished,indices);assert l.s2_session_health(h)==0
      requests=(I*(4096*8))();n=l.s2_session_requests(h,requests,4096);assert n>=0;assert any(requests[i*8+1]==11 and requests[i*8+2]==0x8053c9c for i in range(n)),('no water sound',n)
      traces.append(trace);cases.append({'x':x,'width':width,'replay':replay,'entry':first,'finished':finished,'frames':len(indices)})
     assert traces[0]==traces[1],('reset differs',x,width)
    finally:l.s2_session_destroy(h)
  crops=[]
  for w in [240,480]:
   h,pix=open_(raw,w)
   try:
    assert l.s2_session_step(h,0,pix,len(pix),info)==0;im=image(pix,w);crops.append(im.crop((0,0,40,38)).tobytes())
    if w==480:im.resize((1440,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_hud_edges_wide.png')
   finally:l.s2_session_destroy(h)
  assert crops[0]==crops[1]
  # Source hint60, NPC68 and butterfly11 overlap the player in this isolated fixture.
  b=bytearray(raw)
  for id in [60,68,11]:struct.pack_into('<HH',b,18+(id-1)*44,35,350)
  h,pix=open_(b)
  try:
   assert l.s2_session_step(h,0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);im=image(pix,240);layerChecks=check(im,expected());im.resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/native_hint_behind_player.png')
  finally:l.s2_session_destroy(h)
  # Accepted damage at tick0: exact source red palette until deadline4, then normal.
  h,pix=open_(raw)
  try:
   assert l.s2_session_player_event(h,(I*3)(1,38,1))==1
   for t in range(1,9):
    assert l.s2_session_step(h,0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);im=image(pix,240);paletteChecks+=check(im,expected(red if t<4 else None))
    if t in [1,4]:im.resize((960,640),Image.Resampling.NEAREST).save(ROOT/f'previews/native_damage_palette_tick{t}.png')
  finally:l.s2_session_destroy(h)
 frames[0].save(ROOT/'previews/native_water_death.gif',save_all=True,append_images=frames[1:],duration=33,loop=0);frames[15].save(ROOT/'previews/native_water_death.png')
 report={'water_cases':cases,'layer_opaque_pixels_checked':layerChecks,'damage_palette_pixels_checked':paletteChecks,'hud_edge_equal_at_widths':[240,480],'mismatches':0,'scope':'Native real water event40 contact, original10-frame drowning+sound103, death holds and menu reset; no whole game-over manager or Android execution. Source atlas opaque pixels independently compared for layer order and four-tick red palette.'};(ROOT/'docs/session_water_visuals_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':
 from pathlib import Path
 main()
