#!/usr/bin/env python3
"""Render the same owned scene session called by Android's JNI bridge."""
import argparse,ctypes,json
from PIL import Image,ImageDraw
from replay_generic_actor import ROOT,IP
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--attack",action="store_true");ap.add_argument("--air-attack",action="store_true");ap.add_argument("--item-action",action="store_true");ap.add_argument("--effects",action="store_true");args=ap.parse_args();args.item_action=args.item_action or args.effects;args.attack=args.attack or args.air_attack;effectTrace=[];requests=libRequests=None;attacks=[];airAttacks=[];previousState=0
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create;create.argtypes=[ctypes.c_char_p]*4+[IP];create.restype=ctypes.c_void_p;destroy=lib.s2_session_destroy;destroy.argtypes=[ctypes.c_void_p];destroy.restype=None;step=lib.s2_session_step;step.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];error=ctypes.c_int32();handle=create(*paths,ctypes.byref(error));assert handle and not error.value;pixels=(ctypes.c_uint32*38400)();info=(ctypes.c_int32*8)();frames=[];states=[]
 try:
  for tick in range(1,401 if args.item_action else 601 if args.air_attack else 421 if args.attack else 361):
   held=4 if tick in [80,240] else 16 if 125<=tick<160 else 1 if tick in [170,300] else 0
   if args.attack and tick in [30,355]:held=2
   if args.air_attack and tick==440:held=1
   if args.air_attack and tick in [310,450]:held=2
   if args.item_action and 130<=tick<=190:held=2
   if args.item_action and tick>=200:held=0
   assert step(handle,held,pixels,len(pixels),info)==0,(tick,list(info));states.append(list(info))
   if info[1]==7 and previousState!=7:attacks.append(tick)
   if info[1]==16 and previousState!=16:airAttacks.append(tick)
   if args.effects:
    effectState=(ctypes.c_int32*9)();effectFn=lib.s2_session_effect_state;effectFn.argtypes=[ctypes.c_void_p,IP];assert effectFn(handle,effectState)==0;effectTrace.append([tick,*effectState])
   previousState=info[1]
   if tick%6:continue
   rgba=bytearray(38400*4)
   for i,c in enumerate(pixels):rgba[i*4:i*4+4]=bytes([(c>>16)&255,(c>>8)&255,c&255,255])
   im=Image.frombytes('RGBA',(240,160),bytes(rgba));draw=ImageDraw.Draw(im);draw.rectangle((0,0,239,25),fill='black');draw.text((4,2),'NATIVE SESSION / FOLLOW CAMERA',fill='white');draw.text((4,14),f'{tick:03d} STATE {info[1]} ITEM {info[3]}',fill=(196,231,152));frames.append(im.convert('RGB'))
  if args.item_action:
   libRequests=lib.s2_session_requests;libRequests.argtypes=[ctypes.c_void_p,IP,ctypes.c_size_t];rows=(ctypes.c_int32*(256*8))();n=libRequests(handle,rows,256);assert n>=0;requests=[list(rows[i*8:i*8+8]) for i in range(n)]
   assert [r[1] for r in requests]==[1,11,16,17,19],requests
 finally:destroy(handle)
 prefix='native_session_effects' if args.effects else 'native_session_item_action' if args.item_action else 'native_session_air_attack' if args.air_attack else 'native_session_attack' if args.attack else 'native_session_controls'
 if args.effects:
  assert effectTrace[224][1:]==[896,3,128,1,1,0,1,3,64],effectTrace[224]
  assert effectTrace[252][1]==0 and effectTrace[252][4]==29,effectTrace[252]
  assert effectTrace[288][-2:]==[0,0],effectTrace[288]
 if args.attack:assert attacks==[30,355],attacks
 if args.air_attack:assert airAttacks==[310,450] and states[-1][1]==0,airAttacks
 frames[0].save(ROOT/f'previews/{prefix}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0);frames[37 if args.effects else 22 if args.item_action else 52 if args.air_attack else 5 if args.attack else 28].resize((720,480),Image.Resampling.NEAREST).save(ROOT/f'previews/{prefix}.png');result={'effect_states':effectTrace,'requests':requests,'owner_release_ticks':[states[i][0] for i in range(1,len(states)) if states[i-1][3] and not states[i][3]],'ground_attack_ticks':attacks,'air_attack_ticks':airAttacks,'ticks':400 if args.item_action else 600 if args.air_attack else 420 if args.attack else 360,'gif_frames':len(frames),'final_info8':states[-1],'scope':'Host execution of the same owned C++ session wired to Android JNI. Scripted input, fixed scene/item and follow camera; no Android/device execution or PCM.'};(ROOT/f'docs/{prefix}_preview.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='effect_states'},indent=2))
if __name__=='__main__':main()
