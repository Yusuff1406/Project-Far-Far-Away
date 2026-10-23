#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Controller-only talks with all three NPCs; modal freeze, pages, reset, wide."""
import ctypes,json,struct,tempfile,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_world_info',[ctypes.c_void_p,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_aux_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_dialogue_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(l,name).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());images=[];results=[];frames=0
 with tempfile.TemporaryDirectory()as tmp:
  for ident,message,lines in[(68,67,1),(66,68,2),(21,69,4)]:
   data=bytearray(raw);struct.pack_into('<HH',data,18+(ident-1)*44,40,350);p=Path(tmp)/'fixture.s2ob';p.write_bytes(data)
   for pattern in['normal','cancel','no_input','no_tag','entry_combo']:
    if pattern=='entry_combo'and ident!=68:continue
    fixture=bytearray(data)
    if pattern=='no_tag':struct.pack_into('<I',fixture,16+(ident-1)*44+20,0)
    p.write_bytes(fixture)
    reference=None;summary={}
    for width in[240,480]:
     err=I();h=create(*[str(x).encode()for x in paths],str(p).encode(),ctypes.byref(err));assert h,err.value;assert l.s2_session_set_viewport(h,width,160)==0
     try:
      for replay in range(2):
       if replay:assert l.s2_session_reset(h)==0
       pix=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();npc=(I*216)();d=(I*80)();meta=(I*4)();trace=[];start=None;end=None;frozen=None;lastActive=False;serials=[];comboPage=None;heldPage=None
       for t in range(1,241):
        b=0
        if pattern!='no_input':
         if t==20:b=2
         elif pattern=='cancel'and t==40:b=64
         elif pattern=='entry_combo':
          if t==21:b=3
          elif 60<=t<=99 or 120<=t<=139:b=1
         elif pattern=='normal':
          if t==40:b=3
          elif 50<=t<=75:b=1
          elif t>=90 and t%12==6:b=1
        if pattern=='normal'and end is not None and t<=end+8:b=1
        assert l.s2_session_step(h,b,pix,len(pix),info)==0,(ident,pattern,width,replay,t,list(info));l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,ident,npc);l.s2_session_dialogue_snapshot(h,d);active=bool(d[64]);frames+=1
        if active and start is None:start=t;frozen=bytes(hero)
        if pattern=='normal'and end is not None and t<=end+8:assert hero[80]not in[2,3,4],(ident,'closing A leaked into jump')
        if pattern=='entry_combo'and end is not None:assert hero[80]==0 and list(hero[:2])==list(struct.unpack('<2i',frozen[:8])),(t,'entry combo resumed after dialogue')
        if active:assert bytes(hero)==frozen,(ident,t,'world moved during dialogue')
        if lastActive and not active and end is None:end=t;assert bytes(hero)==frozen
        if active and(not serials or serials[-1]!=d[67]):serials.append(d[67])
        if pattern=='normal':
         if t==39:comboPage=d[74]
         if t==40:assert d[74]==comboPage and active,(ident,'A+B advanced')
         if t==50:heldPage=(d[67],d[74])
         if t==75:assert active and(d[67],d[74])==heldPage,(ident,'held A skipped conversation')
        if ident==68 and pattern=='normal'and width==240 and replay==0 and t%3==0 and t<130:images.append(Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST))
        trace.append(hashlib.sha256(bytes(hero)+bytes(npc)+bytes(d)).hexdigest());lastActive=active
       assert l.s2_session_world_info(h,meta)==0 and list(meta)==[71,67,3,70]
       if pattern in['no_input','no_tag']:
        assert start is None and d[67]==0
        cue=(I*80)();assert l.s2_session_aux_snapshot(h,ident,cue)==(0 if pattern=='no_tag'else 1)
       else:
        assert start is not None and end is not None,(ident,pattern,start,end,list(d[64:]))
        if pattern in['normal','entry_combo']:assert d[67]==lines,(ident,d[67],lines)
        elif pattern=='cancel':assert end==40
       if reference is None:reference=trace;summary={'npc':ident,'message_id':message,'pattern':pattern,'start':start,'end':end,'text_messages':d[67]}
       else:assert trace==reference,(ident,pattern,width,replay)
       assert l.s2_session_reset(h)==0;l.s2_session_dialogue_snapshot(h,d);assert not any(d)
     finally:l.s2_session_destroy(h)
    results.append(summary)
 images[0].save(ROOT/'previews/native_npc_dialogue_fixture.gif',save_all=True,append_images=images[1:],duration=50,loop=0);images[12].save(ROOT/'previews/native_npc_dialogue_fixture.png')
 report={'native_scene_frames':frames,'scenarios':results,'mismatches':0,'scope':'Real B/controller and original NPC contacts/scripts, no forced actor/dialogue events. NPC position moved to40,350 only in temporary fixture. NPC tag0 correctly refuses B. Text controls: no auto-talk, strict A+B refusal, held A advances once, three dialogs finish, sourceSTART interrupt via64. Queued A+B on dialogue-entry frame cleared and does not resume after close. Player freeze, 240/480 viewport state equality and reset checked. Rendering/pagination native; Android device excluded.'};(ROOT/'docs/session_dialogue_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
