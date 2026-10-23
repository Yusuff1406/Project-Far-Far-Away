#!/usr/bin/env python3
"""ROM glyph atlas/palette comparison, including advance-only spaces."""
import ctypes,json,struct,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I);FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_int,ctypes.c_void_p)
def main():
 rom=Path(sys.argv[1]).read_bytes()
 @FC
 def fetch(a,out,n,ctx):
  off=a-0x8000000
  if off<0 or off+n*4>len(rom):return 0
  for i,v in enumerate(struct.unpack_from('<'+'i'*n,rom,off)):out[i]=v
  return 1
 source='''#include "dialogue_presentation.h"
extern "C" int draw(const char* text,uint32_t* pixels,DialogueFetch fetch){return s2_dialogue_draw_text(std::vector<std::string>{text},0,240,pixels,fetch,nullptr);}
'''
 with tempfile.TemporaryDirectory()as tmp:
  cpp=Path(tmp)/'font.cpp';cpp.write_text(source);out=Path(tmp)/'font.so';subprocess.run(['g++','-std=c++17','-shared','-fPIC','-I'+str(ROOT/'native'),str(cpp),'-L'+str(ROOT/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(ROOT/'native/build'),'-o',str(out)],check=True)
  l=ctypes.CDLL(str(out));draw=l.draw;draw.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_uint32),FC];cases=0
  for text in[b' ',b'   ',b'A A',b'B   B',*[bytes([c])for c in range(33,136)]]:
   pixels=(ctypes.c_uint32*38400)(*([0xff202020]*38400));assert draw(text,pixels,fetch)==0;expected=[0xff202020]*38400;x=65
   for ch in text:
    width=rom[0x30fbac+264+ch]
    if ch!=32:
     glyph=rom[0x30fbac+8+ch];raw=rom[0x30fbac+520+glyph*128:0x30fbac+520+(glyph+1)*128]
     for y in range(16):
      for px in range(16):
       tile=(y//8)*2+px//8;v=(raw[tile*32+(y%8)*4+(px%8)//2]>>(4*(px%2)))&15
       if not v:continue
       color=struct.unpack_from('<H',rom,0x30f9ac+v*2)[0];rgb=0xff000000|((color&31)*255//31<<16)|(((color>>5)&31)*255//31<<8)|(((color>>10)&31)*255//31);xx=x+px;yy=18+y
       if 65<=xx<207 and yy<61:expected[yy*240+xx]=rgb
    x+=width
   assert list(pixels)==expected,text;cases+=1
 report={'glyph_and_spacing_cases':cases,'mismatches':0,'scope':'Native rendering against ROM map/width/4bpp atlas/palette, ASCII and button glyphs. Spaces only advance, including leading/consecutive spaces. Native wrapping is tested in full conversations; original hardware blitter not executed.'};(ROOT/'docs/dialogue_font_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
