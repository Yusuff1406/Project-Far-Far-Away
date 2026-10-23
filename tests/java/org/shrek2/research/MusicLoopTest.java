package org.shrek2.research;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import android.media.AudioTrack;
public final class MusicLoopTest {
 static int checks;
 static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
 static MusicPcm load(byte[] a,byte[] b)throws IOException{return MusicPcm.load(new ByteArrayInputStream(a),new ByteArrayInputStream(b));}
 static void rejects(byte[] a,byte[] b)throws Exception{try{load(a,b);throw new AssertionError("accepted corrupt WAV");}catch(IOException expected){checks++;}}
 public static void main(String[] args)throws Exception {
  byte[] a=Files.readAllBytes(Paths.get(args[0])),b=Files.readAllBytes(Paths.get(args[1]));MusicPcm pcm=load(a,b);
  check(pcm.sampleRate==31537);boolean bonus=args[0].endsWith("bonus_00_intro.wav"),menu=args[0].endsWith("menu_intro.wav");boolean boot=args[0].endsWith("boot_intro.wav")||args[0].contains("song_"),credits=args[0].endsWith("credits_intro.wav");check(pcm.loopStartFrames==(credits?168960:boot?(a.length-44)/2:menu?0:bonus?380160:135168));check(pcm.loopEndFrames==(credits?1182720:boot?(a.length+b.length-88)/2:menu?1216512:bonus?1140480:1757184));check(pcm.pcm.length==(credits?2365440:boot?a.length+b.length-88:menu?2433024:bonus?2280960:3514368));
  check(Arrays.equals(Arrays.copyOfRange(pcm.pcm,0,pcm.loopStartFrames*2),Arrays.copyOfRange(a,44,a.length)));check(Arrays.equals(Arrays.copyOfRange(pcm.pcm,pcm.loopStartFrames*2,pcm.pcm.length),Arrays.copyOfRange(b,44,b.length)));
  LoopMusic music=new LoopMusic(pcm);AudioTrack t=AudioTrack.last;check(t.mode==AudioTrack.MODE_STATIC);check(t.writeCalls==1);check(t.rate==31537&&t.channels==1&&t.encoding==2);check(t.start==pcm.loopStartFrames&&t.end==pcm.loopEndFrames&&t.count==-1);check(t.volume==.65f);
  music.play();check(t.playCalls==1);music.play();check(t.playCalls==1);
  byte[] first=t.render(pcm.loopEndFrames+64);check(Arrays.equals(Arrays.copyOf(first,pcm.pcm.length),pcm.pcm));check(Arrays.equals(Arrays.copyOfRange(first,pcm.pcm.length,first.length),Arrays.copyOfRange(pcm.pcm,pcm.loopStartFrames*2,pcm.loopStartFrames*2+128)));
  for(int pass=0;pass<3;pass++){int head=t.position;music.pause();check(t.position==head);check(t.render(64).length==0);music.play();check(t.position==head);byte[] next=t.render(pcm.loopEndFrames-pcm.loopStartFrames);int offset=(head-pcm.loopStartFrames)*2;byte[] loop=Arrays.copyOfRange(pcm.pcm,pcm.loopStartFrames*2,pcm.pcm.length);for(int i=0;i<next.length;i++)if(next[i]!=loop[(offset+i)%loop.length])throw new AssertionError("loop sample "+i);checks++;}
  check(t.writeCalls==1);music.reset();check(t.position==0&&t.start==pcm.loopStartFrames&&t.count==-1);music.play();check(Arrays.equals(t.render(1024),Arrays.copyOf(pcm.pcm,2048)));music.close();check(t.released);music.close();music.play();check(t.playCalls==5);
  rejects(Arrays.copyOf(a,a.length-1),b);byte[] invalid=a.clone();invalid[0]=0;rejects(invalid,b);invalid=a.clone();invalid[22]=2;rejects(invalid,b);invalid=a.clone();invalid[34]=8;rejects(invalid,b);invalid=a.clone();invalid[40]=1;rejects(invalid,b);
  byte[] rate=b.clone();for(int i=0;i<4;i++){rate[24+i]=(byte)(22050>>>(i*8));rate[28+i]=(byte)(44100>>>(i*8));}rejects(a,rate);
  if(menu)rejects(a,a);
  AudioTrack.failWrite=true;try{new LoopMusic(pcm);throw new AssertionError();}catch(IOException expected){check(AudioTrack.last.released);}AudioTrack.failWrite=false;
  AudioTrack.failLoop=true;try{new LoopMusic(pcm);throw new AssertionError();}catch(IOException expected){check(AudioTrack.last.released);}AudioTrack.failLoop=false;
  System.out.println("MusicLoop checks="+checks+" repeated_samples="+((pcm.loopEndFrames-pcm.loopStartFrames)*3)+" mismatches=0");
 }
}
