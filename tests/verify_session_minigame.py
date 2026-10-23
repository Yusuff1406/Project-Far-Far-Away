#!/usr/bin/env python3
"""Physical B contact -> original leprechaun dialogue -> scene26 -> frozen-world return."""
import ctypes,json,struct,tempfile,hashlib
from pathlib import Path
from PIL import Image
from session_fixtures import without_intro
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for n,a in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,I,IP]),('s2_session_dialogue_snapshot',[ctypes.c_void_p,IP]),('s2_session_minigame_snapshot',[ctypes.c_void_p,IP]),('s2_session_minigame_state',[ctypes.c_void_p]),('s2_session_coin_count',[ctypes.c_void_p]),('s2_session_audio_since',[ctypes.c_void_p,I,IP,ctypes.c_size_t,IP]),('s2_session_set_viewport',[ctypes.c_void_p,I,I]),('s2_session_step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,n).argtypes=a
 assets=ROOT/'android/app/src/main/assets/session';paths=[assets/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',assets/'sprites'];records=[];previews=[]
 with tempfile.TemporaryDirectory()as tmp:
  raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));assert struct.unpack_from('<H',raw,16+52*44)[0]==94;struct.pack_into('<HH',raw,18+52*44,40,350);fixture=Path(tmp)/'scene.s2ob';fixture.write_bytes(raw)
  for width in [240,480]:
   for cancel in [False,True]:
    err=I();h=create(*[str(p).encode()for p in paths],str(fixture).encode(),ctypes.byref(err));assert h,err.value;assert l.s2_session_set_viewport(h,width,160)==0
    try:
     for replay in range(2):
      if replay:assert l.s2_session_reset(h)==0
      pix=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();frozen=None;d=(I*80)();mini=(I*320)();npc=(I*216)();started=failed=returned=None;serials=set();score=0;heldResult=0
      for tick in range(1,1001):
       mode=l.s2_session_minigame_state(h);b=0
       if started is None:
        if tick==20:b=2
        elif cancel and tick==40:b=64
        elif not cancel and tick>=40 and tick%12==4:b=1
       elif failed is not None:
        if tick>=failed+4:b=1
       else:
        age=tick-started;b=16 if age<20 else 2 if age==20 else 0
       assert l.s2_session_step(h,b,pix,len(pix),info)==0,(width,cancel,replay,tick,list(info));l.s2_session_snapshot(h,hero);l.s2_session_dialogue_snapshot(h,d);mode=l.s2_session_minigame_state(h)
       if d[64]:serials.add(d[67])
       if mode:
        if started is None:
         started=tick;frozen=bytes(hero);l.s2_session_actor_snapshot(h,53,npc);frozenNpc=bytes(npc);worldCoins=l.s2_session_coin_count(h)
        assert bytes(hero)==frozen,'parent advanced in bonus'
        l.s2_session_actor_snapshot(h,53,npc);assert bytes(npc)==frozenNpc and l.s2_session_coin_count(h)==worldCoins
        assert l.s2_session_minigame_snapshot(h,mini)==0;score=max(score,mini[312])
        if width==240 and not cancel and replay==0 and tick%8==0:previews.append(Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST))
        if mode==2 and failed is None:failed=tick;heldResult=mini[316]
        if mode==2:assert mini[316]==heldResult
       elif started is not None:
        returned=tick;assert bytes(hero)==frozen,'return changed parent state';break
      assert started and failed and returned and score>=1,(started,failed,returned,score)
      if not cancel:assert serials=={1,2},serials
      for tick in range(60):assert l.s2_session_step(h,0,pix,len(pix),info)==0
      assert l.s2_session_actor_snapshot(h,53,npc)==0 and npc[40]&1,'one-shot NPC stayed after return'
      assert l.s2_session_minigame_state(h)==0
      rows=(I*(256*3))();cursor=I();n=l.s2_session_audio_since(h,0,rows,256,ctypes.byref(cursor));assert n>=0;audioIDs=list(rows[:n*3:3]);assert 60 in audioIDs and 100 in audioIDs,audioIDs
      again=(I*(256*3))();nextCursor=I();assert l.s2_session_audio_since(h,0,again,256,ctypes.byref(nextCursor))==n and list(again[:n*3])==list(rows[:n*3]);assert l.s2_session_audio_since(h,cursor.value,None,0,ctypes.byref(nextCursor))==0
      records.append({'width':width,'START_interrupt':cancel,'replay':replay,'entered':started,'failed':failed,'returned':returned,'score':score,'texts':len(serials),'sound_ids':audioIDs})
    finally:l.s2_session_destroy(h)
 if previews:previews[0].save(ROOT/'previews/native_mouse_minigame.gif',save_all=True,append_images=previews[1:],duration=130,loop=0);previews[12].save(ROOT/'previews/native_mouse_minigame.png')
 report={'runs':records,'mismatches':0,'scope':'Native controller inputs only. Leprechaun53 moved to40,350 in temporary object fixture; actual source type94 scripts, dialogue61, scene26 and type140/mushroom16 scripts. Source NPC disappearance, mouse-cap bidirectional contacts, score, floor failure, automatic return, world freeze, 240/480/reset. Reward-list campaign backend and original result screen not ported; Android not run.'};(ROOT/'docs/session_minigame_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
