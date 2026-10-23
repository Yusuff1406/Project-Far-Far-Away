#!/usr/bin/env python3
"""Extract original multipart OBJ graphics, sequence indices and per-animation palettes."""
import argparse,hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from extract import Rom,ROM_BASE,unpack
SIZES=[(8,8),(16,16),(32,32),(64,64),(16,8),(32,8),(32,16),(64,32),(8,16),(8,32),(16,32),(32,64)]
IDENTIFIED={0x34f248:'shrek_ogre',0x32fed0:'donkey',0x344bc0:'puss_in_boots',0x355b60:'shrek_human'}
def roots(rom):
 b=rom.data;found=[]
 for o in range(0,len(b)-20,4):
  a,p,na,nf,e=unpack('<5I',b,o)
  if a==ROM_BASE+o and 0<na<600 and 0<nf<10000 and p==a+20+na*24:found.append(o)
 return found

def bank(rom,root):
 b=rom.data;parent,fp,na,nf,unknown=unpack('<5I',b,root);frames=[];animations=[]
 for n in range(nf):
  off=rom.offset(fp)+n*44;w=unpack('<11I',b,off);pp,gp=w[:2];x,y,bw,bh,extra=unpack('<hhBBH',b,off+8);count=w[4]
  if count>100:raise ValueError('Invalid piece count')
  pieces=[];pos=rom.offset(gp)
  for k in range(count):
   po=rom.offset(pp)+k*8;px,py,shape=unpack('<hhI',b,po)
   if shape>=12:raise ValueError('Invalid OBJ shape')
   sw,sh=SIZES[shape];size=sw*sh//2;payload=b[pos:pos+size]
   if len(payload)!=size:raise ValueError('Truncated piece')
   pieces.append({'x':px,'y':py,'shape':shape,'width':sw,'height':sh,'geometry_offset':po,'graphics_offset':pos,'graphics_bytes':size,'sha256':hashlib.sha256(payload).hexdigest(),'data':payload});pos+=size
  frames.append({'index':n,'record_offset':off,'bounds':[x,y,bw,bh],'bounds_reserved':extra,'pieces':pieces,'auxiliary_pointers_unresolved':list(w[5:])})
 for n in range(na):
  off=root+20+n*24;parent,seq,pal,x,y,w,h,extra,rate,count,flags,reserved=unpack('<IIIhhBBH4B',b,off)
  if parent!=root+ROM_BASE or not count:raise ValueError('Invalid animation')
  indices=list(unpack('<'+'H'*count,b,rom.offset(seq)))
  if any(i>=nf for i in indices):raise ValueError('Frame index out of range')
  palette=b[rom.offset(pal):rom.offset(pal)+32]
  animations.append({'index':n,'record_offset':off,'sequence_offset':rom.offset(seq),'palette_offset':rom.offset(pal),'bounds':[x,y,w,h],'bounds_reserved':extra,'rate_byte':rate,'ticks_per_frame':rate+1,'sequence_count':count,'flags':flags,'loop':bool(flags&1),'reserved_byte':reserved,'frame_indices':indices,'palette':palette})
 return {'root_offset':root,'name':IDENTIFIED.get(root,f'bank_{root:06x}'),'animation_count':na,'frame_count':nf,'header_word4_unresolved':unknown,'animations':animations,'frames':frames}

def frame_image(frame,palette,canvas=(160,160),anchor=(80,100)):
 colors=[tuple(((c>>s)&31)*255//31 for s in (0,5,10)) for c in struct.unpack('<16H',palette)]
 image=Image.new('RGBA',canvas)
 for piece in frame['pieces']:
  sw,sh=piece['width'],piece['height'];data=piece['data'];tileimage=Image.new('RGBA',(sw,sh));pixels=tileimage.load()
  for y in range(sh):
   for x in range(sw):
    offset=((y//8)*(sw//8)+x//8)*32+(y%8)*4+(x%8)//2;c=(data[offset]>>((x%2)*4))&15
    pixels[x,y]=(*colors[c],255 if c else 0)
  image.alpha_composite(tileimage,(anchor[0]+piece['x'],anchor[1]+piece['y']))
 return image

def write_binary(path,data):
 with path.open('wb') as f:
  f.write(struct.pack('<4s3I',b'S2SP',1,data['animation_count'],data['frame_count']))
  for a in data['animations']:
   f.write(struct.pack('<4BhhBBH',a['rate_byte'],a['sequence_count'],a['flags'],a['reserved_byte'],*a['bounds'],a['bounds_reserved']));f.write(a['palette']);f.write(struct.pack('<'+'H'*len(a['frame_indices']),*a['frame_indices']))
  for frame in data['frames']:
   f.write(struct.pack('<hhBBHI',*frame['bounds'],frame['bounds_reserved'],len(frame['pieces'])))
   for p in frame['pieces']:f.write(struct.pack('<hhII',p['x'],p['y'],p['shape'],len(p['data'])));f.write(p['data'])

def public_manifest(data):
 result={k:v for k,v in data.items() if k not in ['animations','frames']}
 result['animations']=[{k:v for k,v in a.items() if k!='palette'} for a in data['animations']]
 result['frames']=[{**{k:v for k,v in f.items() if k!='pieces'},'pieces':[{k:v for k,v in p.items() if k!='data'} for p in f['pieces']]} for f in data['frames']]
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'sprites'));args=ap.parse_args();r=Rom(args.rom);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);manifest={'rom_sha256':r.sha256,'banks':[]};cards=[]
 for root in roots(r):
  d=bank(r,root);folder=out/d['name'];folder.mkdir(exist_ok=True);write_binary(folder/'bank.s2sp',d);m=public_manifest(d);(folder/'bank.json').write_text(json.dumps(m,indent=2)+'\n');manifest['banks'].append(m)
  cols=8;rows=(d['animation_count']+cols-1)//cols;sheet=Image.new('RGB',(cols*160,rows*176),(32,34,39));draw=ImageDraw.Draw(sheet)
  for a in d['animations']:
   im=frame_image(d['frames'][a['frame_indices'][0]],a['palette']);x=a['index']%cols*160;y=a['index']//cols*176;sheet.paste(im,(x,y),im);draw.text((x+5,y+158),f"A{a['index']:02d} {a['sequence_count']}f {a['ticks_per_frame']}t",fill='white')
   if root in IDENTIFIED:
    frames=[]
    colors=[tuple(((c>>s)&31)*255//31 for s in (0,5,10)) for c in struct.unpack('<16H',a['palette'])]
    lookup={rgb:k for k,rgb in enumerate(colors) if k!=0}
    flat=[c for rgb in colors for c in rgb]+[0]*(768-48)
    for k in a['frame_indices']:
     rgba=frame_image(d['frames'][k],a['palette'],(112,112),(56,65));indexed=Image.new('P',rgba.size);indexed.putpalette(flat)
     indexed.putdata([lookup[tuple(pixel[:3])] if pixel[3] else 0 for pixel in rgba.getdata()]);frames.append(indexed)
    # Preview uses one tick = 1/60 s. Original timing byte+1 is code-verified;
    # original scheduler frequency is not yet measured.
    frames[0].save(folder/f"animation_{a['index']:02d}.gif",save_all=True,append_images=frames[1:],duration=round(a['ticks_per_frame']*1000/60),disposal=2,transparency=0,optimize=False,**({'loop':0} if a['loop'] else {}))
  sheet.save(folder/'animation_overview.png');cards.append((d['name'],frame_image(d['frames'][d['animations'][0]['frame_indices'][0]],d['animations'][0]['palette'])))
 grid=Image.new('RGB',(800,704),(32,34,39));draw=ImageDraw.Draw(grid)
 for i,(name,im) in enumerate(cards):
  x=i%4*200;y=i//4*176;grid.paste(im,(x+20,y),im);draw.text((x+5,y+158),name,fill='white')
 grid.save(out/'banks_overview.png');(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'banks':len(manifest['banks']),'animations':sum(x['animation_count'] for x in manifest['banks']),'frame_records':sum(x['frame_count'] for x in manifest['banks']),'parts':sum(len(f['pieces']) for x in manifest['banks'] for f in x['frames'])},indent=2))
if __name__=='__main__':main()
