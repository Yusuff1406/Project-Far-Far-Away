#!/usr/bin/env python3
"""Byte comparison of serialized frontend art/fonts with independently read ROM."""
import sys,struct,io,json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));from extract import Rom
r=Rom(sys.argv[1]);p=ROOT/'android/app/src/main/assets/frontend/menu.s2ui';b=p.read_bytes();meta=json.loads((ROOT/'docs/frontend_resources.json').read_text());assert hashlib.sha256(b).hexdigest()==meta['sha256'];magic,version,ni,nf,ns,nl,nc=struct.unpack_from('<4s6I',b);assert(magic,version,ni,nf,nl)==(b'S2UI',2,35,2,30);at=28;frames=0
for row in meta['images']:
 imageId,w,h,count,period=struct.unpack_from('<5I',b,at);at+=20;raw,_=r.blob(int(row['address'],16));im=Image.open(io.BytesIO(raw));assert(imageId,w,h,count,period)==(row['id'],240,160,im.n_frames,max(1,struct.unpack_from('<I',raw,16)[0]))
 for f in range(count):
  im.seek(f);rgba=im.convert('RGBA');rgba.putalpha(255);pixels=rgba.tobytes('raw','BGRA');palette=b[at:at+1024];indices=b[at+1024:at+39424];assert b''.join(palette[v*4:v*4+4]for v in indices)==pixels;at+=39424;frames+=1
for offset in [0x30fbac,0x316a34]:
 w,h,glyphs,size=struct.unpack_from('<4I',b,at);at+=16;assert(w,h,glyphs,size)==(r.data[offset+2],r.data[offset+3],r.data[offset+1],r.data[offset]*r.data[offset+1]);assert b[at:at+512]==r.data[offset+8:offset+520];at+=512
 for pal in range(3):
  expected=[]
  for v in struct.unpack_from('<16H',r.data,0x30f9ac+pal*32):expected.append(0xff000000|((v&31)*255//31<<16)|(((v>>5)&31)*255//31<<8)|(((v>>10)&31)*255//31))
  assert list(struct.unpack_from('<16I',b,at))==expected;at+=64
 assert b[at:at+size]==r.data[offset+520:offset+520+size];at+=size
for _ in range(ns):k,n=struct.unpack_from('<2I',b,at);at+=8;key=b[at:at+k].decode();at+=k;value=b[at:at+n];at+=n;assert value.decode('latin1')==meta['labels'][key]and value+b'\0'in r.data
catalog=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records']
for i,row in enumerate(catalog):assert struct.unpack_from('<3I',b,at)==(row['scene'],17+i,int(row['bonus']));at+=12
assert b[at:at+nc]==r.data[0x49328:].split(b'\0')[0]and at+nc==len(b)
report=dict(original_flc_frames=frames,original_fonts=nf,original_label_strings=ns,campaign_records=nl,original_title_frame_duration_ms=meta['images'][0]['period_ms'],mismatches=0,device_tested=False);(ROOT/'docs/frontend_resource_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
