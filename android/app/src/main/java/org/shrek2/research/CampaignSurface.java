package org.shrek2.research;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.Choreographer;
import android.view.MotionEvent;
import android.view.View;

final class CampaignSurface extends View implements Choreographer.FrameCallback {
 final CampaignBrowser browser;
 private final Runnable changed;
 private Bitmap bitmap=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);
 private final Paint paint=new Paint();
 private final TouchButtons inputs=new TouchButtons();
 private int pending=0;
 private boolean running=false;
 private long last=0,elapsed=0;
 private float dragX,dragY;
 CampaignSurface(Context c,CampaignBrowser b,Runnable changed){super(c);browser=b;this.changed=changed;paint.setFilterBitmap(false);setContentDescription("Map and animation browser. Drag to pan.");}
 void refresh(){int width=Viewport.width(getWidth(),getHeight(),true);int[] pixels=browser.pixels(width);if(bitmap.getWidth()!=width){Bitmap old=bitmap;bitmap=Bitmap.createBitmap(width,160,Bitmap.Config.ARGB_8888);old.recycle();}bitmap.setPixels(pixels,0,width,0,0,width,160);invalidate();}
 void resume(){if(running)return;running=true;last=elapsed=0;refresh();Choreographer.getInstance().postFrameCallback(this);}
 void press(int pointer,int mask){inputs.press(pointer,mask);pending|=mask;}
 void release(int pointer){inputs.release(pointer);}
 void clearInput(){inputs.clear();pending=0;browser.input(0);}
 void pause(){clearInput();running=false;last=elapsed=0;Choreographer.getInstance().removeFrameCallback(this);}
 @Override public void doFrame(long time){if(!running)return;try{if(last!=0)elapsed+=Math.min(66666668L,Math.max(0,time-last));last=time;int count=0;while(elapsed>=16666667L&&count<4){elapsed-=16666667L;count++;}for(int i=0;i<count;i++){browser.input(inputs.readForStep()|pending);pending=0;browser.step(1);}refresh();changed.run();}catch(Exception e){pause();setContentDescription(e.getMessage());}if(running)Choreographer.getInstance().postFrameCallback(this);}
 private float scale(){return Math.min(getWidth()/(float)bitmap.getWidth(),getHeight()/160f);}
 @Override protected void onDraw(Canvas c){super.onDraw(c);c.drawColor(0xff181818);float s=scale(),w=bitmap.getWidth()*s,h=160*s,x=(getWidth()-w)/2,y=(getHeight()-h)/2;c.drawBitmap(bitmap,null,new RectF(x,y,x+w,y+h),paint);}
 @Override public boolean onTouchEvent(MotionEvent e){if(browser.info()[0]==2)return true;if(e.getActionMasked()==MotionEvent.ACTION_DOWN){dragX=e.getX();dragY=e.getY();return true;}if(e.getActionMasked()==MotionEvent.ACTION_MOVE){float s=scale();if(s>0){int dx=Math.round((dragX-e.getX())/s),dy=Math.round((dragY-e.getY())/s);browser.pan(Math.max(-16384,Math.min(16384,dx)),Math.max(-16384,Math.min(16384,dy)));dragX-=dx*s;dragY-=dy*s;refresh();changed.run();}return true;}if(e.getActionMasked()==MotionEvent.ACTION_UP){performClick();return true;}return true;}
 @Override public boolean performClick(){super.performClick();return true;}
 @Override protected void onDetachedFromWindow(){pause();super.onDetachedFromWindow();}
}
