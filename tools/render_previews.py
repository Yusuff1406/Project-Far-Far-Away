#!/usr/bin/env python3
"""Reference tile renderer + pixel comparison against the portable C++ module."""
import argparse,ctypes,json,struct,sys
from pathlib import Path
from PIL import Image,ImageDraw
from extract import Rom

def reference(scene,pal,gfx,cx,cy,w,h,slot=-1):
 out=bytearray(w*h*4);palette=struct.unpack('<256H',pal)
 layers=sorted([l for l in scene['layers'] if slot<0 or l['slot']==slot],key=lambda l:-l['priority_or_bg_index'])
 for l in layers:
  ox=cx*l['scroll_x_q8']//256 if slot<0 else cx;oy=cy*l['scroll_y_q8']//256 if slot<0 else cy
  tw,th=l['tile_width'],l['tile_height'];entries=l['entries'];bpp=l['bits_per_pixel']
  for y in range(h):
   yy=y+oy
   if not 0<=yy<th*8:continue
   for x in range(w):
    xx=x+ox
    if not 0<=xx<tw*8:continue
    v=entries[(yy//8)*tw+xx//8];idx=v&0xfff;px=xx%8;py=yy%8
    if v&0x1000:px=7-px
    if v&0x2000:py=7-py
    if bpp==8:k=gfx[0][idx*64+py*8+px]
    else:
     k=(gfx[1][idx*32+py*4+px//2]>>((px&1)*4))&15
     if not k:continue
     k+=(v>>14)*16
    if not k:continue
    c=palette[k];o=(y*w+x)*4;out[o:o+4]=bytes([(c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31,255])
 return bytes(out)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);out=root/'previews';out.mkdir(exist_ok=True);rom=Rom(a.rom)
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));fn=lib.s2_render_file
 fn.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t];fn.restype=ctypes.c_int
 cards=[];cases=0
 for n in range(30):
  scene,pal,gfx=rom.scene(n);path=str((root/f'extracted/scene_{n:02d}/scene.s2lv').resolve()).encode()
  camera=(0,max(0,scene['height_px']-160))
  for cx,cy,slot in [(0,0,-1),(*camera,-1),(max(0,scene['width_px']-240),max(0,scene['height_px']-160),-1),(0,0,3)]:
   buffer=(ctypes.c_uint8*(240*160*4))();code=fn(path,cx,cy,240,160,slot,buffer,len(buffer))
   if code:raise RuntimeError((n,code))
   expected=reference(scene,pal,gfx,cx,cy,240,160,slot)
   if bytes(buffer)!=expected:raise AssertionError(f'Native/Python pixel mismatch scene {n}, camera {cx},{cy}, slot {slot}')
   cases+=1
  frame=reference(scene,pal,gfx,*camera,240,160)
  image=Image.frombytes('RGBA',(240,160),frame);bg=Image.new('RGBA',image.size,(24,24,24,255));bg.alpha_composite(image);bg=bg.convert('RGB');bg.save(out/f'scene_{n:02d}.png');cards.append(bg)
  if n==0:bg.resize((960,640),Image.Resampling.NEAREST).save(out/'first_scene.png')
  # Full original gameplay/background layer, with no guess about camera or parallax.
  l=next(l for l in scene['layers'] if l['slot']==3)
  fg=Image.frombytes('RGBA',(l['tile_width']*8,l['tile_height']*8),reference(scene,pal,gfx,0,0,l['tile_width']*8,l['tile_height']*8,3))
  fg.save(out/f'scene_{n:02d}_main_layer.png')
 sheet=Image.new('RGB',(5*250,6*188),(20,22,27));draw=ImageDraw.Draw(sheet)
 for n,im in enumerate(cards):
  x=(n%5)*250+5;y=(n//5)*188+4;sheet.paste(im,(x,y));draw.text((x,y+164),f'Scene {n:02d}',fill='white')
 sheet.save(out/'all_scenes.png')
 result={'cases':cases,'pixels_compared':cases*240*160,'mismatches':0,'method':'Independent Python/C++ viewport rendering comparison; does not establish pixel equivalence with original GBA execution'}
 (root/'docs/render_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
