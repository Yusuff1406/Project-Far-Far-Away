"""Original six book captions and 2px/tick native pointer owner."""
import ctypes as C,json,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tests'))
from verify_generic_runtime import Original,Rom
I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'))
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,a in [('progress',[P,IP]),('restore',[P,IP]),('open',[P,I,I]),('step',[P,I]),('presentation',[P,IP]),('destroy',[P])]:getattr(l,'s2_frontend_'+n).argtypes=a
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h;l.s2_frontend_progress(h,(I*7)(7,0x1ffffff,0x1ffffff,0x1ffffff,0,0,0))
r=Rom(sys.argv[1]);o=Original(r);meta=json.loads((R/'docs/frontend_resources.json').read_text());titles=[]
for i in range(6):
 pointer=struct.unpack_from('<I',r.data,0x45048+i*4)[0];pointer=struct.unpack_from('<I',r.data,pointer-0x8000000)[0];name=r.data[pointer-0x8000000:].split(b'\0')[0].decode();assert meta['labels'][f'book_{i}']==name;titles.append(name)
# The source widget update15860 invokes B624 twice: callsites15874/1589E.
for at in [0x15874,0x1589e]:
 hi,lo=struct.unpack_from('<2H',r.data,at);v=hi&2047;v=v-2048 if v&1024 else v;assert at+4+(v<<12)+((lo&2047)<<1)==0xb624
positions=[(40,68),(62,84),(83,93),(105,102),(125,108),(178,115)];frames=0
for i in range(6):
 for mask,delta in [(16,1),(32,-1)]:
  l.s2_frontend_restore(h,(I*9)(3,i,0,0,0));l.s2_frontend_open(h,3,i);l.s2_frontend_step(h,mask);x,y=positions[i];tx,ty=positions[(i+delta)%6];a=0x02030000;o.u.mem_write(a,bytes(40));o.u.mem_write(a+0x100,struct.pack('<4i',x,y,tx,ty));o.call(0x0800b67c,a,a+0x100,a+0x108)
  for tick in range((max(abs(tx-x),abs(ty-y))+1)//2):
   o.call(0x0800b624,a)
   if struct.unpack('<2i',o.u.mem_read(a,8))!=(tx,ty):o.call(0x0800b624,a)
   l.s2_frontend_step(h,0);p=(I*8)();l.s2_frontend_presentation(h,p);expected=list(struct.unpack('<2i',o.u.mem_read(a,8)));assert list(p)[4:6]==expected,(i,mask,tick,list(p),expected);frames+=1
l.s2_frontend_destroy(h);report=dict(original_book_titles=titles,source_pointer_frames=frames,source_callsites=['08015874','0801589E'],device_tested=False)
(R/'docs/stage89_frontend_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
