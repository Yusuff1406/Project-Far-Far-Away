#!/usr/bin/env python3
"""Native locomotion plus Shrek falling-strip contacts against a positioned type-18 fixture."""
import ctypes,csv,json,struct
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);BND=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,IP,ctypes.c_void_p);PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p);EX=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None;rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int32,IP];rinit.restype=None;step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];contact=lib.s2_shrek_contact_pair;contact.argtypes=[IP,IP,ctypes.c_int32,ctypes.c_uint32,ctypes.c_int,IP,IP,IP,FC,ctypes.c_void_p,IP];envelope=lib.s2_actor_envelope_q8;envelope.argtypes=[IP,FC,ctypes.c_void_p,IP];add=lib.s2_sweep_add;add.argtypes=[ctypes.c_uint32,IP,IP,IP];frame=lib.s2_sweep_frame;frame.argtypes=[IP,ctypes.c_int,BND,PAIR,ctypes.c_void_p];nearest=lib.s2_world_nearest;nearest.argtypes=[IP,IP,ctypes.c_int,EX,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 recordSource=json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'];records=[dict(next(x for x in recordSource if x['type']==18))];records[0]['anchor_px']=[120,350];records[0]['flags_byte']=0;source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18);actors={};envs={};effects=[];tick=0;owner=0;probeID=100000;callbacks=[];activations=[];errors=[]
 @REG
 def registry(enabled,ctx):errors.append('unexpected broadcast registration')
 @RC
 def random_value(ctx):return 37
 @SINK
 def sink(kind,address,scale,ctx):effects.append([tick,owner,kind,address,scale]);return 0 if kind==11 else -4
 for record in records:
  ident=record['instance_id'];s=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();assert init((ctypes.c_int32*2)(*[x*256 for x in record['anchor_px']]),record['flags_byte'],source['initial_animation'],0,res.fetch,None,s)==0;start(source['script'],v);rinit(record['word8_actor_tag'],r);actors[ident]=(s,v,r)
 probe=(ctypes.c_int32*80)();v=(ctypes.c_int32*64)();v[2]=-1;r=(ctypes.c_int32*72)();rinit(0,r);assert init((ctypes.c_int32*2)(120*256,350*256),0,0x0834f274,0,res.fetch,None,probe)==0;probe[40]=0;probe[41]=0;probe[42]=0;actors[probeID]=(probe,v,r)
 player=(ctypes.c_int32*40)();lib.s2_prototype_init.argtypes=[IP];lib.s2_prototype_init(player);move=lib.s2_prototype_step;move.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,IP];extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();profile=lib.s2_shrek_reactions_init;profile.argtypes=[IP,IP,IP,ctypes.c_int,ctypes.c_int32];assert profile(probe,extra,status,4,0)==0;dy=0
 endpoints=(ctypes.c_int32*384)();count=(ctypes.c_int32*1)()
 @BND
 def get_bounds(ident,out,ctx):
  if ident not in envs:return 0
  for i,x in enumerate(envs[ident]):out[i]=x
  return 1
 @PAIR
 def pair(a,b,ctx):
  if a!=probeID:return
  sa,va,ra=actors[a];sb,vb,rb=actors[b];diag=(ctypes.c_int32*8)();code=contact(sa,extra,dy,b,3,sb,vb,rb,res.fetch,None,diag);callbacks.append([tick,a,b,*diag]);
  if code:errors.append([tick,a,b,code])
  if diag[7]:activations.append([tick,a,b,extra[6]])
 @EX
 def exclude(ident,ctx):return 0
 for ident,(s,vm,r) in actors.items():
  b=(ctypes.c_int32*4)();assert envelope(s,res.fetch,None,b)==0;envs[ident]=list(b);assert add(ident,b,endpoints,count)==1
 frames=[];trace=[];totalCallbacks=0
 for tick in range(1,361):
  buttons=1 if tick in [30,150,270] else 0;oldY=player[37];assert move(str(ROOT/'collision/scene_00/scene.s2cl').encode(),str(ROOT/'sprites/shrek_ogre/bank.s2sp').encode(),buttons,player)==0;dy=ctypes.c_int32(player[37]-oldY).value;probe[0:2]=player[0:2];probe[18]=player[18];probe[22]=player[22];probe[47]=0x0834f25c+24*player[19];a=res.lookup[probe[47]];bounds=struct.unpack_from('<hhBB',bytes.fromhex(a['header_hex']),12);probe[26:28]=bounds[:2];probe[30:32]=player[30:32];probe[72:76]=bounds;extra[0]=player[26];extra[2]=buttons;x=player[0]//256
  for ident,(s,vm,r) in actors.items():
   b=(ctypes.c_int32*4)();assert envelope(s,res.fetch,None,b)==0;envs[ident]=list(b)
  n=frame(endpoints,count[0],get_bounds,pair,None);assert n>=0 and not errors;totalCallbacks+=n
  rows=[z for ident,(s,_,_) in actors.items() if ident!=probeID for z in [ident,s[0],s[1]]];closest=(ctypes.c_uint32*1)();assert nearest((ctypes.c_int32*2)(probe[0]>>8,probe[1]>>8),(ctypes.c_int32*len(rows))(*rows),len(records),exclude,None,closest)==0
  for owner,(s,vm,r) in actors.items():
   if owner==probeID:continue
   assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,tick,3200*256,400*256,res.fetch,random_value,None,4096,r,registry,sink)==0
  trace.append([tick,x,n,closest[0],len(activations),len(effects)])
  if tick%8:continue
  width=240;height=160;cx=0;cy=240;buf=(ctypes.c_uint8*(width*height*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),cx,cy,width,height,-1,buf,len(buf))==0;im=Image.new('RGBA',(width,height),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)))
  for ident,(s,vm,r) in actors.items():
   item=res.lookup[s[47]];point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point)
   if not(cx-64<=point[0]//256<=cx+width+64):continue
   assert sprite(str(ROOT/'sprites'/item['bank']/'bank.s2sp').encode(),item['index'],s[22],s[18],width,height,point[0]//256-cx,point[1]//256-cy,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)))
  d=ImageDraw.Draw(im);d.rectangle((0,0,width-1,38),fill='black');d.text((4,2),'SHREK LOCOMOTION / FALLING FOOT CONTACT',fill='white');d.text((4,14),f'{tick:03d} PAIR CALLS {n} NEAREST {closest[0]}',fill=(196,231,152));d.text((4,26),f'ORIGINAL FOOT EVENT / HITS {len(activations)}',fill=(230,211,147));frames.append(im.convert('RGB'))
 assert totalCallbacks>0 and len(effects)==len(activations)>0 and all(x[2]==records[0]['instance_id'] for x in activations);assert not errors
 frames[0].save(ROOT/'previews/native_shrek_defaults.gif',save_all=True,append_images=frames[1:],duration=133,loop=0);frames[10].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_shrek_defaults.png')
 with (ROOT/'docs/native_shrek_defaults.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','source_x_px','broadphase_calls','nearest_type18_instance','activation_count','effect_count']);w.writerows(trace)
 result={'ticks':360,'actors':len(actors),'positioned_fixture_objects':[{'instance_id':x['instance_id'],'type':x['type'],'anchor_px':x['anchor_px'],'flags':x['flags_byte']} for x in records],'gif_frames':len(frames),'broadphase_callbacks':totalCallbacks,'activations':len(activations),'activated_instance_ids':sorted({x[2] for x in activations}),'sound_requests':len(effects),'base_event':list(probe[41:44]),'foot_event':list(extra[4:7]),'scope':'Native Shrek locomotion and E788 falling-strip handler, sweep, real type-18 script/animation and target update. Original recovered ogre base/foot events initialized through s2_shrek_reactions_init; target moved to anchor (120,350) and scheduled jump inputs are explicit fixtures. Two actors with fixed lifetime/update ordering; remaining constructor/global effects, incoming action methods, carry release, full world loop, PCM and Android execution are excluded.'};(ROOT/'docs/native_shrek_defaults_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
