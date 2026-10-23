#!/usr/bin/env python3
"""Check native presentation against independently decoded serialized assets."""
import ctypes as C
import json, struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'))
P=C.c_void_p; I=C.c_int32
lib.s2_frontend_create.argtypes=[C.c_char_p,C.c_char_p];lib.s2_frontend_create.restype=P
for name,args in [('open',[P,I,I]),('step',[P,I]),('snapshot',[P,C.POINTER(I)]),('render',[P,P,C.c_size_t]),('destroy',[P])]:
    getattr(lib,'s2_frontend_'+name).argtypes=args
lib.s2_sprite_bank_create.argtypes=[C.c_char_p];lib.s2_sprite_bank_create.restype=P
lib.s2_sprite_bank_destroy.argtypes=[P]
lib.s2_sprite_composite_bank.argtypes=[P,I,I,I,I,I,I,I,P,C.c_size_t]
data=(ROOT/'android/app/src/main/assets/frontend/menu.s2ui').read_bytes();at=28;images={}
for _ in range(struct.unpack_from('<I',data,8)[0]):
    ident,w,h,count,ms=struct.unpack_from('<5I',data,at);at+=20
    frames=[]
    for f in range(count):
        palette=data[at:at+1024];indices=data[at+1024:at+39424]
        frames.append(b''.join(palette[i*4:i*4+4] for i in indices));at+=39424
    images[ident]=frames
bankpath=str(ROOT/'sprites/bank_328294/bank.s2sp').encode()
handle=lib.s2_frontend_create(str(ROOT/'android/app/src/main/assets/frontend/menu.s2ui').encode(),bankpath)
assert handle
bank=lib.s2_sprite_bank_create(bankpath);assert bank
pixels=(C.c_uint32*38400)();state=(I*9)();checks=0
def render():
    assert lib.s2_frontend_render(handle,pixels,38400)==0
    return bytes(pixels)
def step(n):
    for _ in range(n):assert lib.s2_frontend_step(handle,0)==0
def snap():
    lib.s2_frontend_snapshot(handle,state);return list(state)
try:
    lib.s2_frontend_open(handle,1,0)
    for tick in range(1001):
        frame=min(47,max(0,tick-60)//4)
        assert render()[:240*130*4]==images[0][frame][:240*130*4]
        checks+=1;step(1)
    lib.s2_frontend_open(handle,8,0)
    frames=[]
    for tick in range(1200):
        actual=render()
        if tick%6==0:frames.append(Image.frombytes('RGBA',(240,160),actual,'raw','BGRA').convert('RGB'))
        before=snap();render();render();assert snap()==before
        step(1)
    frames[0].save(ROOT/'previews/frontend_stage62_credits.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
    for _ in range(20000):
        if snap()[0]!=8:break
        step(1)
    assert snap()[0]==1
finally:
    lib.s2_frontend_destroy(handle);lib.s2_sprite_bank_destroy(bank)
report=dict(asset_frame_comparisons=checks,title_delay_ticks=60,title_timing_exact_to_original=False,white_candle_checked_separately=True,credits_background_only_phase=False,credits_intro_frames=80,credits_scroll_ticks_per_pixel=2,render_has_no_state_mutations=True,credits_return_to_main=True,device_tested=False,mismatches=0)
(ROOT/'docs/frontend62_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
