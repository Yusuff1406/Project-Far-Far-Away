package org.shrek2.research;

import java.io.ByteArrayOutputStream;
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
 private static Wave read(InputStream in,boolean allowEmpty)throws IOException {
  ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;
  while((n=in.read(block))!=-1){if(n==0)continue;if(out.size()+n>16*1024*1024)throw new IOException("Could not load or update resources");out.write(block,0,n);}
  byte[] b=out.toByteArray();if(b.length<12||!tag(b,0,"RIFF")||!tag(b,8,"WAVE")||(word(b,4)&0xffffffffL)+8!=b.length)throw new IOException("Could not load or update resources");
  Wave w=new Wave();boolean format=false;
  for(int p=12;p<b.length;){
   if(b.length-p<8)throw new IOException("Could not load or update resources");long size=(word(b,p+4)&0xffffffffL);long end=p+8L+size;if(end>b.length)throw new IOException("Could not load or update resources");
   if(tag(b,p,"fmt ")){if(size<16||word(b,p+8)!=0x00010001||word(b,p+20)!=0x00100002)throw new IOException("Could not load or update resources");w.rate=word(b,p+12);if(w.rate<8000||w.rate>48000||word(b,p+16)!=w.rate*2)throw new IOException("Could not load or update resources");format=true;}
   if(tag(b,p,"data")){if(w.data!=null||(!allowEmpty&&size==0)||(size&1)!=0)throw new IOException("Could not load or update resources");w.data=new byte[(int)size];System.arraycopy(b,p+8,w.data,0,(int)size);}
   long next=end+(size&1);if(next>b.length)throw new IOException("Could not load or update resources");p=(int)next;
  }
  if(!format||w.data==null)throw new IOException("Could not load or update resources");return w;
 }
 static MusicPcm load(InputStream intro,InputStream loop)throws IOException {
  Wave a=read(intro,true),b=read(loop,false);if(a.rate!=b.rate)throw new IOException("Could not load or update resources");byte[] joined=new byte[a.data.length+b.data.length];System.arraycopy(a.data,0,joined,0,a.data.length);System.arraycopy(b.data,0,joined,a.data.length,b.data.length);return new MusicPcm(joined,a.rate,a.data.length/2);
 }
}
