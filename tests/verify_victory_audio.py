#!/usr/bin/env python3
"""Real end trigger -> source victory cue -> descriptor -> shipped PCM90."""
import ctypes,struct,json,hashlib,wave,tempfile,sys
from pathlib import Path
from session_fixtures import without_intro
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
for name,args in [('destroy',[ctypes.c_void_p]),('snapshot',[ctypes.c_void_p,IP]),('set_viewport',[ctypes.c_void_p,I,I]),('set_transitions',[ctypes.c_void_p,I]),('level_complete',[ctypes.c_void_p]),('step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP]),('audio_since',[ctypes.c_void_p,I,IP,ctypes.c_size_t,IP])]:getattr(l,'s2_session_'+name).argtypes=args
rom=Path(sys.argv[1]).read_bytes();row=next(struct.unpack_from('<10I',rom,0x4b73c+i*40)for i in range(24)if struct.unpack_from('<I',rom,0x4b73c+i*40)[0]==14);assert row[1]==0x0834f334 and row[9]==0x08053cd8;assert struct.unpack_from('<3i',rom,row[9]-0x8000000)==(90,-100,200)
raw=bytearray(without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes()));struct.pack_into('<HH',raw,18+2*44,40,350);assets=ROOT/'android/app/src/main/assets/session';cases=[]
with tempfile.TemporaryDirectory()as td:
 obj=Path(td)/'end.s2ob';obj.write_bytes(raw)
 for width in [240,480]:
  e=I();h=c(*[str(p).encode()for p in [assets/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',assets/'sprites',obj]],ctypes.byref(e));assert h,e.value;l.s2_session_set_viewport(h,width,160);l.s2_session_set_transitions(h,1);pix=(ctypes.c_uint32*(width*160))();info=(I*8)();hero=(I*320)();sounds=(I*(256*3))();cursor=0;next_=I();emitted=[];start=None;done=None
  try:
   for tick in range(1,501):
    assert l.s2_session_step(h,1 if tick>=40 and tick%12==4 else 0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero)
    if hero[80]==12 and start is None:start=tick
    n=l.s2_session_audio_since(h,cursor,sounds,256,ctypes.byref(next_));assert n>=0;cursor=next_.value
    for i in range(n):
     if sounds[i*3]==90:emitted.append([tick,*sounds[i*3:i*3+3]])
    if l.s2_session_level_complete(h):done=tick;break
   assert start and done and len(emitted)==1 and emitted[0][1:]==[90,-100,200] and start<emitted[0][0]<done,(width,start,done,emitted);cases.append(dict(width=width,victory_start=start,completion=done,cue=emitted[0]))
  finally:l.s2_session_destroy(h)
fx=next(x for x in json.loads((ROOT/'docs/complete_sfx_resources.json').read_text())['effects']if x['sound_id']==90);path=assets/'audio/sfx_90.wav';assert hashlib.sha256(path.read_bytes()).hexdigest()==fx['sha256']
with wave.open(str(path))as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,31537);duration=w.getnframes()/w.getframerate()
report=dict(cases=cases,source_descriptor='0x08053CD8',sound_id=90,pcm_seconds=duration,pcm_sha256=fx['pcm_sha256'],mismatches=0,device_tested=False);(ROOT/'docs/victory_audio_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
