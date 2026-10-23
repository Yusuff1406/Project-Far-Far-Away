package org.shrek2.research;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Locale;

// Research viewer only: original level art and camera movement, no gameplay.
public final class MainActivity extends Activity {
    static { System.loadLibrary("shrek_scene"); }
    private static native int[] renderScene(String path,int x,int y);
    private static native int[] spriteInfo(String path,int animation);
    private static native int[] renderSprite(String path,int animation,int frame,int flip);
    private static native void advanceAnimation(int rate,int count,int flags,int tick,int[] state);
    private static native int[] renderCollision(String path,int x,int y);
    private String collisionPath;
    private boolean showGeometry=false;
    private String spritePath;
    private int animation=0,flip=0,previewTick=0;
    private int[] animationInfo,animationState;
    private final android.os.Handler handler=new android.os.Handler(android.os.Looper.getMainLooper());
    private final Runnable animate=new Runnable(){public void run(){
        if(animationInfo!=null&&animationState!=null){try{
            if(animationState[0]==0)advanceAnimation(animationInfo[2],animationInfo[1],animationInfo[3],++previewTick,animationState);
            sceneView.refreshActor();
        }catch(Exception e){label.setText("Animation failed: "+e.getMessage());}}
        handler.postDelayed(this,17); // Preview clock; original game scheduler not ported.
    }};
    private int scene=0,cameraX=0,cameraY=0,worldWidth=240,worldHeight=160;
    private String scenePath;
    private TextView label;
    private SceneView sceneView;
    @Override public void onCreate(Bundle state){
        super.onCreate(state);if(!RomAccess.require(this))return;
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        LinearLayout controls=new LinearLayout(this);
        Button prev=new Button(this);prev.setText("◀");controls.addView(prev);
        label=new TextView(this);label.setTextColor(0xffffffff);label.setPadding(16,8,16,8);controls.addView(label,new LinearLayout.LayoutParams(0,-2,1));
        Button next=new Button(this);next.setText("▶");controls.addView(next);
        Button animPrev=new Button(this);animPrev.setText("A◀");controls.addView(animPrev);
        Button animNext=new Button(this);animNext.setText("A▶");controls.addView(animNext);
        Button facing=new Button(this);facing.setText("⇄");controls.addView(facing);
        animPrev.setOnClickListener(v->selectAnimation((animation+25)%26));animNext.setOnClickListener(v->selectAnimation((animation+1)%26));facing.setOnClickListener(v->{flip=1-flip;sceneView.refreshActor();});
        Button geometry=new Button(this);geometry.setText("Geometry");controls.addView(geometry);geometry.setOnClickListener(v->{showGeometry=!showGeometry;sceneView.refresh();});
        Button play=new Button(this);play.setText("Play prototype");controls.addView(play);play.setOnClickListener(v->startActivity(new android.content.Intent(this,PrototypeActivity.class)));
        LinearLayout playRow=new LinearLayout(this);Button sessionPlay=new Button(this);sessionPlay.setText("Item demo");playRow.addView(sessionPlay,new LinearLayout.LayoutParams(0,-2,1));sessionPlay.setOnClickListener(v->startActivity(new android.content.Intent(this,SessionActivity.class)));
        Button worldPlay=new Button(this);worldPlay.setText("Level objects");playRow.addView(worldPlay,new LinearLayout.LayoutParams(0,-2,1));worldPlay.setOnClickListener(v->startActivity(new android.content.Intent(this,SessionActivity.class).putExtra("world",true)));
        root.addView(controls);root.addView(playRow);sceneView=new SceneView(this);root.addView(sceneView,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);
        prev.setOnClickListener(v->selectScene((scene+29)%30));next.setOnClickListener(v->selectScene((scene+1)%30));
        if(state!=null)scene=state.getInt("scene",0);
        selectScene(scene);
        try{File file=new File(getFilesDir(),"shrek_ogre.s2sp");try(InputStream in=getAssets().open("sprites/shrek_ogre.s2sp");OutputStream out=new FileOutputStream(file)){byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);}spritePath=file.getAbsolutePath();selectAnimation(0);}catch(Exception e){label.setText("Sprite load failed: "+e.getMessage());}
    }
    @Override protected void onSaveInstanceState(Bundle out){super.onSaveInstanceState(out);out.putInt("scene",scene);}
    @Override protected void onResume(){super.onResume();if(label==null||!RomAccess.require(this))return;handler.removeCallbacks(animate);handler.post(animate);}
    @Override protected void onPause(){handler.removeCallbacks(animate);super.onPause();}
    private void selectAnimation(int number){if(spritePath==null)return;try{animation=number;animationInfo=spriteInfo(spritePath,animation);previewTick=0;animationState=new int[]{0,0,0,animationInfo[2]+1};sceneView.refreshActor();}catch(Exception e){label.setText("Animation selection failed: "+e.getMessage());}}
    private void selectScene(int number){
        scene=number;
        try{
            String name=String.format(Locale.ROOT,"scene_%02d.s2lv",scene);File file=new File(getFilesDir(),name);
            // Always refresh cached data after replacing the application assets.
            try(InputStream in=getAssets().open("scenes/"+name);OutputStream out=new FileOutputStream(file)){byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);}
            byte[] header=new byte[28];try(InputStream in=new java.io.FileInputStream(file)){int off=0;while(off<header.length){int n=in.read(header,off,header.length-off);if(n<0)throw new java.io.IOException("Truncated scene");off+=n;}}
            ByteBuffer b=ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN);worldWidth=b.getInt(8);worldHeight=b.getInt(12);
            File collisionFile=new File(getFilesDir(),String.format(Locale.ROOT,"scene_%02d.s2cl",scene));try(InputStream in=getAssets().open(String.format(Locale.ROOT,"collision/scene_%02d.s2cl",scene));OutputStream out=new FileOutputStream(collisionFile)){byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);}collisionPath=collisionFile.getAbsolutePath();
            scenePath=file.getAbsolutePath();cameraX=0;cameraY=Math.max(0,worldHeight-160);sceneView.refresh();
        }catch(Exception e){scenePath=null;label.setText("Unable to open scene: "+e.getMessage());}
    }
    private final class SceneView extends View {
        private final Bitmap bitmap=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);
        private final Bitmap geometryBitmap=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);
        private final Bitmap actor=Bitmap.createBitmap(160,160,Bitmap.Config.ARGB_8888);
        private final Paint paint=new Paint();private float lastX,lastY,scale=1;
        SceneView(Context c){super(c);paint.setFilterBitmap(false);setContentDescription("Level resource viewer; drag to move camera");}
        void refresh(){if(scenePath==null)return;try{int[] pixels=renderScene(scenePath,cameraX,cameraY);bitmap.setPixels(pixels,0,240,0,0,240,160);if(showGeometry&&collisionPath!=null){int[] lines=renderCollision(collisionPath,cameraX,cameraY);geometryBitmap.setPixels(lines,0,240,0,0,240,160);}label.setText(String.format(Locale.ROOT,"Resources • %02d / 30 • camera %d, %d",scene+1,cameraX,cameraY));invalidate();}catch(Exception e){label.setText("Render failed: "+e.getMessage());}}
        void refreshActor(){if(spritePath==null||animationState==null)return;int[] pixels=renderSprite(spritePath,animation,animationState[2],flip);actor.setPixels(pixels,0,160,0,0,160,160);label.setText(String.format(Locale.ROOT,"Scene %02d • animation %02d • frame %d",scene+1,animation,animationState[2]));invalidate();}
        @Override protected void onDraw(Canvas c){super.onDraw(c);c.drawColor(0xff181818);scale=Math.min(getWidth()/240f,getHeight()/160f);int w=Math.round(240*scale),h=Math.round(160*scale);int x=(getWidth()-w)/2,y=(getHeight()-h)/2;c.drawBitmap(bitmap,null,new Rect(x,y,x+w,y+h),paint);if(showGeometry&&collisionPath!=null)c.drawBitmap(geometryBitmap,null,new Rect(x,y,x+w,y+h),paint);if(spritePath!=null)c.drawBitmap(actor,null,new Rect(x+Math.round(40*scale),y-Math.round(10*scale),x+Math.round(200*scale),y+Math.round(150*scale)),paint);}
        @Override public boolean onTouchEvent(MotionEvent event){
            if(event.getAction()==MotionEvent.ACTION_DOWN){lastX=event.getX();lastY=event.getY();return true;}
            if(event.getAction()==MotionEvent.ACTION_MOVE){cameraX=Math.max(0,Math.min(Math.max(0,worldWidth-240),cameraX+Math.round((lastX-event.getX())/scale)));cameraY=Math.max(0,Math.min(Math.max(0,worldHeight-160),cameraY+Math.round((lastY-event.getY())/scale)));lastX=event.getX();lastY=event.getY();refresh();return true;}
            if(event.getAction()==MotionEvent.ACTION_UP){performClick();return true;}return true;
        }
        @Override public boolean performClick(){super.performClick();return true;}
    }
}
