#!/usr/bin/env python3
"""Cached direct ARGB composition versus the unchanged RGBA file renderer."""
import ctypes,json,tempfile,time,statistics
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_sprite_bank_create;create.argtypes=[ctypes.c_char_p];create.restype=ctypes.c_void_p;destroy=lib.s2_sprite_bank_destroy;destroy.argtypes=[ctypes.c_void_p]
 cached=lib.s2_sprite_composite_bank;cached.argtypes=[ctypes.c_void_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t]
 old=lib.s2_sprite_render_file;old.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];cases=pixels=0
 for path in sorted((ROOT/'sprites').glob('*/bank.s2sp')):
  metadata=json.loads((path.parent/'bank.json').read_text());handle=create(str(path).encode());assert handle
  try:
   for anim in metadata['animations']:
    for seq in range(anim['sequence_count']):
     for flip in (0,1):
      width=240 if seq%2 else 373;height=160;xy=[(width//2,100),(-8,12),(width+8,168)][seq%3];rgba=(ctypes.c_uint8*(width*height*4))();frame=(ctypes.c_uint32*(width*height))(*([0x77123456]*(width*height)))
      assert old(str(path).encode(),anim['index'],seq,flip,width,height,*xy,rgba,len(rgba))==0
      assert cached(handle,anim['index'],seq,flip,width,height,*xy,frame,len(frame))==0
      raw=np.frombuffer(rgba,dtype=np.uint8).reshape(-1,4);expected=np.full(width*height,0x77123456,dtype=np.uint32);mask=raw[:,3]!=0;colors=raw.astype(np.uint32);expected[mask]=(0xff000000|(colors[mask,0]<<16)|(colors[mask,1]<<8)|colors[mask,2]);expected=expected.tobytes()
      assert bytes(frame)==expected,(path.name,anim['index'],seq,flip);cases+=1;pixels+=width*height
   frame=(ctypes.c_uint32*38400)(*([0x77123456]*38400));before=bytes(frame)
   for args in [(-1,0,0,240,160,0,0),(0,-1,0,240,160,0,0),(0,0,0,0,160,0,0)]:assert cached(handle,*args,frame,len(frame))==-1 and bytes(frame)==before
   assert cached(handle,0,0,0,240,160,2147483647,-2147483648,frame,len(frame))==0 and bytes(frame)==before
  finally:destroy(handle)
 path=ROOT/'sprites/bank_32eb28/bank.s2sp'
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'bank.s2sp';p.write_bytes(path.read_bytes());handle=create(str(p).encode());assert handle;p.unlink();buf=(ctypes.c_uint32*38400)();assert cached(handle,3,0,0,240,160,120,80,buf,len(buf))==0;assert not create(str(p).encode());destroy(handle)
  for raw in (b'',b'NOPE'+path.read_bytes()[4:],path.read_bytes()[:-1]):p.write_bytes(raw);assert not create(str(p).encode())
 seq_count=json.loads((path.parent/'bank.json').read_text())['animations'][3]['sequence_count'];rgba=(ctypes.c_uint8*153600)();frame=(ctypes.c_uint32*38400)();h=create(str(path).encode());timings=[]
 for run in range(5):
  start=time.perf_counter()
  for n in range(300):assert old(str(path).encode(),3,n%seq_count,0,240,160,120,80,rgba,len(rgba))==0
  a=time.perf_counter()-start;start=time.perf_counter()
  for n in range(300):assert cached(h,3,n%seq_count,0,240,160,120,80,frame,len(frame))==0
  timings.append([a,time.perf_counter()-start])
 destroy(h);median=[statistics.median(x[i] for x in timings) for i in (0,1)]
 report={'composition_cases':cases,'pixels_compared':pixels,'banks':16,'mismatches':0,'immutable_snapshot_after_source_unlink':True,'invalid_requests_preserve_frame':True,'isolated_coin_renderer_median_seconds_300_calls':{'file_rgba':median[0],'cached_argb':median[1]},'isolated_ratio':median[0]/median[1],'scope':'All sequence frames and both facings, selected centre/edge/offscreen placements; host timing includes different output formats, not whole-game FPS or Android performance.'};(ROOT/'docs/sprite_cache_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
