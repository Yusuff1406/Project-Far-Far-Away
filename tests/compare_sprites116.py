#!/usr/bin/env python3
"""Compare optimized sprites with a shared library compiled from v1.0.5."""
import argparse,ctypes as C,json,random,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    lib=C.CDLL(str(path.resolve()))
    lib.s2_sprite_bank_create.argtypes=[C.c_char_p];lib.s2_sprite_bank_create.restype=C.c_void_p
    lib.s2_sprite_bank_destroy.argtypes=[C.c_void_p]
    lib.s2_sprite_bank_info.argtypes=[C.c_void_p,C.c_int,C.c_void_p]
    lib.s2_sprite_composite_transform.argtypes=[C.c_void_p]+[C.c_int]*7+[C.c_void_p,C.c_size_t]
    lib.s2_sprite_composite_bank_palette.argtypes=[C.c_void_p]+[C.c_int]*7+[C.c_void_p,C.c_size_t,C.c_int]
    return lib
def packed_bytes(path):
    b=path.read_bytes();na,nf=struct.unpack_from('<II',b,8);off=16
    for _ in range(na):off+=44+2*b[off+1]
    size=0
    for _ in range(nf):
        count=struct.unpack_from('<I',b,off+8)[0];off+=12
        for _ in range(count):
            n=struct.unpack_from('<I',b,off+8)[0];size+=n;off+=12+n
    assert off==len(b)
    return size
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,default=ROOT/'native/build/sprites116.so');a=p.parse_args()
    old,new=load(a.baseline),load(a.candidate);rng=random.Random(116);cases=saved=0
    banks=sorted((ROOT/'android/app/src/main/assets').rglob('*.s2sp'))
    assert banks
    for path in banks:
        saved+=packed_bytes(path);h0=old.s2_sprite_bank_create(str(path).encode());h1=new.s2_sprite_bank_create(str(path).encode());assert h0 and h1
        try:
            row=(C.c_int32*8)();assert old.s2_sprite_bank_info(h0,0,row)==0
            for animation in range(row[0]):
                assert old.s2_sprite_bank_info(h0,animation,row)==0
                for seq in sorted({0,row[1]//2,row[1]-1}):
                    for mirror in range(4):
                        w,h=240,160
                        x,y=rng.choice([(120,100),(-8,4),(248,168),(-2147483648,0),(2147483647,0),(0,-2147483648)])
                        a0=(C.c_uint32*(w*h))();a1=(C.c_uint32*(w*h))()
                        # A nonzero background catches transparency and clipping changes.
                        C.memset(a0,0x37,C.sizeof(a0));C.memset(a1,0x37,C.sizeof(a1))
                        assert old.s2_sprite_composite_transform(h0,animation,seq,mirror,w,h,x,y,a0,w*h)==0
                        assert new.s2_sprite_composite_transform(h1,animation,seq,mirror,w,h,x,y,a1,w*h)==0
                        assert bytes(a0)==bytes(a1),(path,animation,seq,mirror,x,y)
                        cases+=1
                    for flip in (0,1):
                        x,y=rng.choice([(120,100),(-8,4),(248,168)])
                        a0=(C.c_uint32*(w*h))();a1=(C.c_uint32*(w*h))()
                        palette=rng.choice([-1,0,animation])
                        assert old.s2_sprite_composite_bank_palette(h0,animation,seq,flip,w,h,x,y,a0,w*h,palette)==0
                        assert new.s2_sprite_composite_bank_palette(h1,animation,seq,flip,w,h,x,y,a1,w*h,palette)==0
                        assert bytes(a0)==bytes(a1),(path,animation,seq,flip,palette)
                        cases+=1
        finally:
            old.s2_sprite_bank_destroy(h0);new.s2_sprite_bank_destroy(h1)
    report={'sprite_banks':len(banks),'render_comparisons':cases,'mismatches':0,'packed_pixel_bytes_not_retained_all_banks':saved,'scope':'Source-level cached sprite comparison on host, selected first/middle/last sequence frames, all mirror modes, palette overrides and extreme anchors. Total removed buffers is summed across packaged banks, not a measured whole-game RSS or ARMv7 FPS gain.'}
    (ROOT/'docs/sprite_memory116_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
