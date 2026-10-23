package org.shrek2.research;

import android.content.Context;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

// Traversal exposes native movement without granting chapter completion.
final class CampaignPanel extends FrameLayout {
 interface Listener {void close();void song(int address);void launch(int scene);}
 final CampaignBrowser browser;
 final CampaignSurface surface;
 private final Listener listener;
 private final TextView status;
 private final Button mode,play,mirror,zoom,objects,walk,chapter;
 private final LinearLayout walking;
 private int lastSong=-1;
 private static final String[] BANKS={"Shrek","Donkey","Puss in Boots","Gingy","Human Shrek","Enemies and NPCs","Interface","Environment","Coins","Bank 10","Fairy","Bank 12","Mice","NPCs and allies","Bank 15","Items and effects"};
 CampaignPanel(Context context,CampaignBrowser browser,Listener listener){
  super(context);this.browser=browser;this.listener=listener;
  surface=new CampaignSurface(context,browser,this::update);FrameLayout.LayoutParams canvas=new FrameLayout.LayoutParams(-1,-1);canvas.topMargin=Math.round(88*context.getResources().getDisplayMetrics().density);canvas.bottomMargin=Math.round(140*context.getResources().getDisplayMetrics().density);addView(surface,canvas);
  LinearLayout top=new LinearLayout(context);top.setOrientation(LinearLayout.VERTICAL);top.setBackgroundColor(0xdd18251b);
  LinearLayout first=new LinearLayout(context);top.addView(first);
  button(first,"Back",listener::close);mode=button(first,"Characters",()->change(()->browser.mode(browser.info()[0]==1?0:1)));
  button(first,"◀ Map",()->change(()->browser.navigate(-1)));button(first,"Map ▶",()->change(()->browser.navigate(1)));
  chapter=button(first,"Play level",()->listener.launch(browser.info()[1]));
  walk=button(first,"Walk",()->change(()->browser.mode(browser.info()[0]==2?0:2)));
  status=new TextView(context);status.setTextSize(11);status.setTextColor(0xffffffff);status.setPadding(8,2,8,2);top.addView(status);addView(top,new FrameLayout.LayoutParams(-1,-2,Gravity.TOP));
  LinearLayout bottom=new LinearLayout(context);bottom.setOrientation(LinearLayout.VERTICAL);bottom.setBackgroundColor(0xdd18251b);
  LinearLayout characters=new LinearLayout(context);bottom.addView(characters);
  button(characters,"◀ Hero",()->change(()->cycleCharacter(-1)));button(characters,"Hero ▶",()->change(()->cycleCharacter(1)));
  button(characters,"◀ Animation",()->change(()->{browser.mode(1);browser.animation(-1);}));button(characters,"Animation ▶",()->change(()->{browser.mode(1);browser.animation(1);}));
  LinearLayout playback=new LinearLayout(context);bottom.addView(playback);
  objects=button(playback,"Objects",()->change(()->browser.option(2,1-browser.save()[9])));
  play=button(playback,"Pause",()->change(()->browser.option(0,1-browser.save()[8])));
  button(playback,"Restart",()->change(()->{if(browser.info()[0]==2)browser.restartWalk();else browser.animation(0);}));mirror=button(playback,"Mirror: off",()->change(()->browser.option(1,1-browser.save()[7])));
  zoom=button(playback,"Zoom: 2×",()->change(()->browser.option(3,browser.save()[10]%4+1)));
  walking=new LinearLayout(context);walking.setMotionEventSplittingEnabled(true);bottom.addView(walking);control(walking,"◀",32);control(walking,"▶",16);control(walking,"A · Jump",1);control(walking,"B · Air attack",2);
  addView(bottom,new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM));
 }
 private void cycleCharacter(int delta){if(browser.info()[0]==2){int[] order={3,6,4,5,7};int t=browser.walkInfo()[0],at=0;for(int i=0;i<5;i++)if(order[i]==t)at=i;browser.character(order[(at+delta+5)%5]);}else{browser.mode(1);browser.bank(delta);}}
 private void control(LinearLayout row,String text,int mask){Button b=button(row,text,()->{});b.setOnTouchListener((v,e)->{int action=e.getActionMasked(),index=e.getActionIndex();if(action==MotionEvent.ACTION_DOWN||action==MotionEvent.ACTION_POINTER_DOWN)surface.press(e.getPointerId(index),mask);else if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_POINTER_UP)surface.release(e.getPointerId(index));else if(action==MotionEvent.ACTION_CANCEL)surface.clearInput();return true;});}
 private Button button(LinearLayout row,String text,Runnable action){Button b=new Button(getContext());b.setText(text);b.setTextSize(10);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(6,1,6,1);row.addView(b,new LinearLayout.LayoutParams(0,-2,1f));b.setOnClickListener(v->action.run());return b;}
 private void change(Runnable action){try{surface.clearInput();action.run();surface.refresh();update();}catch(Exception e){status.setText(e.getMessage());}}
 void update(){
  int[] info=browser.info(),saved=browser.save();chapter.setVisibility(info[0]!=1&&SessionActivity.playableScene(info[1])?View.VISIBLE:View.GONE);int order=info[2];String map=order<25?"Book "+(order/5+1)+" · chapter "+(order%5+1):"Bonus "+(order-24);
  String name=info[7]<BANKS.length?BANKS[info[7]]:"Bank "+(info[7]+1);
  status.setText(info[0]==0?map+" · "+info[3]+"×"+info[4]+" · map viewer\nDrag to pan · Characters opens animations":name+" · animation "+(info[8]+1)+"/"+info[9]+" · frame "+(info[11]+1)+"/"+info[10]+"\n"+map+" · animation viewer");
  if(info[0]==2){int[] w=browser.walkInfo();String hero=w[0]==3?"Shrek":w[0]==6?"Donkey":w[0]==4?"Puss in Boots":w[0]==5?"Gingy":"Human Shrek";status.setText(map+" · "+hero+" · "+(w[1]>>8)+", "+(w[2]>>8)+"\nMovement preview: map collision only");}
  walking.setVisibility(info[0]==2?View.VISIBLE:View.GONE);walk.setText(info[0]==2?"Browse":browser.canWalk()?"Walk":"Minigame");mirror.setEnabled(info[0]!=2);zoom.setEnabled(info[0]!=2);
  mode.setText(info[0]!=1?"Characters":"Map");play.setText(saved[8]==0?"Pause":"Resume");mirror.setText(saved[7]==0?"Mirror: off":"Mirror: on");zoom.setText("Zoom: "+saved[10]+"×");objects.setText(saved[9]==0?"Objects: off":"Objects: on");
  if(lastSong!=info[13]){listener.song(info[13]);lastSong=info[13];}
 }
 void resume(){update();surface.resume();}
 void pause(){surface.pause();}
}
