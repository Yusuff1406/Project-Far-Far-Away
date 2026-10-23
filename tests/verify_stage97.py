from pathlib import Path
import ctypes as C,subprocess,json
R=Path(__file__).resolve().parents[1];exe=R/'native/build/stage97_fixture'
subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage97_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True);from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
lib=C.CDLL(str(R/'native/build/libshrek_scene.so'));P=C.c_void_p;I=C.c_int32;IP=C.POINTER(I);f=lib.s2_frontend_create;f.argtypes=[C.c_char_p]*2;f.restype=P
for n,args in [('destroy',[P]),('progress',[P,IP]),('open',[P,I,I]),('step',[P,I]),('sound',[P]),('snapshot',[P,IP]),('presentation',[P,IP]),('render',[P,P,C.c_size_t]),('test_books',[P,I]),('epilogue',[P,I])]:getattr(lib,'s2_frontend_'+n).argtypes=args
h=f(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'android/app/src/main/assets/session/sprites/bank_328294/bank.s2sp').encode());assert h
s=(I*9)();pix=(C.c_uint32*38400)();lib.s2_frontend_open(h,4,0)
for t in range(19):lib.s2_frontend_step(h,0)
for key in [128,64,16,32]*3:
 lib.s2_frontend_step(h,key);assert lib.s2_frontend_sound(h)==63;lib.s2_frontend_snapshot(h,s);assert s[1]==0 and s[4]==0
 lib.s2_frontend_step(h,0)
lib.s2_frontend_test_books(h,1);counts=[]
for scene,group,count in [(17,0,4),(5,1,3),(21,2,4),(22,3,3),(15,4,2),(16,5,4)]:
 for repeat in range(2):
  assert lib.s2_frontend_epilogue(h,scene)==1
  for t in range(20):lib.s2_frontend_step(h,0)
  panels=set()
  for t in range(220):
   lib.s2_frontend_snapshot(h,s)
   if s[0]!=14:break
   assert s[2]==group;panels.add(s[1]);lib.s2_frontend_render(h,pix,38400);lib.s2_frontend_step(h,1);lib.s2_frontend_step(h,0)
   for k in range(32):lib.s2_frontend_step(h,0)
  assert panels==set(range(count)),(scene,panels);counts.append(len(panels))
lib.s2_frontend_destroy(h)
(R/'docs/stage97_validation.json').write_text(json.dumps(dict(acceleration_scenes=30,speed_choices=[2,3,4],native_state_and_pixels_identical=True,ending_fairy_three_hits=True,fairy_direct_fade_without_victory=True,blocked_navigation_sound=63,blocked_navigation_restarts_blink=True,cinematic_groups=6,cinematic_panels=20,repeat_cinematic_tests=2,device_tested=False),indent=2)+'\n');print('PASS Stage97: blocked selection feedback and all 20 source cinematic panels twice')
