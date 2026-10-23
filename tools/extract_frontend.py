#!/usr/bin/env python3
"""Original FLC title/books, fonts, menu labels and campaign thumbnail order.
Only asset decoding occurs here; the native frontend never executes ROM code.
"""
import argparse,io,struct,json,hashlib
from pathlib import Path
from PIL import Image
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
BACKGROUNDS=[(0,0x0826dfb8),(1,0x08234ad8),(2,0x08210788),(3,0x08216848),(4,0x0821c36c),(5,0x08221de8),(6,0x08227738),(7,0x0822d654),(8,0x0823efbc),(9,0x08244514),(10,0x0824d47c),(11,0x08256390),(12,0x0825fab8),(13,0x08294bbc),(14,0x0829a57c),(15,0x082a1110),(16,0x082a7360),(17,0x08277058),(18,0x0827e568)]
LABELS=[('start',0x45440),('credits',0x45450),('slots',0x45464),('erase_slots',0x45478),('erase_confirm',0x4548c),('books',0x454a0),('chapter',0x454cc),('game',0x454dc),('back',0x454e8),('resume',0x454fc),('quit_level',0x45508),('quit_game',0x45518),('quit',0x45528),('sleep',0x45534),('new_game',0x45540),('erase',0x45560),('done',0x4556c),('cancel',0x45578),('quit_level_confirm',0x45584),('quit_game_confirm',0x45594),('sleep_confirm',0x455a4)]
POST_STORIES=[[(0x082ad194,0x080453d8),(0x082b33e0,0x080453dc),(0x082b8ac8,0x080453e0),(0x082bf238,0x080453e4)],[(0x082c5008,0x080453e8),(0x082cb93c,0x080453ec),(0x082cf9e0,0x080453f0)],[(0x082d69f0,0x080453f4),(0x082db878,0x080453f8),(0x082dfdb0,0x080453fc),(0x082e4cac,0x08045400)],[(0x082e85ec,0x08045404),(0x082edab8,0x08045408),(0x082f1318,0x0804540c)],[(0x082f57dc,0x08045410),(0x082fb600,0x08045414)],[(0x08300498,0x08045418),(0x08303350,0x0804541c),(0x083064f8,0x08045420),(0x0830a918,0x08045424)]]
BACKGROUNDS += [(19+i,a) for i,(a,_) in enumerate([pair for group in POST_STORIES for pair in group])]
LABELS += [(f'book_{i}',off) for i,off in enumerate([0x4564c,0x45660,0x45678,0x4568c,0x456a0,0x456b4])]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);raw=r.data;catalog=json.loads((ROOT/'objects/campaign_catalog.json').read_text());credits=raw[0x49328:].split(b'\0')[0];labels=[]
 for key,off in LABELS:
  s=raw[off:].split(b'\0')[0];assert s and len(s)<80;(labels.append((key,s)))
 # Original introduction captions, double indirection used by19B0C.
 for i,ptr in enumerate([0x080453c8,0x080453cc,0x080453d0,0x080453d4]):
  for _ in range(2):ptr=struct.unpack_from('<I',raw,ptr-0x08000000)[0]
  labels.append((f'intro_{i}',raw[ptr-0x08000000:].split(b'\0')[0]))
 for group,panels in enumerate(POST_STORIES):
  for panel,(_,ptr) in enumerate(panels):
   for _ in range(2):ptr=struct.unpack_from('<I',raw,ptr-0x08000000)[0]
   labels.append((f'epilogue_{group}_{panel}',raw[ptr-0x08000000:].split(b'\0')[0]))
 out=bytearray(struct.pack('<4s6I',b'S2UI',2,len(BACKGROUNDS),2,len(labels),30,len(credits)));images=[]
 for imageId,address in BACKGROUNDS:
  data,meta=r.blob(address);im=Image.open(io.BytesIO(data));assert im.size==(240,160);period=max(1,struct.unpack_from('<I',data,16)[0]);out+=struct.pack('<5I',imageId,240,160,im.n_frames,period);checks=[]
  for i in range(im.n_frames):
   im.seek(i);assert im.mode=='P';palette=im.getpalette();palette=(palette+[0]*768)[:768]
   for c in range(256):out+=struct.pack('<I',0xff000000|(palette[c*3]<<16)|(palette[c*3+1]<<8)|palette[c*3+2])
   out+=im.tobytes();rgba=im.convert('RGBA');rgba.putalpha(255);checks.append(hashlib.sha256(rgba.tobytes('raw','BGRA')).hexdigest())
  images.append(dict(id=imageId,address=hex(address),frames=im.n_frames,period_ms=period,flc_sha256=hashlib.sha256(data).hexdigest(),pixel_sha256=checks));preview=ROOT/'previews'/f'frontend_asset_{imageId}.png';im.convert('RGB').resize((720,480),Image.Resampling.NEAREST).save(preview)
 for off in [0x30fbac,0x316a34]:
  stride,glyphs,w,h=struct.unpack_from('<4B',raw,off);count=stride*glyphs;out+=struct.pack('<4I',w,h,glyphs,count);out+=raw[off+8:off+520]
  for palette in range(3):
   for c in struct.unpack_from('<16H',raw,0x30f9ac+32*palette):out+=struct.pack('<I',0xff000000|((c&31)*255//31<<16)|(((c>>5)&31)*255//31<<8)|(((c>>10)&31)*255//31))
  out+=raw[off+520:off+520+count]
 for key,value in labels:
  k=key.encode();out+=struct.pack('<2I',len(k),len(value))+k+value
 for row in catalog['records']:out+=struct.pack('<3I',row['scene'],17+row['thumbnail_order'],int(row['bonus']))
 out+=credits;p=ROOT/'android/app/src/main/assets/frontend/menu.s2ui';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(out)
 report=dict(images=images,labels={k:v.decode('latin1')for k,v in labels},font_addresses=['0x0830FBAC','0x08316A34'],font_palette_addresses=['0x0830F9AC','0x0830F9CC','0x0830F9EC'],source_menu_definitions=['0x08049F88','0x0804A21C','0x0804A24C','0x0804A35C'],credits_address='0x08049328',catalog_scenes=[x['scene']for x in catalog['records']],bytes=len(out),sha256=hashlib.sha256(out).hexdigest(),rom_sha256=r.sha256,schema_version=2,frame_storage='indexed8 + per-frame256 ARGB palette',scope='Exact original decoded art and glyph bytes. Native menu navigation is adapted to touch and currently playable scenes; original save RAM is not emulated.')
 (ROOT/'docs/frontend_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(dict(images=len(images),frames=sum(x['frames']for x in images),bytes=len(out)))
if __name__=='__main__':main()
