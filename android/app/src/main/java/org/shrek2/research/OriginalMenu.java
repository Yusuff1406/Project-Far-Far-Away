package org.shrek2.research;
// Same native frontend is driven by desktop tests and Android touch/key input.
final class OriginalMenu implements AutoCloseable {
 static {System.loadLibrary("shrek_scene");}
 private static native long create(String file,String sprites);
 private static native void destroy(long handle);
 private static native void open(long handle,int page,int cursor);
 private static native void restore(long handle,int[] state);
 private static native void progress(long handle,int[] progress);
 private static native void bonusBests(long handle,int[] scores);
 void bonusBests(int[] scores){bonusBests(handle,scores);}
 private static native void chapterCoins(long handle,int[] counts);
 private static native void step(long handle,int buttons);
 private static native void touch(long handle,int x,int y);
 private static native int action(long handle);
 private static native int sound(long handle);
 private static native int[] snapshot(long handle);
 private static native int[] render(long handle);
 private static native int[] presentation(long handle);
 private static native void testBooks(long h,boolean enabled);
 void testBooks(boolean enabled){testBooks(handle,enabled);}
 private static native void names(long h,String names);
 private static native String initials(long h,int slot);
 void names(String p){names(handle,p);}
 String initials(int slot){return initials(handle,slot);}
 private static native int epilogue(long h,int scene);
 int epilogue(int scene){return epilogue(handle,scene);}
 private static native void startupFade(long handle);
 void startupFade(){startupFade(handle);}
 private long handle;
 OriginalMenu(String file,String sprites){handle=create(file,sprites);if(handle==0)throw new IllegalStateException("Could not load or update resources");}
 void open(int p,int c){open(handle,p,c);}
 void restore(int[] p){restore(handle,p);}
 void progress(int[] p){progress(handle,p);}
 void chapterCoins(int[] p){chapterCoins(handle,p);}
 void step(int b){step(handle,b);}
 void touch(int x,int y){touch(handle,x,y);}
 int action(){return action(handle);}
 int sound(){return sound(handle); }
 int[] state(){return snapshot(handle);}
 int[] presentation(){return presentation(handle);}
 int[] pixels(){return render(handle);}
 public void close(){if(handle!=0){destroy(handle);handle=0;}}
}
