#!/usr/bin/env python3
import argparse,ctypes,json,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract import Rom
from extract_sprites import bank,roots,frame_image

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom)
 lib=ctypes.CDLL(str((root/'native/build/libshrek_scene.so').resolve()));fn=lib.s2_sprite_render_file
 fn.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];fn.restype=ctypes.c_int;cases=0;bytes_count=0
 for ro in roots(r):
  d=bank(r,ro);path=str((root/'sprites'/d['name']/'bank.s2sp').resolve()).encode();tests=[]
  for anim in d['animations']:
   positions=range(anim['sequence_count']) if ro==0x34f248 else sorted(set([0,anim['sequence_count']-1]))
   tests.extend((anim,i,flip) for i in positions for flip in [0,1])
  for anim,index,flip in tests:
   out=(ctypes.c_uint8*(160*160*4))();code=fn(path,anim['index'],index,flip,160,160,80,100,out,len(out))
   if code:raise AssertionError((ro,anim['index'],index,code))
   im=frame_image(d['frames'][anim['frame_indices'][index]],anim['palette'])
   if flip:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if bytes(out)!=im.tobytes():raise AssertionError(('pixels',ro,anim['index'],index,flip))
   cases+=1;bytes_count+=len(out)
 result={'cases':cases,'pixels_compared':bytes_count//4,'mismatches':0,'coverage':'Every Shrek ogre sequence frame; first and last sequence frames of every animation in all banks; both facing directions','method':'Independent Python/C++ multipart sprite rendering comparison; no original GPU execution'}
 (root/'docs/sprite_render_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
