#!/usr/bin/env python3
"""Check the optional sky repeat against original pixels, including negative offsets."""
import ctypes,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));P=ctypes.POINTER(ctypes.c_uint8)
 original=lib.s2_render_file;original.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[P,ctypes.c_size_t]
 repeat=lib.s2_render_file_background_repeat;repeat.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*6+[P,ctypes.c_size_t]
 path=str(ROOT/'extracted/scene_00/scene.s2lv').encode();period=304;h=160
 source=(ctypes.c_uint8*(period*h*4))();assert original(path,0,0,period,h,0,source,len(source))==0
 checked=0
 for width in [284,356,480,640]:
  for cx in [-305,-1,0,280,304,365]:
   out=(ctypes.c_uint8*(width*h*4))();assert repeat(path,cx,0,width,h,0,0,out,len(out))==0
   raw=bytes(out);ref=bytes(source)
   for y in range(h):
    expected=b''.join(ref[(y*period+(cx+x)%period)*4:(y*period+(cx+x)%period)*4+4] for x in range(width))
    assert raw[y*width*4:(y+1)*width*4]==expected
   checked+=width*h
 # Every existing native pixel in an original-size view is unchanged at positive camera offsets.
 for cx in [0,1,50,64]:
  old=(ctypes.c_uint8*(240*h*4))();new=(ctypes.c_uint8*(240*h*4))()
  assert original(path,cx,0,240,h,0,old,len(old))==0
  assert repeat(path,cx,0,240,h,0,0,new,len(new))==0
  assert bytes(old)==bytes(new)
 result={'sky_period_px':period,'wrapped_pixels_compared':checked,'repeat_cases':24,'original_view_comparisons':4,'mismatches':0,'scope':'Port-only horizontal repeat of scene00 decorative slot0; compares extracted artwork, not original GBA wide-screen behaviour. Collision, foreground and actors do not repeat.'}
 (ROOT/'docs/widescreen_background_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
