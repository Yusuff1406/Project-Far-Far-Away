package org.shrek2.research;

import java.io.*;
import java.nio.file.*;
import java.security.*;

/** Exact original resource source; never trust a filename or a saved boolean. */
final class RomStore {
 static final String TITLE="Shrek 2 (USA, Europe)";
 static final long SIZE=8388608L;
 static final String SHA256="2ec32cb8c69ff8bbe01b7039ee001105f92ee686b251d26060f9bdb6751f3b80";
 static File file(File files){return new File(new File(files,"rom"),"original.gba");}
 private static String digest(InputStream in,OutputStream out)throws IOException {
  MessageDigest md;try{md=MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new IOException("SHA-256 unavailable",e);}
  byte[]buffer=new byte[65536];long count=0;int n;
  while((n=in.read(buffer))!=-1){if(n==0)continue;count+=n;if(count>SIZE)throw new IOException("Wrong ROM size. Select the uncompressed original .gba file (8 MiB).");md.update(buffer,0,n);if(out!=null)out.write(buffer,0,n);}
  if(count!=SIZE)throw new IOException("Wrong ROM size. Expected an uncompressed 8 MiB .gba file.");
  StringBuilder hex=new StringBuilder(64);for(byte b:md.digest())hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return hex.toString();
 }
 static synchronized boolean valid(File files){
  File rom=file(files);if(!rom.isFile()||rom.length()!=SIZE)return false;
  try(InputStream in=new FileInputStream(rom)){return SHA256.equals(digest(in,null));}catch(IOException|SecurityException e){return false;}
 }
 static synchronized void importRom(File files,InputStream in)throws IOException {
  if(in==null)throw new IOException("Could not open the selected file.");
  File destination=file(files),folder=destination.getParentFile();if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Could not create ROM storage.");
  File temp=File.createTempFile("import_",".tmp",folder);
  try {
   String actual;try(FileOutputStream out=new FileOutputStream(temp)){actual=digest(in,out);out.getFD().sync();}
   if(!SHA256.equals(actual))throw new IOException("ROM hash does not match. Use the unmodified "+TITLE+" release.\nSelected SHA-256: "+actual);
   try{Files.move(temp.toPath(),destination.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}catch(AtomicMoveNotSupportedException e){Files.move(temp.toPath(),destination.toPath(),StandardCopyOption.REPLACE_EXISTING);}
  }finally{Files.deleteIfExists(temp.toPath());}
 }
}
