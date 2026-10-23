#!/usr/bin/env python3
"""ROM sprite/scene data with native VM-driven actor; control script is a fixture."""
import ctypes,csv,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];IP=ctypes.POINTER(ctypes.c_int32);FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_int,ctypes.c_void_p);RC=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p)
class Resources:
 def __init__(self):
  package=(ROOT/'objects/generic_script_resources.s2rs').read_bytes();assert package[:4]==b'S2RS';version,base,size=struct.unpack_from('<3I',package,4);assert version==1 and len(package)==16+size;self.blocks={base:package[16:]};self.animations=json.loads((ROOT/'objects/generic_animation_headers.json').read_text())['animations'];self.lookup={x['address']:x for x in self.animations}
  self.blocks.update({x['address']:bytes.fromhex(x['header_hex']) for x in self.animations})
  contacts=ROOT/'objects/sprite_contact_resources.json'
  if contacts.exists():self.blocks.update({int(addr):bytes.fromhex(raw) for addr,raw in json.loads(contacts.read_text())['blocks'].items()})
  @FC
  def fetch(addr,out,n,context):
   for base,raw in self.blocks.items():
    off=addr-base
    if 0<=off<=len(raw)-n*4:
     for i,v in enumerate(struct.unpack_from('<'+'i'*n,raw,off)):out[i]=v
     return 1
   return 0
  self.fetch=fetch
 def put(self,address,values):self.blocks[address]=struct.pack('<'+'i'*len(values),*values)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];step=lib.s2_generic_runtime_step;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 @RC
 def random_value(ctx):return 37
 binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['39'];animations={x['index']:x['address'] for x in res.animations if x['bank']==binding['bank']};s=(ctypes.c_int32*80)();vm=(ctypes.c_int32*64)();assert init((ctypes.c_int32*2)(120*256,310*256),0,binding['animation'],0,res.fetch,None,s)==0
 for p,data in [(0x02007600,[0,49,1792]),(0x02007610,[-900,49,1792]),(0x02007620,[256,0,256]),(0x02007630,[0,0,0]),(0x02007700,[8,64,0,2,1])]:res.put(p,data)
 program=0x02007800;nested=0x02007a00;commands=[[8,30,1],[8,22,0x02007600],[5,10,0x02007700],[8,4,animations[32]],[8,22,0x02007610],[5,8,45],[8,0,1],[8,21,0x02007620],[5,8,50],[8,0,0],[8,21,0x02007630],[5,2,nested],[5,6,0]];sub=[[8,5,animations[0]],[5,8,20],[8,45,0],[5,6,0]];res.put(program,[v for cmd in commands for v in cmd]);res.put(nested,[v for cmd in sub for v in cmd]);start(program,vm)
 frames=[];trace=[]
 for tick in range(1,241):
  assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,tick,3200*256,400*256,res.fetch,random_value,None,4096)==0
  item=res.lookup[s[47]];trace.append([tick,*s[:2],s[5],s[11],item['index'],s[22],s[18],s[68],vm[2],vm[0]])
  if tick%4:continue
  buf=(ctypes.c_uint8*(240*160*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,230,240,160,-1,buf,len(buf))==0;im=Image.new('RGBA',(240,160),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)));point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point);assert sprite(str(ROOT/'sprites'/item['bank']/'bank.s2sp').encode(),item['index'],s[22],s[18],240,160,point[0]//256,point[1]//256-230,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(240,160),bytes(buf)));draw=ImageDraw.Draw(im);draw.rectangle((0,0,239,25),fill=(0,0,0,255));draw.text((4,2),'NATIVE ACTOR / TEST SCRIPT',fill='white');draw.text((4,14),f'TICK {tick:03d}  ANIM {item["index"]:02d}  VM {vm[2]}',fill=(196,231,152));frames.append(im.convert('RGB'))
 frames[0].save(ROOT/'previews/native_scripted_actor.gif',save_all=True,append_images=frames[1:],duration=67,loop=0);frames[10].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_scripted_actor.png')
 with (ROOT/'docs/native_scripted_actor.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','x_q8','y_q8','vx_q8','vy_q8','animation_index','sequence_index','flip_x','floor_contacts','vm_depth','wait_counter']);w.writerows(trace)
 assert vm[2]==-1;assert len({x[5] for x in trace})==2;assert any(x[8] for x in trace)
 # Real startup script of type 39 now reaches completion through the handler.
 source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==39);actual=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();assert init((ctypes.c_int32*2)(120*256,310*256),0,binding['animation'],0,res.fetch,None,actual)==0;start(source['script'],v);assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),actual,v,1,3200*256,400*256,res.fetch,random_value,None,4096)==0;assert v[2]==-1 and list(actual[41:44])==[1,40,0]
 result={'ticks':240,'gif_frames':len(frames),'script_completed':True,'real_type39_startup_completed':True,'scope':'ROM artwork, scene and collision data; synthetic control script demonstrates linked VM/motion/contact/animation behavior. Type 39 original startup additionally runs natively. No full original object AI/game loop or Android execution.'};(ROOT/'docs/native_scripted_actor_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
