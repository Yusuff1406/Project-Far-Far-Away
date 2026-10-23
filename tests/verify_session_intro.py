#!/usr/bin/env python3
"""Original scene intro: unmodified trigger, physical entry, modal controls and reset."""
import ctypes,hashlib,json,struct,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_dialogue_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(l,name).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];obj=ROOT/'objects/scene_00/scene.s2ob';raw=obj.read_bytes();results=[];images=[];frames=0
 with tempfile.TemporaryDirectory()as tmp:
  for pattern in ['complete','cancel','hold_entry_A','hold_entry_combo','outside','delayed_entry']:
   data=bytearray(raw)
   if pattern in ['outside','delayed_entry']:struct.pack_into('<HH',data,18+70*44,100,311)
   path=Path(tmp)/'fixture.s2ob';path.write_bytes(data);reference=None;summary={}
   for width in [240,480]:
    err=I();h=create(*[str(p).encode()for p in paths],str(path).encode(),ctypes.byref(err));assert h,err.value;assert l.s2_session_set_viewport(h,width,160)==0
    try:
     for replay in range(2):
      if replay:assert l.s2_session_reset(h)==0
      pix=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();zone=(I*216)();d=(I*80)();trace=[];started=None;ended=None;frozen=None;seen=[];last=False;serialAtHold=None
      for t in range(1,361):
       b=0
       if pattern=='hold_entry_A'and t<=30:b=1
       elif pattern=='hold_entry_combo'and t<=30:b=3
       elif pattern=='delayed_entry'and started is None:b=16
       elif pattern=='cancel'and t==20:b=64
       elif pattern not in ['cancel','outside'] and t>=50 and t%8==2:b=1
       if t==40 and started is not None and ended is None:b=3
       if ended is not None and t<=ended+12:b=64 if pattern=='cancel'else 1
       assert l.s2_session_step(h,b,pix,len(pix),info)==0,(pattern,width,replay,t,list(info));frames+=1;l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,71,zone);l.s2_session_dialogue_snapshot(h,d);active=bool(d[64])
       if active and started is None:started=t;frozen=bytes(hero);assert zone[40]&1
       if active:
        assert bytes(hero)==frozen,(pattern,t,'world advanced')
        if not seen or seen[-1]!=(d[67],d[65]):seen.append((d[67],d[65]))
       if last and not active:assert ended is None;ended=t;assert bytes(hero)==frozen
       if ended is not None:assert not active and zone[40]&1,(pattern,t,'intro repeated')
       if ended is not None and t<=ended+12:assert hero[80]not in [2,3,4],(pattern,t,'closing A jumped')
       if t==1:serialAtHold=d[67]
       if t==30 and pattern in ['hold_entry_A','hold_entry_combo']:assert d[67]==serialAtHold==1 and d[74]==0
       if t==39:beforeCombo=list(d[65:68])+[d[74]]
       if t==40 and active:assert list(d[65:68])+[d[74]]==beforeCombo
       if width==240 and replay==0 and pattern=='complete'and active and t%4==1:images.append(Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST))
       if width==480 and replay==0 and pattern=='complete'and t==1:Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').convert('RGB').resize((1440,480),Image.Resampling.NEAREST).save(ROOT/'previews/native_intro_wide.png')
       trace.append(hashlib.sha256(bytes(hero)+bytes(zone)+bytes(d)).hexdigest());last=active
      if pattern=='outside':assert started is None and not zone[40]&1
      else:
       assert ended is not None and(started==1 if pattern!='delayed_entry'else started>1),(pattern,started,ended)
       assert d[67]==(1 if pattern=='cancel'else 5),(pattern,list(d[64:]))
      if reference is None:reference=trace;summary={'pattern':pattern,'start':started,'end':ended,'text_messages':d[67],'portraits':[hex(p[1])for p in seen]}
      else:assert trace==reference,(pattern,width,replay)
      assert l.s2_session_reset(h)==0;l.s2_session_actor_snapshot(h,71,zone);l.s2_session_dialogue_snapshot(h,d);assert not(zone[40]&1)and not any(d)
    finally:l.s2_session_destroy(h)
   results.append(summary)
 images[0].save(ROOT/'previews/native_intro.png');images[0].save(ROOT/'previews/native_intro.gif',save_all=True,append_images=images[1:],duration=67,loop=0)
 report={'native_scene_frames':frames,'scenarios':results,'mismatches':0,'scope':'Actual source scene zone71/type151 at31,311 and player spawn unchanged in default scenarios; additional relocated zone tests no early activation and physical entry. Five source texts/portraits, modal freeze, strictA+B refusal, held-entry keys, menuSTART cancellation, consumed zone/no retrigger, restart and240/480 state equality. Native pre-update scheduling and pagination are integration choices; Android/device excluded.'};(ROOT/'docs/session_intro_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
