#!/usr/bin/env python3
"""All-map native loading, exact cached backgrounds, gallery and state contracts."""
import ctypes as C,hashlib,json,struct,tempfile,shutil
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];P=C.c_void_p;I=C.c_int32;IP=C.POINTER(I)
lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));assets=ROOT/'android/app/src/main/assets/campaign'
lib.s2_campaign_create.argtypes=[C.c_char_p];lib.s2_campaign_create.restype=P
for name,args in [('destroy',[P]),('select_scene',[P,I]),('navigate',[P,I]),('mode',[P,I]),('bank',[P,I]),('animation',[P,I]),('pan',[P,I,I]),('option',[P,I,I]),('step',[P,I]),('info',[P,IP]),('save',[P,IP]),('restore',[P,IP]),('render',[P,I,P,C.c_size_t])]:getattr(lib,'s2_campaign_'+name).argtypes=args
lib.s2_render_file.argtypes=[C.c_char_p,I,I,I,I,I,P,C.c_size_t]
lib.s2_render_file_background_repeat.argtypes=[C.c_char_p,I,I,I,I,I,I,P,C.c_size_t]
h=lib.s2_campaign_create(str(assets).encode());assert h
meta=json.loads((ROOT/'docs/campaign_visual_resources.json').read_text());source=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records'];cards=[];comparisons=0;gallery=0
def info():
    out=(I*16)();assert lib.s2_campaign_info(h,out)==0;return list(out)
def save():
    out=(I*12)();assert lib.s2_campaign_save(h,out)==0;return list(out)
def render(w):
    out=(C.c_uint32*(w*160))();assert lib.s2_campaign_render(h,w,out,len(out))==0;return bytes(out)
try:
    for row in source:
        n=row['scene'];assert (assets/f'scenes/scene_{n:02}.s2lv').read_bytes()==(ROOT/f'extracted/scene_{n:02}/scene.s2lv').read_bytes()
        assert lib.s2_campaign_select_scene(h,n)==0;s=info();assert s[1:6]==[n,row['thumbnail_order'],row['width'],row['height'],row['object_count']]
        assert lib.s2_campaign_option(h,2,0)==0
        for width in [240,426,640]:
            for dx,dy in [(0,0),(16384,16384),(-16384,-16384)]:
                assert lib.s2_campaign_pan(h,dx,dy)==0;actual=render(width);s=info();assert 0<=s[14]<=max(0,row['width']-width)and 0<=s[15]<=max(0,row['height']-160)
                view=min(width,row['width']);offset=(width-view)//2;expected=(C.c_uint8*(view*160*4))()
                args=[str(assets/f'scenes/scene_{n:02}.s2lv').encode(),s[14],s[15],view,160,-1]
                fn=lib.s2_render_file_background_repeat if view>240 else lib.s2_render_file
                if view>240:args+=[0]
                assert fn(*args,expected,len(expected))==0
                raw=bytes(expected);bg=bytearray(bytes((24,24,24,255))*(width*160))
                for y in range(160):
                    for x in range(view):
                        i=(y*view+x)*4;at=(y*width+offset+x)*4
                        if raw[i+3]:bg[at:at+4]=bytes((raw[i+2],raw[i+1],raw[i],255))
                assert actual==bg,(n,width,dx,dy);comparisons+=1
        assert lib.s2_campaign_select_scene(h,n)==0;assert lib.s2_campaign_option(h,2,1)==0
        for _ in range(24):assert lib.s2_campaign_step(h,4)==0
        raw=render(426);cards.append((f'{row["thumbnail_order"]+1:02d} / scene {n:02d}',Image.frombytes('RGBA',(426,160),raw,'raw','BGRA').convert('RGB')))
    assert lib.s2_campaign_mode(h,1)==0
    for bank in range(16):
        assert info()[7]==bank
        n=info()[9]
        for animation in range(n):
            assert info()[8]==animation
            for ticks in [0,4,4,4]:assert lib.s2_campaign_step(h,ticks)==0
            for zoom in [1,2,4]:assert lib.s2_campaign_option(h,3,zoom)==0;render(426);gallery+=1
            lib.s2_campaign_animation(h,1)
        lib.s2_campaign_bank(h,1)
    lib.s2_campaign_option(h,0,1);before=save();lib.s2_campaign_step(h,4);assert save()==before
    lib.s2_campaign_option(h,0,0);lib.s2_campaign_step(h,4);assert save()[6]==4
    saved=save();lib.s2_campaign_select_scene(h,0);assert lib.s2_campaign_restore(h,(I*12)(*saved))==0;assert save()==saved
    for at,bad in [(0,30),(1,3),(2,16),(3,600),(6,-1),(7,2),(10,0),(11,1)]:
        state=saved.copy();state[at]=bad;assert lib.s2_campaign_restore(h,(I*12)(*state))==-1;assert save()==saved
    assert lib.s2_campaign_select_scene(h,30)==-1 and save()==saved
    assert lib.s2_campaign_pan(h,2147483647,0)==-1 and save()==saved
    assert lib.s2_campaign_step(h,5)==-1 and save()==saved
    # Opening and deleting a second browser cannot reset the first owner's state.
    other=lib.s2_campaign_create(str(assets).encode());assert other;lib.s2_campaign_destroy(other);assert save()==saved
    with tempfile.TemporaryDirectory()as td:
        dest=Path(td);(dest/'scenes').mkdir();shutil.copyfile(assets/'scenes/scene_00.s2lv',dest/'scenes/scene_00.s2lv')
        data=(assets/'catalog.s2cp').read_bytes()
        for invalid in [b'',data[:100],data[:-1],data+b'0']:
            (dest/'catalog.s2cp').write_bytes(invalid);assert not lib.s2_campaign_create(str(dest).encode())
finally:lib.s2_campaign_destroy(h)
sheet=Image.new('RGB',(426*3,184*10),(18,25,20));draw=ImageDraw.Draw(sheet)
for index,(label,im)in enumerate(cards):x=index%3*426;y=index//3*184;sheet.paste(im,(x,y));draw.text((x+6,y+164),label,fill='white')
sheet.save(ROOT/'previews/campaign_all_worlds.png')
report=dict(scenes=30,cached_background_comparisons=comparisons,gallery_animation_scale_renders=gallery,sprite_banks=16,animations=387,placements=meta['total_placements'],bound_placements=meta['bound_placements'],state_restore=True,invalid_state_atomic=True,separate_owners=True,malformed_catalog_rejected=True,mismatches=0,device_tested=False,scope='Native graphics and UI-independent resource owner. These tests do not certify AI, physics, chapter completion or character abilities on preview maps.')
(ROOT/'docs/campaign_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
