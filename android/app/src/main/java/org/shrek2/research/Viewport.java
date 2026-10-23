package org.shrek2.research;

// Square native pixels; extend the world horizontally instead of stretching the art.
public final class Viewport {
 private Viewport(){}
 public static int width(int surfaceWidth,int surfaceHeight,boolean wide){
  if(!wide||surfaceWidth<=0||surfaceHeight<=0)return 240;
  return (int)Math.max(240,Math.min(640,Math.round(surfaceWidth*160.0/surfaceHeight)));
 }
 public static float scale(int surfaceWidth,int surfaceHeight,int frameWidth,boolean fill){
  if(surfaceWidth<=0||surfaceHeight<=0||frameWidth<=0)return 0;
  float x=surfaceWidth/(float)frameWidth,y=surfaceHeight/160f;
  return fill?Math.max(x,y):Math.min(x,y);
 }
}
