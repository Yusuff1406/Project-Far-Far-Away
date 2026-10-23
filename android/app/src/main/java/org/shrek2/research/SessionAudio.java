package org.shrek2.research;

import android.app.Activity;
import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.media.SoundPool;
import java.io.InputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

// All103 nonzero original FX instruments, rendered offline with both GAX slots. SoundPool is the port's playback backend.
public final class SessionAudio implements AutoCloseable {
 private final Activity activity;
 private final SoundPool pool;
 private final AudioManager manager;
 private final AudioFocusRequest focus;
 private final HashMap<Integer,Integer> samples=new HashMap<>();
 private final HashSet<Integer> loaded=new HashSet<>();
 private final ArrayList<Integer> streams=new ArrayList<>();
 private static final long MAX_PENDING_EFFECT_NS=250_000_000L;
 private static final class PendingEffect {
  final int sound,priority,gain;final long queuedAt;
  PendingEffect(int sound,int priority,int gain){this.sound=sound;this.priority=priority;this.gain=gain;queuedAt=System.nanoTime();}
 }
 private final ArrayList<PendingEffect> pendingEffects=new ArrayList<>();
 private boolean enabled,musicEnabled,resumed=false,focused=false,closed=false;
 private LoopMusic chapterMusic,levelOverride;private int overrideSong=-1;
 private int frontendEpilogue=-1;
 private LoopMusic epilogueMusic;
 private LoopMusic music,bonusMusic,bootMusic,frontendMusic,creditsMusic,browserMusic;
 private boolean frontendMode=false,menuPaused=false,finaleMenuMusic=false;
 private LoopMusic selectedMusic;private float trackGain=1f;
 private final android.os.Handler menuFadeHandler=new android.os.Handler();private float menuGain=1f;private final Runnable menuFade=new Runnable(){public void run(){if(closed)return;float target=menuPaused?.25f:1f;trackGain=Math.min(1f,trackGain+.08f);menuGain+=Math.max(-.075f,Math.min(.075f,target-menuGain));startMusic();if(trackGain<1f||Math.abs(menuGain-target)>.001f)menuFadeHandler.postDelayed(this,16);}};
 private boolean browsing=false;private int browserSong=-1;
 private boolean frontendBoot=false,frontendCredits=false;
 private boolean bonusScene=false,bonusMusicFailed=false;
 private int missed=0;
 public SessionAudio(Activity activity,boolean initial,boolean initialMusic)throws IOException {
  this(activity,initial,initialMusic,false);
 }
 public SessionAudio(Activity activity,boolean initial,boolean initialMusic,boolean menu)throws IOException {
  this.activity=activity;enabled=initial;musicEnabled=initialMusic;frontendBoot=menu;frontendMode=menu;
  AudioAttributes attrs=new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build();
  manager=(AudioManager)activity.getSystemService(Context.AUDIO_SERVICE);
  pool=new SoundPool.Builder().setMaxStreams(8).setAudioAttributes(attrs).build();
  focus=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN).setAudioAttributes(attrs).setOnAudioFocusChangeListener(change->{
   if(closed)return;focused=change==AudioManager.AUDIOFOCUS_GAIN;
   if(!focused){stop();pauseMusic();}else startMusic();
  }).build();
  pool.setOnLoadCompleteListener((p,id,status)->activity.runOnUiThread(()->{if(closed)return;if(status==0)loaded.add(id);else{pendingEffects.removeIf(q->samples.get(q.sound)!=null&&samples.get(q.sound)==id);missed++;}flushLoadedEffect(id);}));
  try {
   for(int id=1;id<=103;id++)try(AssetFileDescriptor file=activity.getAssets().openFd("session/audio/sfx_"+id+".wav")){
    int sample=pool.load(file,1);if(sample==0)throw new IOException("Could not load sound "+id);samples.put(id,sample);
   }
   try(InputStream intro=activity.getAssets().open("session/music/scene_00_intro.wav");InputStream loop=activity.getAssets().open("session/music/scene_00_loop.wav")){music=new LoopMusic(MusicPcm.load(intro,loop));}
     try(InputStream intro=activity.getAssets().open("session/music/bonus_00_intro.wav");InputStream loop=activity.getAssets().open("session/music/bonus_00_loop.wav")){bonusMusic=new LoopMusic(MusicPcm.load(intro,loop));}
   if(menu){
    try(InputStream intro=activity.getAssets().open("frontend/menu_intro.wav");InputStream loop=activity.getAssets().open("frontend/menu_loop.wav")){frontendMusic=new LoopMusic(MusicPcm.load(intro,loop));}
   }
   if(menu)try(InputStream intro=activity.getAssets().open("frontend/credits_intro.wav");InputStream loop=activity.getAssets().open("frontend/credits_loop.wav")){creditsMusic=new LoopMusic(MusicPcm.load(intro,loop));}
   if(menu)try(InputStream intro=activity.getAssets().open("frontend/boot_intro.wav");InputStream loop=activity.getAssets().open("frontend/boot_loop.wav")){bootMusic=new LoopMusic(MusicPcm.load(intro,loop));}
  }catch(IOException e){if(creditsMusic!=null)creditsMusic.close();if(frontendMusic!=null)frontendMusic.close();if(bootMusic!=null)bootMusic.close();if(bonusMusic!=null)bonusMusic.close();if(music!=null)music.close();pool.release();closed=true;throw e;}
 }
 private void stop(){for(int stream:streams)pool.stop(stream);streams.clear();pendingEffects.clear();}
 // Sample completion callbacks can arrive in any order. Preserve the source
 // event order; never replay an old jump after a newer damage effect.
 private void flushLoadedEffect(int sample){
  while(!pendingEffects.isEmpty()){
   PendingEffect q=pendingEffects.get(0);Integer id=samples.get(q.sound);
   if(System.nanoTime()-q.queuedAt>MAX_PENDING_EFFECT_NS||id==null){pendingEffects.remove(0);missed++;continue;}
   if(!loaded.contains(id))return;
   pendingEffects.remove(0);if(enabled&&resumed&&focused&&!closed)playLoaded(id,q.priority,q.gain);
  }
 }
 private void pauseMusic(){pauseMusicExcept(null);}
 private void pauseMusicExcept(LoopMusic keep){if(levelOverride!=null)levelOverride.pause();if(epilogueMusic!=null)epilogueMusic.pause();if(chapterMusic!=null)chapterMusic.pause();if(music!=null)music.pause();if(bonusMusic!=null)bonusMusic.pause();if(bootMusic!=null)bootMusic.pause();if(frontendMusic!=null&&frontendMusic!=keep)frontendMusic.pause();if(creditsMusic!=null)creditsMusic.pause();if(browserMusic!=null)browserMusic.pause();}
 private void startMusic(){LoopMusic selected=browsing?browserMusic:frontendMode?(frontendEpilogue>=0?(frontendEpilogue==5?frontendMusic:epilogueMusic):frontendBoot?bootMusic:frontendCredits?creditsMusic:frontendMusic):finaleMenuMusic?frontendMusic:levelOverride!=null?levelOverride:bonusScene&&!bonusMusicFailed?bonusMusic:chapterMusic!=null?chapterMusic:music;if(!closed&&resumed&&focused&&musicEnabled&&selected!=null){if(selected!=selectedMusic){selectedMusic=selected;trackGain=0f;menuFadeHandler.removeCallbacks(menuFade);menuFadeHandler.postDelayed(menuFade,16);}selected.volume(menuGain*trackGain);selected.play();}}
 private void acquire(){focused=true;startMusic();}
 private void refreshFocus(){if(resumed&&(enabled||musicEnabled))acquire();else {manager.abandonAudioFocusRequest(focus);focused=false;}}
 public void setEnabled(boolean value){enabled=value;stop();refreshFocus();}
 public void setMusicEnabled(boolean value){musicEnabled=value;if(!value)pauseMusic();refreshFocus();}
 public void resume(){if(closed)return;resumed=true;refreshFocus();}
 public void pause(){if(closed)return;resumed=false;stop();pauseMusic();manager.abandonAudioFocusRequest(focus);focused=false;}
 public void setChapterMusic(int scene){finaleMenuMusic=false;setLevelOverride(-1);String prefix;switch(scene){case 0:prefix="campaign/music/song_0820dc94_";break;case 1:prefix="campaign/music/song_08209b78_";break;case 2:prefix="campaign/music/song_08209428_";break;case 13:prefix="campaign/music/song_0820f388_";break;case 17:prefix="campaign/music/song_0820dc94_";break;case 25:prefix="campaign/music/song_0820dc94_";break;case 14:prefix="campaign/music/song_08209b78_";break;case 9:prefix="campaign/music/song_0820f388_";break;case 11:prefix="campaign/music/song_08209428_";break;case 8:prefix="campaign/music/song_0820f7b8_";break;case 4:prefix="campaign/music/song_0820bf90_";break;case 10:prefix="campaign/music/song_0820d4dc_";break;case 23:prefix="campaign/music/song_0820f7b8_";break;case 21:prefix="campaign/music/song_08209b78_";break;case 29:prefix="campaign/music/song_0820dc94_";break;case 24:prefix="campaign/music/song_0820f7b8_";break;case 3:prefix="campaign/music/song_0820af48_";break;case 19:prefix="campaign/music/song_0820d4dc_";break;case 22:prefix="campaign/music/song_0820af48_";break;case 28:prefix="campaign/music/song_0820dc94_";break;case 12:prefix="campaign/music/song_0820fc5c_";break;case 5:prefix="campaign/music/song_0820a320_";break;case 20:prefix="campaign/music/song_0820af48_";break;case 15:prefix="campaign/music/song_0820e9b8_";break;case 16:prefix="campaign/music/song_0820c5f0_";break;default:throw new IllegalArgumentException("Unknown scene");}pauseMusic();if(chapterMusic!=null){chapterMusic.close();chapterMusic=null;}if(scene!=0){try(InputStream intro=activity.getAssets().open(prefix+"intro.wav");InputStream loop=activity.getAssets().open(prefix+"loop.wav")){chapterMusic=new LoopMusic(MusicPcm.load(intro,loop));}catch(IOException e){throw new IllegalStateException("Level music unavailable",e);}}startMusic();}
 public void setLevelOverride(int song){if(song==overrideSong)return;LoopMusic next=null;if(song>=0){String prefix=song==0x082106c0?"frontend/menu_":String.format(java.util.Locale.ROOT,"campaign/music/song_%08x_",song);try(InputStream intro=activity.getAssets().open(prefix+"intro.wav");InputStream loop=activity.getAssets().open(prefix+"loop.wav")){next=new LoopMusic(MusicPcm.load(intro,loop));}catch(IOException e){throw new IllegalStateException("Track unavailable",e);}}pauseMusic();if(levelOverride!=null)levelOverride.close();levelOverride=next;overrideSong=song;startMusic();}
 public void setBrowsing(boolean value){if(closed||browsing==value)return;pauseMusic();browsing=value;startMusic();}
 public void setBrowserSong(int song){if(closed||browserSong==song)return;String prefix=String.format(java.util.Locale.ROOT,"campaign/music/song_%08x_",song);try(InputStream intro=activity.getAssets().open(prefix+"intro.wav");InputStream loop=activity.getAssets().open(prefix+"loop.wav")){LoopMusic next=new LoopMusic(MusicPcm.load(intro,loop));pauseMusic();if(browserMusic!=null)browserMusic.close();browserMusic=next;browserSong=song;startMusic();}catch(IOException e){throw new IllegalStateException("Map music unavailable",e);}}
 public void setFrontendMode(boolean menu){if(closed||frontendMode==menu)return;if(menu&&frontendMusic==null)return;pauseMusicExcept(finaleMenuMusic?frontendMusic:null);frontendMode=menu;if(menu){music.reset();bonusMusic.reset();if(chapterMusic!=null)chapterMusic.reset();bonusScene=false;}if(frontendMusic!=null&&!finaleMenuMusic&&frontendEpilogue!=5)frontendMusic.reset();startMusic();}
 public void setMenuPaused(boolean paused){if(closed)return;menuPaused=paused;menuFadeHandler.removeCallbacks(menuFade);menuFadeHandler.post(menuFade);startMusic();}
 public void setFrontendCredits(boolean credits){if(closed||frontendCredits==credits)return;pauseMusic();frontendCredits=credits;if(creditsMusic!=null)creditsMusic.reset();if(!credits&&frontendMusic!=null)frontendMusic.reset();startMusic();}
 public void setFrontendEpilogue(int group){if(closed||frontendEpilogue==group)return;pauseMusicExcept((group==5&&finaleMenuMusic)||(frontendEpilogue==5&&group<0)?frontendMusic:null);if(epilogueMusic!=null){epilogueMusic.close();epilogueMusic=null;}frontendEpilogue=group;if(group>=0&&group!=5){int[] songs={0x08210364,0x08210364,0x0820d4dc,0x0820fc5c,0x0820bf90,0x082106c0};String prefix=group==5?"frontend/menu_":String.format(java.util.Locale.ROOT,"campaign/music/song_%08x_",songs[group]);try(InputStream intro=activity.getAssets().open(prefix+"intro.wav");InputStream loop=activity.getAssets().open(prefix+"loop.wav")){epilogueMusic=new LoopMusic(MusicPcm.load(intro,loop));}catch(IOException e){throw new IllegalStateException("Cutscene music unavailable",e);}}startMusic();}
 public void setFrontendBoot(boolean boot){if(closed||frontendBoot==boot)return;pauseMusic();frontendBoot=boot;startMusic();}
 public void setBonusScene(boolean bonus){if(closed||bonusScene==bonus)return;pauseMusic();bonusScene=bonus;if(bonus&&!bonusMusicFailed){try{bonusMusic.reset();}catch(IllegalStateException failure){bonusMusicFailed=true;missed++;bonusMusic.close();}}startMusic();}
 // Level death keeps the active track and its playback cursor running.
 public void deathRestart(){if(closed)return;stop();}
 public void setFinaleMenuMusic(boolean value){if(closed||finaleMenuMusic==value)return;pauseMusic();finaleMenuMusic=value;if(value&&frontendMusic!=null)frontendMusic.reset();startMusic();}
 public void reset(){if(closed)return;finaleMenuMusic=false;selectedMusic=null;stop();pauseMusic();bonusScene=false;music.reset();bonusMusic.reset();if(chapterMusic!=null)chapterMusic.reset();if(levelOverride!=null)levelOverride.reset();startMusic();}
 public void play(int sound,int priority,int gain){
  if(closed||!enabled||!resumed||!focused||gain<=0)return;
  Integer sample=samples.get(sound);if(sample==null){missed++;return;}flushLoadedEffect(sample);
  if(!pendingEffects.isEmpty()||!loaded.contains(sample)){if(pendingEffects.size()<32)pendingEffects.add(new PendingEffect(sound,priority,gain));else missed++;return;}
  playLoaded(sample,priority,gain);
 }
 private void playLoaded(int sample,int priority,int gain){
  float volume=Math.max(0,Math.min(255,gain))/255f;
  int androidPriority=(int)Math.max(0,Math.min(Integer.MAX_VALUE,(long)priority+1000));
  int stream=pool.play(sample,volume,volume,androidPriority,0,1f);if(stream!=0)streams.add(stream);else missed++;
 }
 public int[] snapshot(){return new int[]{overrideSong,music.position(),chapterMusic==null?0:chapterMusic.position(),bonusMusic.position(),levelOverride==null?0:levelOverride.position(),frontendMusic==null?0:frontendMusic.position(),finaleMenuMusic?1:0};}
 public void restore(int[]s){if(s==null||(s.length!=5&&s.length!=7))return;stop();pauseMusic();setLevelOverride(s[0]);pauseMusic();music.seek(s[1]);if(chapterMusic!=null)chapterMusic.seek(s[2]);bonusMusic.seek(s[3]);if(levelOverride!=null)levelOverride.seek(s[4]);if(s.length==7){if(frontendMusic!=null)frontendMusic.seek(s[5]);finaleMenuMusic=s[6]!=0;}startMusic();}
 public String status(){return musicEnabled?(enabled?"music and effects":"music"):(enabled?(missed==0?"effects":"missed effect"):"sound off");}
 @Override public void close(){if(closed)return;menuFadeHandler.removeCallbacks(menuFade);pause();closed=true;if(levelOverride!=null)levelOverride.close();if(epilogueMusic!=null)epilogueMusic.close();if(chapterMusic!=null)chapterMusic.close();if(browserMusic!=null)browserMusic.close();music.close();bonusMusic.close();if(bootMusic!=null)bootMusic.close();if(creditsMusic!=null)creditsMusic.close();if(frontendMusic!=null)frontendMusic.close();pool.release();}
}
