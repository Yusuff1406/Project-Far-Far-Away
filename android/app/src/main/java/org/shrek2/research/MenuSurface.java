package org.shrek2.research;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.Choreographer;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
final class MenuSurface extends View implements Choreographer.FrameCallback {
 interface Listener{void action(int action,int[] state);}
 final OriginalMenu menu;private final Listener listener;private SessionAudio audio;private final Bitmap bitmap=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);private final Paint paint=new Paint();private long last=0,elapsed=0;private boolean running=false;private float downX,downY;boolean overlay=false;private int fadeAlpha=0;private Runnable changed;
 private int heldButtons=0;private boolean directTouch=false;void touchEnabled(boolean enabled){directTouch=enabled;}
 void held(int mask,boolean down){heldButtons=down?heldButtons|mask:heldButtons&~mask;menu.step(heldButtons);dispatch();refresh();}
 void onChanged(Runnable r){changed=r;}
 MenuSurface(Context c,OriginalMenu m,Listener l){super(c);menu=m;listener=l;paint.setFilterBitmap(false);setFocusableInTouchMode(true);setContentDescription("Project Far Far Away menu. Use touch, directions and A/B.");}
 void audio(SessionAudio a){audio=a;}
 void resume(){if(running)return;running=true;last=elapsed=0;Choreographer.getInstance().postFrameCallback(this);refresh();}
 void releaseButtons(){heldButtons=0;menu.step(0);}
 void pause(){releaseButtons();running=false;last=elapsed=0;Choreographer.getInstance().removeFrameCallback(this);}
 void refresh(){if(changed!=null)changed.run();if(audio!=null&&!overlay){int[] state=menu.state();audio.setFrontendCredits(state[0]==8);audio.setFrontendEpilogue(state[0]==14?state[2]:-1);}fadeAlpha=menu.presentation()[2];bitmap.setPixels(menu.pixels(),0,240,0,0,240,160);invalidate();}
 void press(int mask){menu.step(mask);menu.step(0);dispatch();refresh();}
 private void dispatch(){int sound=menu.sound();if(sound>0&&audio!=null)audio.play(sound,sound==100?0:-100,sound==100?256:200);int action=menu.action();if(action!=0)listener.action(action,menu.state());}
 @Override public void doFrame(long time){if(!running)return;if(last!=0)elapsed+=Math.min(66666668L,Math.max(0,time-last));last=time;int count=0;while(elapsed>=16666667L&&count++<4){menu.step(heldButtons);dispatch();elapsed-=16666667L;}if(count>0)refresh();if(running)Choreographer.getInstance().postFrameCallback(this);}
 private float scale(){return Math.min(getWidth()/240f,getHeight()/160f);}
 @Override protected void onDraw(Canvas c){super.onDraw(c);if(!overlay)c.drawColor(0xff000000);else if(fadeAlpha>0)c.drawColor((fadeAlpha*255/64)<<24);float s=scale(),x=(getWidth()-240*s)/2,y=(getHeight()-160*s)/2;c.drawBitmap(bitmap,null,new RectF(x,y,x+240*s,y+160*s),paint);}
 @Override public boolean onTouchEvent(MotionEvent e){if(!directTouch)return true;if(e.getActionMasked()==MotionEvent.ACTION_DOWN){downX=e.getX();downY=e.getY();return true;}if(e.getActionMasked()==MotionEvent.ACTION_UP){if(Math.abs(e.getX()-downX)<32&&Math.abs(e.getY()-downY)<32){float s=scale();if(s>0){int x=(int)Math.floor((e.getX()-(getWidth()-240*s)/2)/s),y=(int)Math.floor((e.getY()-(getHeight()-160*s)/2)/s);if(x>=0&&x<240&&y>=0&&y<160){menu.touch(x,y);dispatch();refresh();}}}performClick();return true;}return true;}
 @Override public boolean performClick(){super.performClick();return true;}
 @Override protected void onDetachedFromWindow(){pause();super.onDetachedFromWindow();}
}
