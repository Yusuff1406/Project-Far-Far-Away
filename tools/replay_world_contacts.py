#!/usr/bin/env python3
"""Native sweep discovers contacts among five real scene-0 type-18 records and a probe."""
import ctypes,csv,json
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);BND=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p);PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p);EX=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None;rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int32,IP];rinit.restype=None;step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];contact=lib.s2_generic_contact_pair;contact.argtypes=[IP,IP,IP,IP,FC,ctypes.c_void_p,IP];envelope=lib.s2_actor_envelope_q8;envelope.argtypes=[IP,FC,ctypes.c_void_p,IP];add=lib.s2_sweep_add;add.argtypes=[ctypes.c_uint32,IP,IP,IP];frame=lib.s2_sweep_frame;frame.argtypes=[IP,ctypes.c_int,BND,PAIR,ctypes.c_void_p];nearest=lib.s2_world_nearest;nearest.argtypes=[IP,IP,ctypes.c_int,EX,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 recordSource=json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'];records=[x for x in recordSource if x['type']==18];source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18);actors={};envs={};effects=[];tick=0;owner=0;probeID=100000;callbacks=[];activations=[];errors=[]
 @REG
 def registry(enabled,ctx):errors.append('unexpected broadcast registration')
 @RC
 def random_value(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):effects.append([tick,owner,kind,address,scale]);return 0 if kind==11 else -4
 for record in records:
  ident=record['instance_id'];s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(*[x*256 for x in record['anchor_px']]),record['flags_byte'],source['initial_animation'],0,res.fetch,None,s)==0;start(source['script'],v);rinit(record['word8_actor_tag'],r);actors[ident]=(s,v,r)
 probe=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();v[2]=-1;r=(ctypes.c_int32*72)();rinit(0,r);assert init((ctypes.c_int32*2)(1360*256,296*256),0,0x0834f274,0,res.fetch,None,probe)==0;probe[40]=0;probe[41]=1;probe[42]=8;actors[probeID]=(probe,v,r)
 endpoints=(ctypes.c_int32*384)();count=(ctypes.c_int32*1)()
 @BND
 def get_bounds(ident,out,ctx):
  if ident not in envs:return 0
  for i,x in enumerate(envs[ident]):out[i]=x
  return 1
 @PAIR
 def pair(a,b,ctx):
  sa,va,ra=actors[a];sb,vb,rb=actors[b];diag=(ctypes.c_int32*4)();code=contact(sa,sb,vb,rb,res.fetch,None,diag);callbacks.append([tick,a,b,*diag]);
  if code:errors.append([tick,a,b,code])
  if diag[1]:activations.append([tick,a,b,sa[43]])
 @EX
 def exclude(ident,ctx):return 0
 for ident,(s,vm,r) in actors.items():
  b=(ctypes.c_int32*4)();assert envelope(s,res.fetch,None,b)==0;envs[ident]=list(b);assert add(ident,b,endpoints,count)==1
 frames=[];trace=[];totalCallbacks=0
 for tick in range(1,481):
  phase=tick%160;x=1360+(phase if phase<=80 else 160-phase)*3;probe[0]=(x-3)*256;probe[1]=297*256;probe[18]=phase>80
  for ident,(s,vm,r) in actors.items():
   b=(ctypes.c_int32*4)();assert envelope(s,res.fetch,None,b)==0;envs[ident]=list(b)
  n=frame(endpoints,count[0],get_bounds,pair,None);assert n>=0 and not errors;totalCallbacks+=n
  rows=[z for ident,(s,_,_) in actors.items() if ident!=probeID for z in [ident,s[0],s[1]]];closest=(ctypes.c_uint32*1)();assert nearest((ctypes.c_int32*2)(probe[0]>>8,probe[1]>>8),(ctypes.c_int32*len(rows))(*rows),len(records),exclude,None,closest)==0
  for owner,(s,vm,r) in actors.items():assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,tick,3200*256,400*256,res.fetch,random_value,None,4096,r,registry,sink)==0
  trace.append([tick,x,n,closest[0],len(activations),len(effects)])
  if tick%8:continue
  width=320;height=160;cx=1350;cy=170;buf=(ctypes.c_uint8*(width*height*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),cx,cy,width,height,-1,buf,len(buf))==0;im=Image.new('RGBA',(width,height),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)))
  for ident,(s,vm,r) in actors.items():
   item=res.lookup[s[47]];point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point)
   if not(cx-64<=point[0]//256<=cx+width+64):continue
   assert sprite(str(ROOT/'sprites'/item['bank']/'bank.s2sp').encode(),item['index'],s[22],s[18],width,height,point[0]//256-cx,point[1]//256-cy,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)))
  d=ImageDraw.Draw(im);d.rectangle((0,0,width-1,38),fill='black');d.text((4,2),'WORLD SWEEP / REAL SCENE OBJECT POSITIONS',fill='white');d.text((4,14),f'{tick:03d} PAIR CALLS {n} NEAREST {closest[0]}',fill=(196,231,152));d.text((4,26),f'SOURCE PATH FIXTURE / REACTIONS {len(activations)}',fill=(230,211,147));frames.append(im.convert('RGB'))
 assert totalCallbacks>0 and len(effects)==len(activations)>0 and all(x[2]==37 for x in activations);assert not errors
 frames[0].save(ROOT/'previews/native_world_contacts.gif',save_all=True,append_images=frames[1:],duration=133,loop=0);frames[10].resize((960,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_world_contacts.png')
 with (ROOT/'docs/native_world_contacts.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','source_x_px','broadphase_calls','nearest_type18_instance','activation_count','effect_count']);w.writerows(trace)
 result={'ticks':480,'actors':len(actors),'real_scene_objects':[{'instance_id':x['instance_id'],'type':x['type'],'anchor_px':x['anchor_px'],'flags':x['flags_byte']} for x in records],'gif_frames':len(frames),'broadphase_callbacks':totalCallbacks,'activations':len(activations),'activated_instance_ids':sorted({x[2] for x in activations}),'sound_requests':len(effects),'scope':'Five original scene-0 type-18 positions/flags/scripts plus a moving generic source fixture. Native envelopes, endpoint refresh/sort/sweep, nearest lookup, contact/activation and target VM update. Fixed selected object lifetime/update scheduling; other scene records, world category activation/destruction, Shrek subclass behavior, actual sound and Android execution are excluded.'};(ROOT/'docs/native_world_contacts_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
