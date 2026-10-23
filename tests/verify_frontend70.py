#!/usr/bin/env python3
"""Source names rendered as real glyph ink; direct chapter routes and pause Start."""
import ctypes as C,struct,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,args in [('open',[P,I,I]),('step',[P,I]),('snapshot',[P,C.POINTER(I)]),('restore',[P,C.POINTER(I)]),('render',[P,P,C.c_size_t]),('action',[P]),('touch',[P,I,I]),('destroy',[P])]:getattr(l,'s2_frontend_'+n).argtypes=args
h=l.s2_frontend_create(str(ROOT/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(ROOT/'sprites/bank_328294/bank.s2sp').encode());assert h;pix=(C.c_uint32*38400)();state=(I*9)();rom=Path(sys.argv[1]).read_bytes();names=rom[0x49328:].split(b'\0')[0].replace(b'\1\1',b'').split(b'\n');checked=[]
try:
 # Compare actual ink pixels to independently decoded original8px font.
 font=0x316a34;stride,glyphs,w,height=struct.unpack_from('<4B',rom,font);index=rom[font+8:font+264];adv=rom[font+264:font+520]
 for name in [b'Karthik Bala',b'Tobi Saulnier',b'Craig Derrick',b'Robert Trevellyan',b'Brian Sox',b'Yin Zhang']:
  row=names.index(name);tick=2*(24+row*10-64)
  l.s2_frontend_restore(h,(I*9)(8,0,0,0,tick,0,0,0,0))
  for _ in range(16):l.s2_frontend_step(h,0)
  l.s2_frontend_render(h,pix,38400);x=120-sum(adv[c]for c in name)//2;y=64;ink=0
  for c in name:
   if c!=32:
    for py in range(8):
     for px in range(8):
      b=rom[font+520+index[c]*stride+py*4+px//2];n=(b>>((px&1)*4))&15
      if not n:continue
      v=struct.unpack_from('<H',rom,0x30f9ac+n*2)[0];color=0xff000000|((v&31)*255//31<<16)|(((v>>5)&31)*255//31<<8)|((v>>10)&31)*255//31
      assert pix[(y+py)*240+x+px]==color,(name,px,py);ink+=1
   x+=adv[c]
  assert ink>30;checked.append(dict(name=name.decode(),ink_pixels=ink))
  if name==b'Karthik Bala':Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/stage70_credits_names.png')
 l.s2_frontend_restore(h,(I*9)(7,1,0,0,0,1,0,0,0));l.s2_frontend_snapshot(h,state);assert state[0]==4,'restored obsolete preview prompt'
 l.s2_frontend_open(h,5,2);l.s2_frontend_step(h,8)
 for _ in range(16):l.s2_frontend_step(h,0)
 assert l.s2_frontend_action(h)==2,'Start selected Quit Game instead of resuming'
finally:l.s2_frontend_destroy(h)
report=dict(original_names_visible=checked,pause_start_resumes=True,mismatches=0,device_tested=False,scope='Actual native frame compared to independently decoded source small-font glyphs and palette for six named credits. Candle appearance and boot legal timing are checked separately by Stage71.')
(ROOT/'docs/frontend70_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
