package org.shrek2.research;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.FileOutputStream;

// Experimental single-scene controls. Full original game FSM is not ported.
public final class PrototypeActivity extends Activity {
 static { System.loadLibrary("shrek_scene"); }
 private static native void resetPrototype(int[] state);
 private static native int[] stepAndRender(String scene,String collision,String sprite,int buttons,int[] state);
 private final int[] state=new int[40];
 private final Handler handler=new Handler(Looper.getMainLooper());
 private int buttons=0;
 private String scenePath,collisionPath,spritePath;
 private boolean ready=false;
 private TextView label;
 private GameView view;
 private final Runnable update=new Runnable(){public void run(){
  if(ready){try{int[] pixels=stepAndRender(scenePath,collisionPath,spritePath,buttons,state);view.setPixels(pixels);}catch(Exception e){ready=false;label.setText("Prototype stopped: "+e.getMessage());}}
  handler.postDelayed(this,17);
 }};
 @Override public void onCreate(Bundle saved){
  super.onCreate(saved);if(!RomAccess.require(this))return;LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);label=new TextView(this);label.setText("Prototype: first scene");label.setPadding(12,4,12,4);root.addView(label);
  view=new GameView(this);root.addView(view,new LinearLayout.LayoutParams(-1,0,1));LinearLayout controls=new LinearLayout(this);
  addControl(controls,"◀",32);addControl(controls,"Jump",1);addControl(controls,"▶",16);
  Button restart=new Button(this);restart.setText("Restart");controls.addView(restart);restart.setOnClickListener(v->{buttons=0;resetPrototype(state);});
  Button back=new Button(this);back.setText("Resources");controls.addView(back);back.setOnClickListener(v->finish());root.addView(controls);setContentView(root);
  try{scenePath=copyAsset("scenes/scene_00.s2lv","prototype_scene.s2lv");collisionPath=copyAsset("collision/scene_00.s2cl","prototype_collision.s2cl");spritePath=copyAsset("sprites/shrek_ogre.s2sp","prototype_sprite.s2sp");resetPrototype(state);if(saved!=null){int[] prior=saved.getIntArray("state");if(prior!=null&&prior.length==32)System.arraycopy(prior,0,state,0,32);}ready=true;}catch(Exception e){label.setText("Unable to start prototype: "+e.getMessage());}
 }
 private String copyAsset(String name,String local)throws java.io.IOException{
  File file=new File(getFilesDir(),local);try(InputStream in=getAssets().open(name);OutputStream out=new FileOutputStream(file)){byte[] buffer=new byte[65536];int n;while((n=in.read(buffer))!=-1)out.write(buffer,0,n);}return file.getAbsolutePath();
 }
 private void addControl(LinearLayout row,String text,int mask){
  Button b=new Button(this);b.setText(text);row.addView(b,new LinearLayout.LayoutParams(0,-2,1));b.setOnTouchListener((v,e)->{int action=e.getActionMasked();if(action==MotionEvent.ACTION_DOWN)buttons|=mask;else if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){buttons&=~mask;if(action==MotionEvent.ACTION_UP)v.performClick();}return true;});
 }
 @Override protected void onResume(){super.onResume();if(label==null||!RomAccess.require(this))return;handler.removeCallbacks(update);handler.post(update);}
 @Override protected void onPause(){buttons=0;handler.removeCallbacks(update);super.onPause();}
 @Override protected void onSaveInstanceState(Bundle out){super.onSaveInstanceState(out);out.putIntArray("state",state.clone());}
 private static final class GameView extends View {
  private final Bitmap frame=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);
  private final Paint paint=new Paint();
  GameView(Context c){super(c);paint.setFilterBitmap(false);setContentDescription("Shrek 2 first-scene prototype");}
  void setPixels(int[] pixels){frame.setPixels(pixels,0,240,0,0,240,160);invalidate();}
  @Override protected void onDraw(Canvas canvas){super.onDraw(canvas);canvas.drawColor(0xff181818);float scale=Math.min(getWidth()/240f,getHeight()/160f);int w=Math.round(240*scale),h=Math.round(160*scale),x=(getWidth()-w)/2,y=(getHeight()-h)/2;canvas.drawBitmap(frame,null,new Rect(x,y,x+w,y+h),paint);}
 }
}
