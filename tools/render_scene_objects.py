#!/usr/bin/env python3
"""Original scene placements with verified generic-route initial artwork."""
import ctypes,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];render.restype=ctypes.c_int;sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];sprite.restype=ctypes.c_int
 w,h=3200,400;buf=(ctypes.c_uint8*(w*h*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,0,w,h,-1,buf,len(buf))==0;im=Image.new('RGBA',(w,h),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)));bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];rows=json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'];drawn=[];unknown=[]
 for row in rows:
  info=bindings.get(str(row['type']));x,y=row['anchor_px'];flags=row['flags_byte']
  if not info or flags&2:unknown.append(row);continue
  bank=str(ROOT/'sprites'/info['bank']/'bank.s2sp').encode();assert sprite(bank,info['index'],0,flags&1,w,h,x,y,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(w,h),bytes(buf)));drawn.append(row['instance_id'])
 d=ImageDraw.Draw(im)
 for row in unknown:
  x,y=row['anchor_px'];d.ellipse((x-3,y-3,x+3,y+3),fill=(255,80,210,255));d.text((x+5,y-10),str(row['type']),fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
 # Put the status strip outside the level image to avoid covering source artwork.
 sheet=Image.new('RGB',(w,h+30),(20,20,20));sheet.paste(im.convert('RGB'),(0,0));ImageDraw.Draw(sheet).text((8,h+8),'SCENE 00: original placements / initial artwork only / pink markers: unresolved constructor routes',fill=(255,255,255));sheet.save(ROOT/'previews/scene_00_object_placements.png')
 crop=im.crop((0,160,480,400)).convert('RGB').resize((960,480),Image.Resampling.NEAREST);crop.save(ROOT/'previews/scene_00_objects_detail.png')
 result={'scene':0,'records':len(rows),'initial_artwork_drawn':len(drawn),'marker_only':len(unknown),'drawn_instance_ids':drawn,'marker_types':sorted(set(x['type'] for x in unknown)),'scope':'Verified factory definition -> initial sprite binding for generic constructor paths; placement anchors from original spawn loop, flipX from parameter bit0. No simulation, removal-state filtering, secondary variants or enemy behavior; flipY cases shown as markers.'};(ROOT/'docs/object_placement_preview.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
