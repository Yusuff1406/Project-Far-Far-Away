package org.shrek2.research;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;
import java.io.IOException;

// Static PCM loops in the audio service, without Java completion callbacks.
final class LoopMusic implements AutoCloseable {
 private final AudioTrack track;
 private final int loopStart,loopEnd;
 private boolean closed;
 LoopMusic(MusicPcm music)throws IOException {
  loopStart=music.loopStartFrames;loopEnd=music.loopEndFrames;
  AudioTrack candidate=null;
  try {
   candidate=new AudioTrack.Builder().setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build()).setAudioFormat(new AudioFormat.Builder().setEncoding(AudioFormat.ENCODING_PCM_16BIT).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).setSampleRate(music.sampleRate).build()).setTransferMode(AudioTrack.MODE_STATIC).setBufferSizeInBytes(music.pcm.length).build();
   if(candidate.getState()!=AudioTrack.STATE_INITIALIZED&&candidate.getState()!=AudioTrack.STATE_NO_STATIC_DATA)throw new IOException("Could not load or update resources");
   short[] samples=new short[music.pcm.length/2];for(int i=0;i<samples.length;i++)samples[i]=(short)((music.pcm[i*2]&255)|((music.pcm[i*2+1]&255)<<8));
   if(candidate.write(samples,0,samples.length)!=samples.length)throw new IOException("Could not load or update resources");
   if(candidate.setLoopPoints(loopStart,loopEnd,-1)!=AudioTrack.SUCCESS)throw new IOException("Could not load or update resources");candidate.setVolume(.65f);
  }catch(IOException|RuntimeException e){if(candidate!=null)candidate.release();if(e instanceof IOException)throw (IOException)e;throw new IOException("Could not load or update resources",e);}
  track=candidate;
 }
 void volume(float gain){if(!closed)track.setVolume(.65f*Math.max(0f,Math.min(1f,gain)));}
 void play(){if(!closed&&track.getPlayState()!=AudioTrack.PLAYSTATE_PLAYING)track.play();}
 void pause(){if(!closed&&track.getPlayState()==AudioTrack.PLAYSTATE_PLAYING)track.pause();}
 void reset(){if(closed)return;track.stop();if(track.reloadStaticData()!=AudioTrack.SUCCESS||track.setLoopPoints(loopStart,loopEnd,-1)!=AudioTrack.SUCCESS)throw new IllegalStateException("Could not load or update resources");}
 int position(){if(closed)return 0;long p=Integer.toUnsignedLong(track.getPlaybackHeadPosition());return p<loopEnd?(int)p:loopStart+(int)((p-loopStart)%(loopEnd-loopStart));}
 void seek(int frame){if(closed)return;if(frame<0)throw new IllegalArgumentException("Invalid music position");int p=frame<loopEnd?frame:loopStart+(frame-loopStart)%(loopEnd-loopStart);track.stop();if(track.setPlaybackHeadPosition(p)!=AudioTrack.SUCCESS||track.setLoopPoints(loopStart,loopEnd,-1)!=AudioTrack.SUCCESS)throw new IllegalStateException("Could not restore music position");}
 @Override public void close(){if(closed)return;pause();closed=true;track.release();}
}
