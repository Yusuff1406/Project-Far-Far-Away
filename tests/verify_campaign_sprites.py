#!/usr/bin/env python3
"""Every source animation frame, plus source X/Y mirrors, independent ROM decoder."""
import ctypes as C,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom
from extract_sprites import bank,roots,frame_image
rom=Rom(sys.argv[1]);lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));P=C.c_void_p;I=C.c_int32
lib.s2_sprite_bank_create.argtypes=[C.c_char_p];lib.s2_sprite_bank_create.restype=P
lib.s2_sprite_bank_destroy.argtypes=[P];lib.s2_sprite_composite_transform.argtypes=[P,I,I,I,I,I,I,I,P,C.c_size_t];lib.s2_sprite_bank_info.argtypes=[P,I,C.POINTER(I)]
cases=frames=animations=0
for root in roots(rom):
    source=bank(rom,root);path=ROOT/'android/app/src/main/assets/campaign/sprites'/source['name']/'bank.s2sp';assert path.read_bytes()==(ROOT/'sprites'/source['name']/'bank.s2sp').read_bytes()
    handle=lib.s2_sprite_bank_create(str(path).encode());assert handle
    try:
        for anim in source['animations']:
            metadata=(I*8)();assert lib.s2_sprite_bank_info(handle,anim['index'],metadata)==0
            assert list(metadata)==[source['animation_count'],anim['sequence_count'],anim['rate_byte'],anim['flags'],*anim['bounds']]
            animations+=1
            for index in range(anim['sequence_count']):
                source_image=frame_image(source['frames'][anim['frame_indices'][index]],anim['palette'],(256,256),(128,128));frames+=1
                mirrors=range(4)if index in[0,anim['sequence_count']-1]else[0]
                for mirror in mirrors:
                    out=(C.c_uint32*(256*256))();assert lib.s2_sprite_composite_transform(handle,anim['index'],index,mirror,256,256,128,128,out,len(out))==0
                    expected=source_image
                    if mirror&1:expected=expected.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    if mirror&2:expected=expected.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    assert bytes(out)==expected.tobytes('raw','BGRA'),(source['name'],anim['index'],index,mirror)
                    cases+=1
    finally:lib.s2_sprite_bank_destroy(handle)
report=dict(banks=16,animations=animations,all_sequence_frames=frames,comparisons=cases,pixels_compared=cases*256*256,source_mirror_bits=2,mismatches=0,device_tested=False)
(ROOT/'docs/campaign_sprite_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
