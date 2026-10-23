#!/usr/bin/env python3
"""Original static collision trees referenced by the scene descriptor."""
import argparse,collections,hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from extract import Rom,unpack,ROM_BASE
COLORS={1:(255,89,105),2:(84,178,255),3:(93,255,128),4:(255,204,80),5:(204,111,255)}

def scene_collision(rom,n):
 desc=unpack('<8I',rom.data,0x28d94+n*32);root=desc[5];nodes=[];segments=[];visiting=set();seen={}
 def visit(p):
  if not p:return -1
  if p in visiting:raise ValueError('Collision tree cycle')
  if p in seen:return seen[p]
  visiting.add(p);off=rom.offset(p);w=unpack('<4i6I',rom.data,off);idx=len(nodes);seen[p]=idx
  if w[4]>2000:raise ValueError('Invalid segment count')
  node={'index':idx,'rom_offset':off,'bounds':list(w[:4]),'segment_start':len(segments),'segment_count':w[4],'children':[]};nodes.append(node)
  for k in range(w[4]):
   so=rom.offset(w[5])+k*24;v=unpack('<4i2I',rom.data,so)
   segments.append({'index':len(segments),'rom_offset':so,'endpoints':list(v[:4]),'type':v[4],'auxiliary_pointer':v[5]})
  node['children']=[visit(cp) for cp in w[6:]];visiting.remove(p);return idx
 visit(root)
 return {'scene_id':n,'root_offset':rom.offset(root),'node_count':len(nodes),'segment_count':len(segments),'types':dict(collections.Counter(s['type'] for s in segments)),'nodes':nodes,'segments':segments}

def write_binary(path,data):
 with path.open('wb') as f:
  f.write(struct.pack('<4s3I',b'S2CL',1,data['node_count'],data['segment_count']))
  for node in data['nodes']:f.write(struct.pack('<4i6i',*node['bounds'],node['segment_start'],node['segment_count'],*node['children']))
  for s in data['segments']:f.write(struct.pack('<4i3I',*s['endpoints'],s['type'],s['rom_offset'],s['auxiliary_pointer']))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--project',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();root=Path(a.project);r=Rom(a.rom);out=root/'collision';out.mkdir(exist_ok=True);manifest={'rom_sha256':r.sha256,'scenes':[]}
 for n in range(30):
  data=scene_collision(r,n);folder=out/f'scene_{n:02d}';folder.mkdir(exist_ok=True);write_binary(folder/'scene.s2cl',data)
  data['binary_sha256']=hashlib.sha256((folder/'scene.s2cl').read_bytes()).hexdigest();(folder/'collision.json').write_text(json.dumps(data,indent=2)+'\n');manifest['scenes'].append(data)
  if (root/f'previews/scene_{n:02d}_main_layer.png').is_file():
   image=Image.open(root/f'previews/scene_{n:02d}_main_layer.png').convert('RGBA');base=Image.new('RGBA',image.size,(24,24,24,255));base.alpha_composite(image);draw=ImageDraw.Draw(base)
   for s in data['segments']:draw.line(s['endpoints'],fill=COLORS.get(s['type'],(255,255,255)),width=2)
   if n!=0:base=base.crop((0,max(0,base.height-320),min(640,base.width),base.height))
   base.convert('RGB').save(folder/'geometry_overlay.png')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'scenes':30,'nodes':sum(s['node_count'] for s in manifest['scenes']),'segments':sum(s['segment_count'] for s in manifest['scenes']),'types':dict(collections.Counter(seg['type'] for s in manifest['scenes'] for seg in s['segments']))},indent=2))
if __name__=='__main__':main()
