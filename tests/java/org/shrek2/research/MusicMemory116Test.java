package org.shrek2.research;

import java.io.*;
import java.nio.file.*;
import java.util.*;

// Exercise the real parser on short-read streams and a bounded small heap.
public final class MusicMemory116Test {
 static int checks;
 static void check(boolean ok){if(!ok)throw new AssertionError("check "+checks);checks++;}
 static void put(byte[] b,int p,int v){for(int i=0;i<4;i++)b[p+i]=(byte)(v>>>(8*i));}
 static byte[] header(int size){byte[] b=new byte[44];System.arraycopy("RIFF".getBytes(),0,b,0,4);put(b,4,size+36);System.arraycopy("WAVEfmt ".getBytes(),0,b,8,8);put(b,16,16);put(b,20,0x10001);put(b,24,31537);put(b,28,63074);put(b,32,0x100002);System.arraycopy("data".getBytes(),0,b,36,4);put(b,40,size);return b;}
 static InputStream wave(int size){
  return new SequenceInputStream(new ByteArrayInputStream(header(size)),new InputStream(){int left=size;public int read(){return left-- >0?90:-1;}public int read(byte[] b,int off,int n){if(left==0)return -1;n=Math.min(left,n);Arrays.fill(b,off,off+n,(byte)90);left-=n;return n;}});
 }
 static InputStream fragmented(byte[] bytes){return new FilterInputStream(new ByteArrayInputStream(bytes)){int calls;public int read(byte[] b,int off,int n)throws IOException{if(++calls%5==0)return 0;return super.read(b,off,Math.min(7,n));}public long skip(long n){return 0;}};}
 static void reject(byte[] intro,byte[] loop)throws Exception{try{MusicPcm.load(fragmented(intro),fragmented(loop));throw new AssertionError("accepted damaged WAV");}catch(IOException expected){checks++;}}
 public static void main(String[] args)throws Exception {
  if(args.length==0){
   MusicPcm p=MusicPcm.load(wave(0),wave(12*1024*1024));
   check(p.pcm.length==12*1024*1024&&p.loopStartFrames==0&&p.sampleRate==31537);
   for(byte b:p.pcm)if(b!=90)throw new AssertionError("PCM mismatch");
   System.out.println("PASS 12 MiB PCM under 32 MiB heap; samples unchanged");return;
  }
  int files=0;
  try(java.util.stream.Stream<Path> paths=Files.walk(Paths.get(args[0]))){
   for(Path path:(Iterable<Path>)paths.filter(p->p.toString().endsWith("_intro.wav"))::iterator){
    Path loop=Paths.get(path.toString().replace("_intro.wav","_loop.wav"));if(!Files.exists(loop))continue;
    byte[] a=Files.readAllBytes(path),b=Files.readAllBytes(loop);
    MusicPcm p=MusicPcm.load(fragmented(a),fragmented(b));
    check(p.pcm.length==a.length+b.length-88&&p.loopStartFrames==(a.length-44)/2);
    for(int i=44;i<a.length;i++)if(p.pcm[i-44]!=a[i])throw new AssertionError(path+" intro PCM");
    for(int i=44;i<b.length;i++)if(p.pcm[a.length-44+i-44]!=b[i])throw new AssertionError(loop+" loop PCM");
    files++;
   }
  }
  check(files>0);
  byte[] empty=header(0),valid=Arrays.copyOf(header(4),48);Arrays.fill(valid,44,48,(byte)90);
  reject(empty,empty);reject(empty,Arrays.copyOf(valid,47));
  byte[] bad=valid.clone();bad[22]=2;reject(empty,bad);
  bad=valid.clone();bad[34]=8;reject(empty,bad);
  bad=valid.clone();put(bad,4,Integer.MAX_VALUE);reject(empty,bad);
  bad=Arrays.copyOf(valid,49);reject(empty,bad);
  bad=valid.clone();put(bad,40,3);reject(empty,bad);
  bad=valid.clone();put(bad,24,8000);put(bad,28,16000);reject(empty,bad);
  // Unknown odd-sized chunks include one pad byte; data need not follow fmt.
  ByteArrayOutputStream extra=new ByteArrayOutputStream();extra.write(valid,0,12);extra.write("JUNK".getBytes());extra.write(new byte[]{1,0,0,0,7,0});extra.write(valid,12,36);byte[] padded=extra.toByteArray();put(padded,4,padded.length-8);
  MusicPcm paddedPcm=MusicPcm.load(fragmented(empty),fragmented(padded));check(paddedPcm.pcm.length==4&&paddedPcm.pcm[0]==90);
  reject(empty,Arrays.copyOf(padded,padded.length-1));
  extra.reset();extra.write(valid,0,12);extra.write(valid,36,12);extra.write(valid,12,24);byte[] reordered=extra.toByteArray();
  check(MusicPcm.load(fragmented(empty),fragmented(reordered)).pcm.length==4);
  System.out.println("PASS "+files+" music pairs, all PCM bytes and loop markers; "+checks+" parser checks");
 }
}
