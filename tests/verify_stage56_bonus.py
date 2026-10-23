#!/usr/bin/env python3
"""Reward oracle plus native controller-only bonus/reward, exit, HUD and carry-hit tests."""
import ctypes,json,struct,tempfile,sys
from pathlib import Path
from PIL import Image
from session_fixtures import without_intro
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
 for n,args in [('destroy',[ctypes.c_void_p]),('snapshot',[ctypes.c_void_p,IP]),('actor_snapshot',[ctypes.c_void_p,I,IP]),('minigame_actor_snapshot',[ctypes.c_void_p,I,IP]),('minigame_snapshot',[ctypes.c_void_p,IP]),('transition_snapshot',[ctypes.c_void_p,IP]),('player_event',[ctypes.c_void_p,IP]),('set_transitions',[ctypes.c_void_p,I]),('set_bonus_results',[ctypes.c_void_p,I]),('set_viewport',[ctypes.c_void_p,I,I]),('bonus_best',[ctypes.c_void_p]),('level_complete',[ctypes.c_void_p]),('minigame_state',[ctypes.c_void_p]),('health',[ctypes.c_void_p]),('requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,'s2_session_'+n).argtypes=args
 assets=ROOT/'android/app/src/main/assets/session';paths=[assets/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',assets/'sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());runs=[]
 previewOnly='--preview-only'in sys.argv
 with tempfile.TemporaryDirectory()as td:
  for width,kind in ([(240,'reward')] if previewOnly else [(w,k)for w in [240,480]for k in ['reward','result','exit','hud']]+[(240,k)for k in [81,82,83,84,85]]):
   data=bytearray(raw)
   if kind in ['reward','result']:struct.pack_into('<HH',data,18+52*44,100,350)
   elif kind=='exit':struct.pack_into('<HH',data,18+2*44,40,350)
   elif isinstance(kind,int):struct.pack_into('<3H',data,16+23*44,kind,40,350)
   f=Path(td)/'fixture.s2ob';f.write_bytes(data);err=I();h=c(*[str(p).encode()for p in paths],str(f).encode(),ctypes.byref(err));assert h,err.value
   try:
    l.s2_session_set_bonus_results(h,kind=='result');l.s2_session_set_viewport(h,width,160);l.s2_session_set_transitions(h,1);pix=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();mini=(I*320)();tr=(I*8)();start=failed=returned=done=None;score=0;fades=[];hud=[];modes=set();transitionFrames=[]
    if kind in ['reward','result']:assert l.s2_session_player_event(h,(I*3)(1,37,0))==1 and l.s2_session_health(h)==5
    for tick in range(1,3001 if kind in ['reward','result']else 501):
     b=0;mode=l.s2_session_minigame_state(h)
     if kind in ['reward','result']:
      if start is None:
       if tick==120:b=2
       elif tick>=140 and tick%12==4:b=1
      elif failed is not None:
       if kind=='result' and tick>=failed+120:b=1
      elif mode:
       age=info[0];l.s2_session_minigame_snapshot(h,mini)
       if not mini[102]:
        dx=112*256-mini[0];b=16 if dx>256 else 32 if dx<-256 else 2 if age>25 and mini[80]<=5 and age%8==0 else 0
       elif score>=5:b=32
       else:
        targets=[]
        for ident in [4,5,6]:
         a=(I*216)()
         if l.s2_session_minigame_actor_snapshot(h,ident,a)==0 and a[11]>0 and a[1]>0:targets.append((a[1],a))
        if targets:
         a=max(targets,key=lambda x:x[0])[1];future=max(0,(65*256-a[1])/max(1,a[11]));target=max(10*256,min(230*256,a[0]+a[5]*future));dx=target-mini[0];b=16 if dx>256 else 32 if dx<-256 else 0
      if returned:b=0
     elif kind=='exit':b=1 if tick>=40 and tick%12==4 else 0
     elif isinstance(kind,int):
      b=4 if tick==80 else 0
      if tick==300 and kind in [81,82]:
       l.s2_session_snapshot(h,hero);assert hero[81]==(5 if kind==81 else 7) and hero[83];assert l.s2_session_player_event(h,(I*3)(1,37,0))==1;assert l.s2_session_health(h)==(5 if kind==81 else 6);l.s2_session_snapshot(h,hero);assert hero[83]==0 and hero[81]==0
     assert l.s2_session_step(h,b,pix,len(pix),info)==0,(kind,width,tick,list(info));l.s2_session_transition_snapshot(h,tr);fades.append(tr[0]);mode=l.s2_session_minigame_state(h);l.s2_session_snapshot(h,hero);modes.add(hero[81])
     if tick==1:assert all(x==0xff000000 for x in pix)
     if kind=='reward' and width==240 and tick>100 and (tr[0]>0 or (len(fades)>1 and fades[-2]>0)):
      transitionFrames.append(Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
     if kind in ['reward','result']:
      if mode:
       if start is None:start=tick
       l.s2_session_minigame_snapshot(h,mini);score=mini[312]
       if mode==2 and failed is None:
        failed=tick
        if width==240:Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/native_minigame_reward.png')
      elif start and returned is None:returned=tick
      if returned and tick>returned+180:break
     elif kind=='exit' and l.s2_session_level_complete(h):done=tick;break
     elif kind=='hud' and tick>=17:
      im=Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA');hud.append(im.crop((width-16,4,width-2,21)).tobytes())
      if tick==44:im.resize((width*3,480),Image.Resampling.NEAREST).save(ROOT/f'previews/native_hud_coins_{width}.png');break
    assert fades[:16]==list(range(60,-1,-4))
    if kind in ['reward','result']:
     assert start and failed and returned and 5<=score<=9,(start,failed,returned,score);assert (returned-failed>=120) if kind=='result' else (returned-failed<=17);assert l.s2_session_health(h)==6 and l.s2_session_bonus_best(h)==score
     rows=(I*(256*8))();n=l.s2_session_requests(h,rows,256);awards=[list(rows[i*8:i*8+8])for i in range(n)if rows[i*8+1]==30];assert len(awards)==1 and awards[0][4]==84
     result=dict(kind=kind,width=width,score=score,health=6,returned=returned,awards=awards)
    elif kind=='exit':
     assert done and 64 in fades;Image.frombytes('RGBA',(width,160),bytes(pix),'raw','BGRA').resize((width*3,480),Image.Resampling.NEAREST).save(ROOT/f'previews/native_level_complete_{width}.png');assert l.s2_session_step(h,0,pix,len(pix),info)==0;assert l.s2_session_step(h,1,pix,len(pix),info)==0;assert not l.s2_session_level_complete(h) and info[0]==0;result=dict(kind=kind,width=width,completed=done)
    elif kind=='hud':assert len(set(hud))==7;result=dict(kind=kind,width=width,unique_frames=7)
    else:
     if kind in [81,82]:assert(5 if kind==81 else 7)in modes
     result=dict(kind=kind,width=width,carry_modes=sorted(modes),final_health=l.s2_session_health(h))
    if transitionFrames:transitionFrames[0].save(ROOT/'previews/native_bonus_mosaic.gif',save_all=True,append_images=transitionFrames[1:],duration=33,loop=0);transitionFrames[len(transitionFrames)//4].save(ROOT/'previews/native_bonus_mosaic.png')
    runs.append(result);print(result,flush=True)
   finally:l.s2_session_destroy(h)
 # Actual original reward-selection function, all five tables and boundary scores.
 from verify_generic_runtime import Original,Rom,FC
 o=Original(Rom(sys.argv[1]));f=l.s2_bonus_rewards;f.argtypes=[I,I,FC,ctypes.c_void_p,IP];cases=0
 @FC
 def fetch(a,out,n,ctx):
  for i,v in enumerate(struct.unpack('<'+'i'*n,o.u.mem_read(a,n*4))):out[i]=v
  return 1
 for level in range(5):
  for score in [-2147483648,-1,*range(101),2147483647]:
   o.u.mem_write(o.actor,bytes(40));o.u.mem_write(o.actor+0x18,struct.pack('<2i',level,score));o.call(0x80091a4,o.actor);out=(I*4)();assert f(level,score,fetch,None,out)>=0 and list(out)==list(struct.unpack('<4i',o.u.mem_read(o.actor+4,16)));cases+=1
 report=dict(runs=runs,original_reward_cases=cases,mismatches=0,scope='Source NPC53 to100,350 or exit3 to40,350 only in temporary fixtures; original row24 replaced by reward type81..85 for pickup tests. One initial hurt event; five-bounce score/award84/collection use controller and source contacts, no forced score or pickup. Additional owner hurt events verify consumed shield with no health loss and invisibility removal with health loss. Startup/outgoing fades enabled, seven HUD frames, exit dialogue2 and A retry. Original091A4 selection verified independently. Android/device excluded.');(ROOT/('docs/stage56_bonus_preview_validation.json' if previewOnly else 'docs/stage56_bonus_validation.json')).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
