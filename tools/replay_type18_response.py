#!/usr/bin/env python3
"""Real type-18 scripts and artwork; local trigger times/low audio backend are fixtures."""
import ctypes,csv,json
from PIL import Image,ImageDraw
from replay_generic_actor import Resources,ROOT,IP,FC,RC
REG=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);PLAY=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_void_p);VOL=ctypes.CFUNCTYPE(None,ctypes.c_int32,ctypes.c_uint32,ctypes.c_void_p)
def main():
 res=Resources();lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));init=lib.s2_generic_runtime_init;init.argtypes=[IP,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,FC,ctypes.c_void_p,IP];start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,IP];start.restype=None;rinit=lib.s2_reactions_init;rinit.argtypes=[ctypes.c_int32,IP];rinit.restype=None;activate=lib.s2_generic_activate;activate.argtypes=[IP,IP,IP];step=lib.s2_generic_runtime_step_effects;step.argtypes=[ctypes.c_char_p,IP,IP,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,FC,RC,ctypes.c_void_p,ctypes.c_int,IP,REG,SINK];audio=lib.s2_audio_sfx_resource;audio.argtypes=[IP,ctypes.c_uint32,ctypes.c_int32,FC,PLAY,VOL,ctypes.c_void_p];clamp=lib.s2_audio_volume_byte;clamp.argtypes=[ctypes.c_uint32];clamp.restype=ctypes.c_uint32
 render=lib.s2_render_file;render.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*5+[ctypes.c_void_p,ctypes.c_size_t];sprite=lib.s2_sprite_render_file;sprite.argtypes=[ctypes.c_char_p]+[ctypes.c_int]*7+[ctypes.c_void_p,ctypes.c_size_t];anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[IP,IP,ctypes.c_int,ctypes.c_int,IP];anchor.restype=None
 source=next(x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'] if x['type']==18);s=(ctypes.c_int32*80)();vm=(ctypes.c_int32*64)();r=(ctypes.c_int32*72)();manager=(ctypes.c_int32*8)(1,0,256,0,0,0,0,0);assert init((ctypes.c_int32*2)(120*256,320*256),0,source['initial_animation'],0,res.fetch,None,s)==0;start(source['script'],vm);rinit(0,r)
 sounds=[];gains=[];currentTick=0
 @REG
 def registry(enabled,ctx):raise AssertionError('This script registers only a local reaction')
 @RC
 def random_value(ctx):return 37
 @PLAY
 def play(id,channel,priority,sub,ctx):sounds.append([currentTick,id,channel,priority,sub]);return channel
 @VOL
 def volume(voice,gain,ctx):gains.append([currentTick,voice,gain,clamp(gain)])
 @SINK
 def sink(kind,address,scale,ctx):
  if kind!=11:return -4
  e=audio(manager,address,scale,res.fetch,play,volume,None);return e if e<0 else 0
 frames=[];trace=[];triggerCount=0
 for currentTick in range(1,361):
  if currentTick in [40,140,240]:assert activate(vm,r,(ctypes.c_int32*3)(2,8,999))==1;triggerCount+=1
  assert step(str(ROOT/'collision/scene_00/scene.s2cl').encode(),s,vm,currentTick,3200*256,400*256,res.fetch,random_value,None,4096,r,registry,sink)==0
  item=res.lookup[s[47]];trace.append([currentTick,*s[:2],item['index'],s[22],vm[2],r[0],r[8],manager[1],len(sounds)])
  if currentTick%6:continue
  width=240;height=160;buf=(ctypes.c_uint8*(width*height*4))();assert render(str(ROOT/'extracted/scene_00/scene.s2lv').encode(),0,230,width,height,-1,buf,len(buf))==0;im=Image.new('RGBA',(width,height),(24,24,24,255));im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)));point=(ctypes.c_int32*2)();anchor(ctypes.cast(ctypes.byref(s,72*4),IP),s,s[18],s[38],point);assert sprite(str(ROOT/'sprites'/item['bank']/'bank.s2sp').encode(),item['index'],s[22],s[18],width,height,point[0]//256,point[1]//256-230,buf,len(buf))==0;im.alpha_composite(Image.frombytes('RGBA',(width,height),bytes(buf)));d=ImageDraw.Draw(im);d.rectangle((0,0,width-1,38),fill='black');d.text((4,2),'TYPE 18 / ORIGINAL SCRIPTS',fill='white');d.text((4,14),f'{currentTick:03d} ANIM {item["index"]:02d} TRIGGERS {triggerCount}',fill=(196,231,152));d.text((4,26),f'SFX REQUESTS {len(sounds)} / NO AUDIO OUTPUT',fill=(230,211,147));frames.append(im.convert('RGB'))
 assert len(sounds)==3 and [x[1:] for x in sounds]==[[59,0,-100,-1],[59,1,-100,-1],[59,0,-100,-1]];assert all(x[2:]==[200,200] for x in gains)
 frames[0].save(ROOT/'previews/native_type18_response.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[7].resize((720,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_type18_response.png')
 with (ROOT/'docs/native_type18_response.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tick','x_q8','y_q8','animation_index','sequence','vm_depth','local_count','local_event_id','next_audio_channel','sound_requests']);w.writerows(trace)
 result={'type':18,'ticks':360,'gif_frames':len(frames),'script_source':'Original ROM initial script 0x08052C28 and registered response 0x080531FC, read from exported resources','trigger_ticks':[40,140,240],'sound_requests':sounds,'volume_requests':gains,'scope':'Real original startup/reaction/animation scripts run through native actor/VM/event/audio-request modules. Trigger times and low-level play/volume outputs are fixtures; no physical trigger discovery, sample decoding, audible audio or Android execution.'};(ROOT/'docs/native_type18_response_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
