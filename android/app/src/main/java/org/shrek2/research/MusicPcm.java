package org.shrek2.research;

import java.io.IOException;
import java.io.InputStream;

// One continuous intro+loop buffer. Loop markers are PCM frames, never WAV bytes.
final class MusicPcm {
 final byte[] pcm;
 final int sampleRate,loopStartFrames,loopEndFrames;
 private MusicPcm(byte[] pcm,int rate,int start){this.pcm=pcm;sampleRate=rate;loopStartFrames=start;loopEndFrames=pcm.length/2;}
 private static int word(byte[] b,int p){return (b[p]&255)|((b[p+1]&255)<<8)|((b[p+2]&255)<<16)|((b[p+3]&255)<<24);}
 private static boolean tag(byte[] b,int p,String name){for(int i=0;i<4;i++)if((b[p+i]&255)!=name.charAt(i))return false;return true;}
 private static final class Wave {byte[] data;int rate;}
 private static void readFully(InputStream in,byte[] b,int size)throws IOException {
  for(int p=0;p<size;){int n=in.read(b,p,size-p);if(n<0)throw new IOException("Could not load or update resources");if(n==0){int one=in.read();if(one<0)throw new IOException("Could not load or update resources");b[p++]=(byte)one;}else p+=n;}
 }
 private static void discard(InputStream in,int size,byte[] scratch)throws IOException {
  while(size>0){int n=Math.min(size,scratch.length);readFully(in,scratch,n);size-=n;}
 }
 private static Wave read(InputStream in,boolean allowEmpty)throws IOException {
  // Read PCM directly into its final chunk buffer. Avoid retaining a growing
  // whole-file buffer, its flattened copy and another PCM copy on small heaps.
  byte[] b=new byte[16],scratch=new byte[8192];readFully(in,b,12);
  long length=(word(b,4)&0xffffffffL)+8;
  if(!tag(b,0,"RIFF")||!tag(b,8,"WAVE")||length<12||length>16*1024*1024)throw new IOException("Could not load or update resources");
  Wave w=new Wave();boolean format=false;
  for(long p=12;p<length;){
   if(length-p<8)throw new IOException("Could not load or update resources");readFully(in,b,8);
   long size=word(b,4)&0xffffffffL,next=p+8+size+(size&1);
   if(next>length)throw new IOException("Could not load or update resources");
   boolean fmt=tag(b,0,"fmt "),data=tag(b,0,"data");
   if(fmt){if(size<16)throw new IOException("Could not load or update resources");readFully(in,b,16);if(word(b,0)!=0x00010001||word(b,12)!=0x00100002)throw new IOException("Could not load or update resources");w.rate=word(b,4);if(w.rate<8000||w.rate>48000||word(b,8)!=w.rate*2)throw new IOException("Could not load or update resources");format=true;discard(in,(int)size-16,scratch);}
   else if(data){if(w.data!=null||(!allowEmpty&&size==0)||(size&1)!=0)throw new IOException("Could not load or update resources");w.data=new byte[(int)size];readFully(in,w.data,(int)size);}
   else discard(in,(int)size,scratch);
   if((size&1)!=0)readFully(in,b,1);p=next;
  }
  if(!format||w.data==null||in.read()!=-1)throw new IOException("Could not load or update resources");return w;
 }
 static MusicPcm load(InputStream intro,InputStream loop)throws IOException {
  Wave a=read(intro,true),b=read(loop,false);if(a.rate!=b.rate)throw new IOException("Could not load or update resources");byte[] joined=new byte[a.data.length+b.data.length];System.arraycopy(a.data,0,joined,0,a.data.length);System.arraycopy(b.data,0,joined,a.data.length,b.data.length);return new MusicPcm(joined,a.rate,a.data.length/2);
 }
}
