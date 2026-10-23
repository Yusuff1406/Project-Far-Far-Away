from verify_puss_boss import *
from extract_collision import scene_collision
u.mem_write(0x02000800,struct.pack('<3I',0x08000000+scene_collision(r,5)['root_offset'],240*256,160*256))
p,s=setup();step=l.s2_puss_boss_step;step.argtypes=[C.c_char_p,IP,IP,I,I,FC,SINK,P]
for tick in range(1,2200):
 u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));fx.clear();orig.clear();o.call(0x08018208,o.actor);assert step(str(ROOT/'collision/scene_05/scene.s2cl').encode(),p,s,20,tick,fetch,sink,None)==0;compare(('fullframe',tick),p,s)
 xy=struct.unpack('<2i',u.mem_read(o.actor+0x178,8));assert list(p[:2])==list(xy),(tick,list(p[:2]),xy,list(s[:9]));
report=dict(frames=tick,mismatches=0,scope='Original18208 full update, actual scene5 collision, no player contacts.');(ROOT/'docs/puss_boss_frames_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
