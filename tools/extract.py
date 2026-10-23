#!/usr/bin/env python3
"""Verified scene resource extraction for Shrek 2 BSEE, SHA256 below."""
from pathlib import Path
import argparse, collections, hashlib, json, struct
ROM_BASE = 0x08000000
ROM_SHA256 = '2ec32cb8c69ff8bbe01b7039ee001105f92ee686b251d26060f9bdb6751f3b80'
SCENE_TABLE = 0x28d94
SCENE_COUNT = 30

def unpack(fmt, b, off):
    size=struct.calcsize(fmt)
    if off<0 or off+size>len(b): raise ValueError(f'Out-of-bounds read at {off:#x}')
    return struct.unpack_from(fmt,b,off)

class Rom:
    def __init__(self,path):
        self.data=Path(path).read_bytes()
        self.sha256=hashlib.sha256(self.data).hexdigest()
        if self.sha256!=ROM_SHA256: raise ValueError('Unsupported ROM: SHA256 mismatch; do not reuse these offsets for another build')
        self.cache={}
    def offset(self,p):
        o=p-ROM_BASE
        if not 0<=o<len(self.data): raise ValueError(f'Invalid ROM pointer {p:#x}')
        return o
    def blob(self,p):
        if p in self.cache: return self.cache[p]
        o=self.offset(p); h=unpack('<I',self.data,o)[0]; pos=o+4
        if h&255==0x10:
            size=h>>8; out=bytearray()
            if not 0<size<=4*1024*1024: raise ValueError('Invalid LZ10 size')
            while len(out)<size:
                flags=unpack('<B',self.data,pos)[0];pos+=1
                for bit in range(8):
                    if len(out)==size:break
                    if flags&(128>>bit):
                        a,c=unpack('<BB',self.data,pos);pos+=2
                        dist=((a&15)<<8|c)+1; count=(a>>4)+3
                        if dist>len(out) or len(out)+count>size: raise ValueError('Invalid LZ10 back-reference')
                        for _ in range(count):out.append(out[-dist])
                    else:
                        out.append(unpack('<B',self.data,pos)[0]);pos+=1
            codec='lz10'
        else:
            size=h
            if not 0<size<=4*1024*1024 or pos+size>len(self.data):raise ValueError('Invalid raw blob size')
            out=self.data[pos:pos+size];pos+=size;codec='raw-u32-size'
        result=(bytes(out),{'rom_offset':o,'codec':codec,'stored_bytes':pos-o,'decoded_bytes':size,'decoded_sha256':hashlib.sha256(out).hexdigest()})
        self.cache[p]=result
        return result
    def column_map(self,p):
        b=self.data;o=self.offset(p);width,height=unpack('<HH',b,o)
        if not 0<width<=1024 or not 0<height<=1024:raise ValueError('Invalid column-map dimensions')
        base=o+4+4*width;rows=[0]*(width*height);ends=[];commands=collections.Counter()
        for x in range(width):
            pos=base+unpack('<I',b,o+4+4*x)[0]*2;col=[]
            while len(col)<height:
                cmd=unpack('<H',b,pos)[0];pos+=2;kind=cmd>>14;count=cmd&0x3fff
                if count==0 or len(col)+count>height:raise ValueError('Invalid column run length')
                commands[kind]+=1
                if kind==2:
                    value=unpack('<H',b,pos)[0];pos+=2;col.extend([value]*count)
                elif kind==3:
                    col.extend(unpack('<'+'H'*count,b,pos));pos+=count*2
                else:raise ValueError(f'Unexpected command {cmd:#x}')
            for y,value in enumerate(col):rows[y*width+x]=value
            ends.append(pos)
        return width,height,rows,{'rom_offset':o,'stored_extent_bytes':max(ends)-o,'commands':dict(commands)}
    def scene(self,n):
        off=SCENE_TABLE+n*32;w=unpack('<8I',self.data,off)
        paloff=self.offset(w[0]);pal=self.data[paloff:paloff+512]
        geometry=unpack('<10I',self.data,self.offset(w[5]))
        gfxp=unpack('<2I',self.data,self.offset(w[7]));gfx=[self.blob(p) for p in gfxp]
        if len(gfx[0][0])%64 or len(gfx[1][0])%32:raise ValueError('Invalid graphics bank length')
        layers=[]
        for slot,lp in enumerate(w[1:5]):
            if not lp:continue
            desc=unpack('<6I',self.data,self.offset(lp));blocks,meta=self.blob(desc[0]);bw,bh,grid,mapmeta=self.column_map(desc[1])
            if len(blocks)%8:raise ValueError('Invalid 2x2 block pool')
            pool=unpack('<'+'H'*(len(blocks)//2),blocks,0)
            tw,th=bw*2,bh*2;entries=[0]*(tw*th);bank_counts=collections.Counter()
            for y in range(bh):
                for x in range(bw):
                    block=grid[y*bw+x]
                    if block>=len(blocks)//8:raise ValueError('Block index outside pool')
                    for k in range(4):
                        v=pool[block*4+k];bank=v>>14;idx=v&0xfff
                        if bank==3:raise ValueError('Unsupported bank selector 3')
                        limit=len(gfx[0][0])//64 if desc[5]&0x10000 else len(gfx[1][0])//32
                        if idx>=limit:raise ValueError(f'Tile index outside graphics bank: scene {n}, slot {slot}, {v:#x}')
                        entries[(y*2+k//2)*tw+x*2+k%2]=v;bank_counts[bank]+=1
            layers.append({'slot':slot,'descriptor_offset':self.offset(lp),'descriptor_words':list(desc),'priority_or_bg_index':desc[2],'scroll_x_q8':desc[3],'scroll_y_q8':desc[4],'format_flags':desc[5], 'bits_per_pixel':8 if desc[5]&0x10000 else 4,'tile_width':tw,'tile_height':th,'block_count':len(blocks)//8,'banks_used':dict(bank_counts),'block_pool':meta,'column_map':mapmeta,'entries':entries})
        objoff=self.offset(w[6]);ocount,op,aux1,aux2,aux3,aux4=unpack('<6I',self.data,objoff)
        ocount &= 65535
        # Exact fixed record width is independently visible from array boundaries: 8 bytes.
        oo=self.offset(op);objects=[]
        for k in range(ocount):
            v=unpack('<4H',self.data,oo+k*8)
            objects.append({'index':k,'rom_offset':oo+k*8,'raw_u16':list(v),'type_id':v[0],'anchor_x_px':v[1],'anchor_y_px':v[2],'parameter_index':v[3]})
        return {'id':n,'descriptor_offset':off,'descriptor_words':list(w),'geometry_words':list(geometry),'width_px':geometry[2],'height_px':geometry[3],'palette_offset':paloff,'palette_sha256':hashlib.sha256(pal).hexdigest(),'graphics_banks':[m for _,m in gfx],'objects_descriptor_offset':objoff,'object_count':ocount,'object_aux_pointers':[aux1,aux2,aux3,aux4],'objects':objects,'layers':layers},pal,[g for g,_ in gfx]

def write_scene(path,scene,pal,gfx):
    with path.open('wb') as f:
        f.write(struct.pack('<4s6I',b'S2LV',1,scene['width_px'],scene['height_px'],len(gfx[0]),len(gfx[1]),len(scene['layers'])))
        f.write(pal);f.write(gfx[0]);f.write(gfx[1])
        for layer in scene['layers']:
            f.write(struct.pack('<7I',layer['slot'],layer['priority_or_bg_index'],layer['scroll_x_q8'],layer['scroll_y_q8'],layer['format_flags'],layer['tile_width'],layer['tile_height']))
            f.write(struct.pack('<'+'H'*len(layer['entries']),*layer['entries']))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='extracted');args=ap.parse_args()
    rom=Rom(args.rom);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':1,'rom_sha256':rom.sha256,'rom_bytes':len(rom.data),'scene_table_offset':SCENE_TABLE,'scene_count':SCENE_COUNT,'scenes':[]}
    for n in range(SCENE_COUNT):
        scene,pal,gfx=rom.scene(n);folder=out/f'scene_{n:02d}';folder.mkdir(exist_ok=True)
        write_scene(folder/'scene.s2lv',scene,pal,gfx)
        (folder/'palette.bgr555').write_bytes(pal)
        for k,g in enumerate(gfx):(folder/f'tiles_bank{k}.bin').write_bytes(g)
        for layer in scene['layers']:
            data=struct.pack('<'+'H'*len(layer['entries']),*layer.pop('entries'))
            (folder/f"layer_{layer['slot']}.u16").write_bytes(data)
            layer['expanded_sha256']=hashlib.sha256(data).hexdigest()
        scene['scene_file_sha256']=hashlib.sha256((folder/'scene.s2lv').read_bytes()).hexdigest()
        (folder/'scene.json').write_text(json.dumps(scene,indent=2)+'\n')
        manifest['scenes'].append(scene)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'scenes':len(manifest['scenes']),'layers':sum(len(s['layers']) for s in manifest['scenes']),'objects':sum(s['object_count'] for s in manifest['scenes']),'unique_blobs':len(rom.cache)},indent=2))
if __name__=='__main__':main()
