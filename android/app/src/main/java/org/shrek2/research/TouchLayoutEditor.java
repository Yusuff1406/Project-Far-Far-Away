package org.shrek2.research;

import android.content.Context;
import android.view.Gravity;
import android.view.MotionEvent;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Paused, non-gameplay preview. All edits remain local until Save. */
final class TouchLayoutEditor extends FrameLayout {
 interface Done {void close(boolean save);}
 final ControlProfile.Layout draft;
 private final Done done;
 private final FrameLayout canvas;
 private final Button[] buttons=new Button[ControlProfile.NAMES.length];
 private final TextView selectedLabel;
 private int selected;
 private float downX,downY;
 private int startX,startY;
 TouchLayoutEditor(Context context,ControlProfile profile,Done done){
  super(context);this.done=done;draft=profile.draft();setBackgroundColor(0x55000000);
  // The canvas retains the exact gameplay area, including safe insets.
  canvas=new FrameLayout(context);addView(canvas,new FrameLayout.LayoutParams(-1,-1));
  for(int i=0;i<buttons.length;i++){
   final int n=i;Button b=buttons[i]=new Button(context);b.setText(ControlProfile.NAMES[i]);b.setTextSize(12);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(0,0,0,0);
   canvas.addView(b,new FrameLayout.LayoutParams(dp(draft.size[i]),dp(draft.size[i])));
   b.setOnTouchListener((v,e)->{int a=e.getActionMasked();if(a==MotionEvent.ACTION_DOWN){selected=n;FrameLayout.LayoutParams lp=(FrameLayout.LayoutParams)b.getLayoutParams();startX=lp.leftMargin;startY=lp.topMargin;downX=e.getRawX();downY=e.getRawY();refreshSelection();}
    else if(a==MotionEvent.ACTION_MOVE||a==MotionEvent.ACTION_UP){FrameLayout.LayoutParams lp=(FrameLayout.LayoutParams)b.getLayoutParams();int w=Math.max(0,canvas.getWidth()-lp.width),h=Math.max(0,canvas.getHeight()-lp.height);lp.leftMargin=ControlProfile.clamp(Math.round(startX+e.getRawX()-downX),0,w);lp.topMargin=ControlProfile.clamp(Math.round(startY+e.getRawY()-downY),0,h);b.setLayoutParams(lp);draft.x[n]=w==0?0:Math.round(lp.leftMargin*100f/w);draft.y[n]=h==0?0:Math.round(lp.topMargin*100f/h);}
    return true;});
  }
  LinearLayout toolbar=new LinearLayout(context);toolbar.setOrientation(LinearLayout.VERTICAL);toolbar.setBackgroundColor(0xdd181818);
  selectedLabel=new TextView(context);selectedLabel.setTextColor(0xffffffff);toolbar.addView(selectedLabel);
  LinearLayout row=new LinearLayout(context);toolbar.addView(row);
  action(row,"Choose",()->new android.app.AlertDialog.Builder(context).setTitle("Select button").setItems(ControlProfile.NAMES,(d,i)->{selected=i;refreshSelection();}).show());
  action(row,"−",()->resize(-4));action(row,"+",()->resize(4));action(row,"Show / Hide",()->{draft.shown[selected]=!draft.shown[selected];refreshSelection();});
  LinearLayout saves=new LinearLayout(context);toolbar.addView(saves);action(saves,"Save",()->close(true));action(saves,"Reset",()->{draft.reset();layoutButtons();});action(saves,"Cancel",()->close(false));
  FrameLayout.LayoutParams tools=new FrameLayout.LayoutParams(-2,-2,Gravity.TOP|Gravity.CENTER_HORIZONTAL);addView(toolbar,tools);
  selectedLabel.setOnClickListener(v->{tools.gravity=(tools.gravity==(Gravity.TOP|Gravity.CENTER_HORIZONTAL)?Gravity.BOTTOM:Gravity.TOP)|Gravity.CENTER_HORIZONTAL;toolbar.setLayoutParams(tools);});
  canvas.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{if(r-l!=or-ol||b-t!=ob-ot)layoutButtons();});refreshSelection();
 }
 private void action(LinearLayout row,String text,Runnable action){Button b=new Button(getContext());b.setText(text);b.setTextSize(12);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(dp(8),0,dp(8),0);b.setOnClickListener(v->action.run());row.addView(b,new LinearLayout.LayoutParams(-2,dp(44)));}
 private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
 void resize(int delta){draft.size[selected]=ControlProfile.clamp(draft.size[selected]+delta,24,144);layoutButtons();}
 void close(boolean save){done.close(save);}
 void layoutButtons(){for(int i=0;i<buttons.length;i++){int size=dp(draft.size[i]);FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(size,size,Gravity.TOP|Gravity.LEFT);lp.leftMargin=Math.max(0,canvas.getWidth()-size)*draft.x[i]/100;lp.topMargin=Math.max(0,canvas.getHeight()-size)*draft.y[i]/100;buttons[i].setLayoutParams(lp);}refreshSelection();}
 private void refreshSelection(){if(selectedLabel==null)return;selectedLabel.setText("Tap here to move toolbar · "+ControlProfile.NAMES[selected]+" · "+draft.size[selected]+" dp · "+(draft.shown[selected]?"shown":"hidden"));for(int i=0;i<buttons.length;i++){buttons[i].setAlpha(draft.shown[i]?(i==selected?1f:.8f):.35f);buttons[i].setPressed(i==selected);}}
}
