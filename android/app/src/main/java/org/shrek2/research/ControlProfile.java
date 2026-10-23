package org.shrek2.research;

import android.content.SharedPreferences;

/** Persistent input preferences; coordinates are percentages of the usable view. */
final class ControlProfile {
 static final String[] NAMES={"Left","Down","Right","Up","B","A","Select","Start","L","R","QoL","L+R"};
 static final int[] ACTIONS={32,128,16,64,2,1,4,8,512,256,4096,768};
 static final String[] ACTION_NAMES={"Left","Down","Right","Up","Attack / Back","Jump / Confirm","Select / Interact","Start / Pause","L / Next hero","R / Next hero","QoL menu","Quick load","Quick save","L + R / Joint control"};
 static final int[] ALL_ACTIONS={32,128,16,64,2,1,4,8,512,256,4096,1024,2048,768};
 static final int[] DEFAULT_X={2,10,18,10,89,98,46,54,0,100,50,85};
 static final int[] DEFAULT_Y={98,98,98,78,98,98,98,98,12,12,78,12};
 private final SharedPreferences prefs;
 ControlProfile(SharedPreferences p){prefs=p;}
 private int value(int i,String k,int d){return prefs.getInt("touch_"+i+"_"+k,d);}
 int x(int i){return clamp(value(i,"x",DEFAULT_X[i]),0,100);}
 int y(int i){return clamp(value(i,"y",DEFAULT_Y[i]),0,100);}
 int size(int i){return clamp(value(i,"size",i==10?44:52),24,144);}
 int action(int i){return value(i,"action",ACTIONS[i]);}
 boolean visible(int i){return value(i,"visible",i==11?0:1)!=0;}
 int visibility(){return prefs.getInt("touch_visibility",0);}
 void visibility(int mode){prefs.edit().putInt("touch_visibility",clamp(mode,0,2)).apply();}
 boolean show(boolean pad){return visibility()==0||(visibility()==2&&!pad);}
 void geometry(int i,int x,int y,int size){prefs.edit().putInt("touch_"+i+"_x",clamp(x,0,100)).putInt("touch_"+i+"_y",clamp(y,0,100)).putInt("touch_"+i+"_size",clamp(size,24,144)).apply();}
 void action(int i,int action){prefs.edit().putInt("touch_"+i+"_action",action).apply();}
 void visible(int i,boolean on){prefs.edit().putInt("touch_"+i+"_visible",on?1:0).apply();}
 int pad(int key,int fallback){return prefs.getInt("pad_key_"+key,fallback);}
 void bind(int key,int action){prefs.edit().putInt("pad_key_"+key,action).apply();}
 Layout draft(){return new Layout(this);}
 static final class Layout {
  final int[] x=new int[NAMES.length],y=new int[NAMES.length],size=new int[NAMES.length];final boolean[] shown=new boolean[NAMES.length];
  Layout(ControlProfile p){for(int i=0;i<NAMES.length;i++){x[i]=p.x(i);y[i]=p.y(i);size[i]=p.size(i);shown[i]=p.visible(i);}}
  void reset(){for(int i=0;i<NAMES.length;i++){x[i]=DEFAULT_X[i];y[i]=DEFAULT_Y[i];size[i]=i==10?44:52;shown[i]=i!=11;}}
  void save(ControlProfile p){SharedPreferences.Editor e=p.prefs.edit();for(int i=0;i<NAMES.length;i++)e.putInt("touch_"+i+"_x",x[i]).putInt("touch_"+i+"_y",y[i]).putInt("touch_"+i+"_size",size[i]).putInt("touch_"+i+"_visible",shown[i]?1:0);e.apply();}
 }
 void reset(){SharedPreferences.Editor e=prefs.edit();for(String key:prefs.getAll().keySet())if(key.equals("touch_visibility")||key.matches("touch_[0-9]+_.*")||key.startsWith("pad_key_"))e.remove(key);e.apply();}
 static int clamp(int v,int lo,int hi){return Math.max(lo,Math.min(hi,v));}
}
