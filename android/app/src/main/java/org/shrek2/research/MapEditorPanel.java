package org.shrek2.research;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Paused live scene editor. Touch drag previews; only release commits an edit. */
final class MapEditorPanel extends FrameLayout implements android.view.Choreographer.FrameCallback {
 interface Host {int[] info();int[] entities();int[] thumbnail(int type);void frame(int w,int x,int y,int[] out);void preview(int w,int h,int x,int y,int id,int px,int py,int[]out);int edit(int cmd,int a,int b,int c);void undo();void save();void reset();void close();}
 private final Host host;
 final MapView map;
 private final TextView status;
 private final Button modeButton,deleteButton,duplicateButton,stepButton,zoomButton;
 private int[] entities=new int[0];
 private final java.util.Map<Integer,Bitmap> thumbnails=new java.util.HashMap<>();
 int cameraX,cameraY,selected=0,placeType=0,step=8;
 float zoom=1f;boolean pan=true;private int held=0;private long repeatAt=0;
 private int worldWidth,worldHeight;
 private static final int[] TYPES={13,14,15,16,17,10,18,52,53,54,55,56,57,58,59,60,61,62,76,77,78,79,80,81,82,83,84,85,89};
 private static final String[] NAMES={"Crate","Stump","Crate variant","Mushroom","Spring","Breakable floor","Branch","Witch spawner","Pumpkin","Archer","Axe guard","Axe guard variant","Red enemy","Red enemy variant","Armored knight","Shield knight","Flying pumpkin","Flying pumpkin variant","Key","Apple","Flight fairy","Banana","Shield","Invisibility","Clover","Potion","Flask","Heart jar","Coin"};
 MapEditorPanel(Context context,Host host){super(context);this.host=host;setBackgroundColor(0xff181818);int[]a=host.info();worldWidth=a[8];worldHeight=a[9];cameraX=Math.max(0,a[2]-120);cameraY=Math.max(0,a[3]-80);
  map=new MapView(context);FrameLayout.LayoutParams area=new FrameLayout.LayoutParams(-1,-1);area.topMargin=dp(86);area.bottomMargin=dp(52);addView(map,area);
  LinearLayout top=new LinearLayout(context);top.setOrientation(LinearLayout.VERTICAL);LinearLayout row=new LinearLayout(context);top.addView(row);
  button(row,"Back",host::close);modeButton=button(row,"Pan",()->{pan=!pan;placeType=0;update();});button(row,"Add",this::addPicker);duplicateButton=button(row,"Copy",this::duplicate);deleteButton=button(row,"Delete",()->{if(selected>0&&host.edit(5,selected,0,0)>=0){selected=0;refresh();}});button(row,"Undo",()->{host.undo();refresh();});button(row,"Save",host::save);button(row,"Reset",()->{host.reset();selected=0;refresh();});
  status=new TextView(context);status.setTextSize(11);status.setTextColor(0xffffffff);status.setPadding(dp(8),0,dp(8),0);top.addView(status);addView(top,new FrameLayout.LayoutParams(-1,-2,Gravity.TOP));
  LinearLayout bottom=new LinearLayout(context);direction(bottom,"←",32);direction(bottom,"↑",64);direction(bottom,"↓",128);direction(bottom,"→",16);button(bottom,"Objects",this::objectPicker);button(bottom,"Center",this::center);stepButton=button(bottom,"Step 8",()->{step=step==1?8:step==8?32:1;update();});button(bottom,"−",()->zoomBy(1/1.5f));zoomButton=button(bottom,"1×",()->setZoom(1f));button(bottom,"+",()->zoomBy(1.5f));addView(bottom,new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM));refresh();
 }
 private int dp(int n){return Math.round(n*getContext().getResources().getDisplayMetrics().density);}
 private Button button(LinearLayout row,String text,Runnable action){Button b=new Button(getContext());b.setText(text);b.setTextSize(11);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(2,0,2,0);row.addView(b,new LinearLayout.LayoutParams(0,-2,1f));b.setOnClickListener(v->action.run());return b;}
 private void direction(LinearLayout row,String label,int mask){Button b=button(row,label,()->nudge(mask==32?-1:mask==16?1:0,mask==64?-1:mask==128?1:0));b.setOnTouchListener((v,e)->{int a=e.getActionMasked();if(a==MotionEvent.ACTION_DOWN)input(mask,true);else if(a==MotionEvent.ACTION_UP||a==MotionEvent.ACTION_CANCEL)input(mask,false);return true;});}
 void releaseInput(){if(map!=null)map.cancelGesture();held=0;repeatAt=0;android.view.Choreographer.getInstance().removeFrameCallback(this);}
 @Override public void doFrame(long time){if(held==0)return;if(repeatAt==0)repeatAt=time+250000000L;if(time>=repeatAt){nudge(((held&16)!=0?1:0)-((held&32)!=0?1:0),((held&128)!=0?1:0)-((held&64)!=0?1:0));repeatAt=time+80000000L;}android.view.Choreographer.getInstance().postFrameCallback(this);}
 private String name(int type){if(type>=3&&type<=7)return new String[]{"Shrek","Puss in Boots","Gingy","Donkey","Human Shrek"}[type-3];for(int i=0;i<TYPES.length;i++)if(TYPES[i]==type)return NAMES[i];return "Object "+type;}
 private int at(int id){for(int i=0;i<entities.length;i+=6)if(entities[i]==id)return i;return -1;}
 private Bitmap thumbnail(int type){Bitmap b=thumbnails.get(type);if(b==null){int[] pixels=host.thumbnail(type);b=Bitmap.createBitmap(64,64,Bitmap.Config.ARGB_8888);b.setPixels(pixels,0,64,0,0,64,64);thumbnails.put(type,b);}return b;}
 private void palette(String title,int[] types,String[] labels,java.util.function.IntConsumer choose){
  android.widget.ScrollView scroll=new android.widget.ScrollView(getContext());LinearLayout grid=new LinearLayout(getContext());grid.setOrientation(LinearLayout.VERTICAL);grid.setPadding(dp(6),dp(6),dp(6),dp(6));scroll.addView(grid);
  final android.app.AlertDialog[] dialog=new android.app.AlertDialog[1];
  for(int base=0;base<types.length;base+=3){LinearLayout row=new LinearLayout(getContext());grid.addView(row);for(int column=0;column<3;column++){int i=base+column;LinearLayout card=new LinearLayout(getContext());card.setOrientation(LinearLayout.VERTICAL);card.setPadding(dp(4),dp(4),dp(4),dp(4));card.setBackgroundColor(0xff29343b);LinearLayout.LayoutParams cell=new LinearLayout.LayoutParams(0,dp(108),1f);cell.setMargins(dp(3),dp(3),dp(3),dp(3));row.addView(card,cell);if(i>=types.length){card.setVisibility(View.INVISIBLE);continue;}
   Bitmap preview=thumbnail(types[i]);View icon=new View(getContext()){final Paint p=new Paint();final RectF r=new RectF();@Override protected void onDraw(Canvas c){super.onDraw(c);float side=Math.min(getWidth(),getHeight());r.set((getWidth()-side)/2,0,(getWidth()+side)/2,side);c.drawBitmap(preview,null,r,p);}};card.addView(icon,new LinearLayout.LayoutParams(-1,dp(64)));TextView label=new TextView(getContext());label.setText(labels[i]);label.setTextSize(11);label.setTextColor(0xffffffff);label.setGravity(Gravity.CENTER);card.addView(label,new LinearLayout.LayoutParams(-1,-2));card.setContentDescription(labels[i]);final int index=i;card.setOnClickListener(v->{choose.accept(index);dialog[0].dismiss();});
  }}dialog[0]=new android.app.AlertDialog.Builder(getContext()).setTitle(title).setView(scroll).setNegativeButton("Cancel",(d,i)->{}).show();
 }
 private void addPicker(){palette("Add object · choose, then tap map",TYPES,NAMES,i->{placeType=TYPES[i];pan=false;update();});}
 void duplicate(){int i=at(selected);if(i<0||selected<=0)return;int offset=Math.max(step,entities[i+4]+8),x=entities[i+2]+offset,y=entities[i+3];if(x>=worldWidth)x=Math.max(0,entities[i+2]-offset);int result=host.edit(11,selected,x,y);if(result>=0){selected=result;pan=false;placeType=0;map.cancelGesture();refresh();center();}}

 private void objectPicker(){String[]labels=new String[entities.length/6];int[]types=new int[labels.length],ids=new int[labels.length];for(int i=0;i<labels.length;i++){types[i]=entities[i*6+1];ids[i]=entities[i*6];labels[i]=name(types[i])+(ids[i]<0?" · character":" #"+ids[i]);}palette("Select and center",types,labels,i->{selected=ids[i];pan=false;placeType=0;center();});}
 void refresh(){entities=host.entities();if(at(selected)<0)selected=0;map.refresh();update();}
 private void update(){modeButton.setText(pan?"Pan":"Move");stepButton.setText("Step "+step);zoomButton.setText(String.format(java.util.Locale.ROOT,"%.1f×",zoom));deleteButton.setEnabled(selected>0);duplicateButton.setEnabled(selected>0);int i=at(selected);status.setText(placeType!=0?"Tap map to place "+name(placeType):pan?"Drag to pan · Objects selects and centers · arrows pan the map":(i<0?"Tap an object or character":"Selected: "+name(entities[i+1]))+" · drag or tap destination · pinch to zoom · blank drag pans");map.invalidate();}
 void zoomBy(float multiplier){setZoom(zoom*multiplier);}
 void setZoom(float value){zoomAt(value,map.getWidth()/2f,map.getHeight()/2f);}
 private void zoomAt(float value,float screenX,float screenY){float wx=cameraX+(screenX-map.left())/map.scale(),wy=cameraY+(screenY-map.top())/map.scale();zoom=Math.max(.5f,Math.min(4f,value));map.resize();cameraX=Math.round(wx-(screenX-map.left())/map.scale());cameraY=Math.round(wy-(screenY-map.top())/map.scale());clamp();map.refresh();update();}
 private void clamp(){cameraX=Math.max(0,Math.min(Math.max(0,worldWidth-map.width),cameraX));cameraY=Math.max(0,Math.min(Math.max(0,worldHeight-map.height),cameraY));}
 private void center(){int i=at(selected);int[]a=host.info();cameraX=(i<0?a[2]:entities[i+2])-map.width/2;cameraY=(i<0?a[3]:entities[i+3])-map.height/2;clamp();map.refresh();update();}
 void nudge(int dx,int dy){int i=at(selected);if(!pan&&placeType==0&&i>=0){move(selected,entities[i+2]+dx*step,entities[i+3]+dy*step);}else{cameraX+=dx*32;cameraY+=dy*32;clamp();map.refresh();}}
 private void move(int id,int x,int y){x=Math.max(0,Math.min(worldWidth-1,x));y=Math.max(0,Math.min(worldHeight-1,y));if(host.edit(id<0?10:8,id<0?-id-1:id,x,y)>=0)refresh();}
 void input(int mask,boolean down){if((mask&240)!=0){if(down){held|=mask;android.view.Choreographer.getInstance().postFrameCallback(this);}else{held&=~mask;if(held==0)releaseInput();return;}}else if(!down)return;if(mask==32)nudge(-1,0);else if(mask==16)nudge(1,0);else if(mask==64)nudge(0,-1);else if(mask==128)nudge(0,1);else if(mask==2||mask==8)host.close();else if(mask==1){if(placeType!=0)place(cameraX+map.width/2,cameraY+map.height/2);else{pan=!pan;update();}}}
 private void place(int x,int y){if(placeType==0)return;int result=host.edit(4,placeType,Math.max(0,Math.min(worldWidth-1,x)),Math.max(0,Math.min(worldHeight-1,y)));if(result>=0){selected=result;placeType=0;pan=false;refresh();}}
 void dispose(){releaseInput();map.bitmap.recycle();for(Bitmap b:thumbnails.values())b.recycle();thumbnails.clear();}
 final class MapView extends View {
  int width=240,height=160;Bitmap bitmap=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);int[] pixels=new int[240*160];final Paint paint=new Paint(),marker=new Paint();final RectF destination=new RectF();float lastX,lastY,startX,startY,offsetX,offsetY,ghostX,ghostY,lastSpan=0;int tapSelect=0;boolean dragObject=false,moved=false,tapPlace=false,multi=false;
  MapView(Context c){super(c);paint.setFilterBitmap(false);marker.setColor(0xffffd54f);marker.setStyle(Paint.Style.STROKE);marker.setStrokeWidth(2);setContentDescription("Map editor: tap an object, drag it or tap its destination. Pinch or use zoom buttons.");}
  void cancelGesture(){dragObject=false;tapPlace=false;tapSelect=0;multi=false;lastSpan=0;moved=false;}
  void resize(){int w=Math.max(60,Math.min(1280,Math.round(Viewport.width(getWidth(),getHeight(),true)/zoom))),h=Math.max(40,Math.min(640,Math.round(160/zoom)));if(width!=w||height!=h){width=w;height=h;bitmap.recycle();bitmap=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);pixels=new int[w*h];}}
  void refresh(){resize();clamp();host.preview(width,height,cameraX,cameraY,dragObject?selected:0,Math.round(ghostX),Math.round(ghostY),pixels);bitmap.setPixels(pixels,0,width,0,0,width,height);invalidate();}
  float scale(){return Math.max(.01f,Math.min(getWidth()/(float)width,getHeight()/(float)height));}float left(){return (getWidth()-width*scale())/2;}float top(){return (getHeight()-height*scale())/2;}
  int hit(float x,float y){int best=0;float distance=Float.MAX_VALUE;for(int i=0;i<entities.length;i+=6){float dx=Math.abs(x-entities[i+2]),dy=Math.abs(y-entities[i+3]);if(dx>Math.max(8,entities[i+4]/2f)||dy>Math.max(8,entities[i+5]/2f))continue;float d=dx*dx+dy*dy;if(d<distance){distance=d;best=entities[i];}}return best;}
  @Override protected void onSizeChanged(int w,int h,int oldw,int oldh){super.onSizeChanged(w,h,oldw,oldh);if(w>0&&h>0)refresh();}
  @Override protected void onDraw(Canvas c){super.onDraw(c);c.drawColor(0xff181818);float s=scale(),l=left(),t=top();destination.set(l,t,l+width*s,t+height*s);c.drawBitmap(bitmap,null,destination,paint);int i=at(selected);if(i>=0){float x=dragObject?ghostX:entities[i+2],y=dragObject?ghostY:entities[i+3],hw=Math.max(4,entities[i+4]/2f),hh=Math.max(4,entities[i+5]/2f);c.drawRect(l+(x-cameraX-hw)*s,t+(y-cameraY-hh)*s,l+(x-cameraX+hw)*s,t+(y-cameraY+hh)*s,marker);}}
  @Override public boolean onTouchEvent(MotionEvent e){int action=e.getActionMasked();float x=e.getX(),y=e.getY();if(action==MotionEvent.ACTION_CANCEL){cancelGesture();refresh();return true;}if(action==MotionEvent.ACTION_DOWN){multi=false;lastSpan=0;}
   if(e.getPointerCount()>=2){float dx=e.getX(1)-x,dy=e.getY(1)-y,span=(float)Math.hypot(dx,dy),mx=(x+e.getX(1))/2,my=(y+e.getY(1))/2;
    if(!multi||action==MotionEvent.ACTION_POINTER_DOWN){multi=true;dragObject=false;tapPlace=false;lastSpan=span;lastX=mx;lastY=my;refresh();}
    else if(action==MotionEvent.ACTION_MOVE){cameraX+=Math.round((lastX-mx)/scale());cameraY+=Math.round((lastY-my)/scale());if(lastSpan>dp(8)&&span>dp(8))zoomAt(zoom*span/lastSpan,mx,my);else{clamp();refresh();}lastSpan=span;lastX=mx;lastY=my;}return true;
   }
   if(multi){if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){cancelGesture();refresh();}return true;}
   float wx=cameraX+(x-left())/scale(),wy=cameraY+(y-top())/scale();
   if(action==MotionEvent.ACTION_DOWN){lastX=startX=x;lastY=startY=y;moved=false;tapPlace=false;tapSelect=pan?hit(wx,wy):0;if(placeType!=0)return true;int id=pan?0:hit(wx,wy);if(id!=0){selected=id;int i=at(id);offsetX=entities[i+2]-wx;offsetY=entities[i+3]-wy;ghostX=entities[i+2];ghostY=entities[i+3];dragObject=true;}else tapPlace=!pan&&selected!=0;update();return true;}
   if(action==MotionEvent.ACTION_MOVE){moved|=Math.abs(x-startX)+Math.abs(y-startY)>dp(4);if(dragObject){ghostX=Math.max(0,Math.min(worldWidth-1,wx+offsetX));ghostY=Math.max(0,Math.min(worldHeight-1,wy+offsetY));refresh();}else if(placeType==0){int dx=Math.round((lastX-x)/scale()),dy=Math.round((lastY-y)/scale());cameraX+=dx;cameraY+=dy;lastX-=dx*scale();lastY-=dy*scale();clamp();refresh();}return true;}
   if(action==MotionEvent.ACTION_UP){int id=selected,tx=Math.round(ghostX),ty=Math.round(ghostY);boolean commit=dragObject&&moved,tap=tapPlace&&!moved;dragObject=false;tapPlace=false;if(pan&&!moved&&tapSelect!=0){selected=tapSelect;pan=false;update();}else if(placeType!=0&&!moved)place(Math.round(wx),Math.round(wy));else if(commit)move(id,tx,ty);else if(tap)move(id,Math.round(wx),Math.round(wy));refresh();performClick();return true;}
   if(action==MotionEvent.ACTION_CANCEL){cancelGesture();refresh();return true;}return true;
  }
  @Override public boolean performClick(){super.performClick();return true;}
 }
}
