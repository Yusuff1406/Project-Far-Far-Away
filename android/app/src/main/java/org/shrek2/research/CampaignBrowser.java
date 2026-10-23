package org.shrek2.research;

// Map inspection and static traversal, embedded in the existing Activity.
final class CampaignBrowser implements AutoCloseable {
 static {System.loadLibrary("shrek_scene");}
 private static native long create(String root);
 private static native void destroy(long h);
 private static native void command(long h,int command,int a,int b);
 private static native int[] info(long h);
 private static native int[] pixels(long h,int width);
 private static native int[] save(long h);
 private static native void restore(long h,int[] state);
 private static native int[] walkInfo(long h);
 private static native int[] saveWalk(long h);
 private static native void restoreWalk(long h,int[] state);
 private static native boolean canWalk(long h);
 boolean canWalk(){return canWalk(handle);}
 private long handle;
 CampaignBrowser(String root){handle=create(root);if(handle==0)throw new IllegalStateException("Maps unavailable");}
 void select(int scene){command(handle,0,scene,0);}
 void navigate(int delta){command(handle,1,delta,0);}
 void mode(int mode){command(handle,2,mode,0);}
 void bank(int delta){command(handle,3,delta,0);}
 void animation(int delta){command(handle,4,delta,0);}
 void pan(int x,int y){command(handle,5,x,y);}
 void option(int option,int value){command(handle,6,option,value);}
 void input(int held){command(handle,8,held,0);}
 void character(int type){command(handle,9,type,0);}
 void restartWalk(){command(handle,10,0,0);}
 int[] walkInfo(){return walkInfo(handle);}
 int[] saveWalk(){return saveWalk(handle);}
 void restoreWalk(int[] state){restoreWalk(handle,state);}
 void step(int ticks){command(handle,7,ticks,0);}
 int[] info(){return info(handle);}
 int[] pixels(int width){return pixels(handle,width);}
 int[] save(){return save(handle);}
 void restore(int[] state){restore(handle,state);}
 @Override public void close(){if(handle!=0){destroy(handle);handle=0;}}
}
