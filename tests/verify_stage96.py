from pathlib import Path
import ctypes as C,subprocess,json
R=Path(__file__).resolve().parents[1];lib=C.CDLL(str(R/'native/build/libshrek_scene.so'));P=C.c_void_p;I=C.c_int32;IP=C.POINTER(I)
f=lib.s2_frontend_create;f.argtypes=[C.c_char_p]*2;f.restype=P
for n,args in [('destroy',[P]),('progress',[P,IP]),('open',[P,I,I]),('restore',[P,IP]),('step',[P,I]),('touch',[P,I,I]),('snapshot',[P,IP]),('presentation',[P,IP]),('render',[P,C.c_void_p,C.c_size_t]),('test_books',[P,I]),('startup_fade',[P]),('action',[P]),('sound',[P])]:getattr(lib,'s2_frontend_'+n).argtypes=args
h=f(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'android/app/src/main/assets/session/sprites/bank_328294/bank.s2sp').encode());assert h
state=(I*9)();pix=(C.c_uint32*38400)();presentation=(I*8)()
def snap():lib.s2_frontend_snapshot(h,state);return list(state)
def render():assert lib.s2_frontend_render(h,pix,38400)==0;return bytes(pix)
def press(b):lib.s2_frontend_step(h,b);lib.s2_frontend_step(h,0)
cases=0
for slot in range(3):
 for done in range(26):
  mask=(1<<done)-1;lib.s2_frontend_progress(h,(I*7)(7,*([mask]*3),0,0,0))
  for book in range(min(4,done//5)+1):
   available=min(5,max(1,done-book*5+1));lib.s2_frontend_restore(h,(I*9)(4,4,book,slot,0,0,0,0,0))
   for t in range(20):lib.s2_frontend_step(h,0)
   assert snap()[1]==available-1,(done,book,snap())
   for b in [128,64,16,32]:
    for t in range(7):
     old=snap()[1];press(b);assert snap()[1]==(old+(1 if b in [128,16]else -1))%available
   for row in range(available,5):
    old=snap();left=render();lib.s2_frontend_touch(h,150,12+row*22);assert snap()==old and render()==left and lib.s2_frontend_action(h)==0
   cases+=1
# With zero progress even the preview image stays unchanged under all navigation buttons.
lib.s2_frontend_progress(h,(I*7)(1,0,0,0,0,0,0));lib.s2_frontend_restore(h,(I*9)(4,0,0,0,0,0,0,0,0))
for i in range(20):lib.s2_frontend_step(h,0)
original=render()
for b in [16,32,64,128]*10:
 press(b);image=render();assert snap()[1]==0
 for y in range(160):assert original[(y*240)*4:(y*240+110)*4]==image[(y*240)*4:(y*240+110)*4]
# Cheat toggle still permits all five entries and bonus game previews.
lib.s2_frontend_test_books(h,1)
for book in range(6):
 lib.s2_frontend_restore(h,(I*9)(4,0,book,0,0,0,0,0,0))
 for i in range(20):lib.s2_frontend_step(h,0)
 for row in range(5):assert snap()[1]==row;press(128)
 assert snap()[1]==0
# Initial black hold and 16-step monotonic fade, followed by an unfiltered source frame.
lib.s2_frontend_open(h,11,0);lib.s2_frontend_startup_fade(h);levels=[]
for tick in range(29):
 image=render();lib.s2_frontend_presentation(h,presentation);levels.append(presentation[2]);assert snap()[0]==11 and snap()[1]==0
 if tick<=12:assert set(pix)=={0xff000000}
 lib.s2_frontend_step(h,0)
assert levels[:13]==[64]*13 and levels[13:]==list(range(60,-1,-4)),levels
lib.s2_frontend_open(h,11,0);unfiltered=render();assert image==unfiltered
lib.s2_frontend_destroy(h)
exe=R/'native/build/stage96_pause_fixture';subprocess.run(['g++','-std=c++17','-O2',str(R/'tests/stage96_pause_fixture.cpp'),'-L'+str(R/'native/build'),'-lshrek_scene','-Wl,-rpath,'+str(R/'native/build'),'-o',str(exe)],check=True);from fixture_workspace import prepare_workspace
prepare_workspace(R)
subprocess.run([str(exe)],cwd=R,check=True)
report=dict(progress_slot_book_cases=cases,closed_touch_rejected=True,locked_preview_unchanged=True,test_unlock_and_bonus_navigation=True,startup_black_hold_frames=12,startup_fade_frames=16,paused_scene_width_cases=60,nested_minigame=True,pause_does_not_advance_state=True,device_tested=False)
(R/'docs/stage96_validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS Stage96 frontend',cases,'progress/slot/book cases, preview and startup fade')
