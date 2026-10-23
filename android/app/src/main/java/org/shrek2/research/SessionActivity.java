package org.shrek2.research;

import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.os.Bundle;
import android.os.Build;
import android.view.Gravity;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.graphics.Insets;
import android.view.Choreographer;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.ScrollView;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

// Owned native player+item scene. Full world and PCM are still separate work.
public class SessionActivity extends Activity implements Choreographer.FrameCallback {
 static {System.loadLibrary("shrek_scene");}
 private static native long createSession(String resources,String scene,String collision,String sprites);
 private static native void loadWorldSession(long h,String resources,String scene,String collision,String sprites,String objects);
 private static native long createWorldSession(String resources,String scene,String collision,String sprites,String objects);
 private static native void destroySession(long session);
 private static native void restartSession(long session);
 private static native int[] advanceSession(long session,int buttons,int width,int height,int[] info);
 private static native int readCoinCount(long session);
 private static native int readHealth(long session);
 private static native int readDeathRestarts(long session);
 private static native int readMinigameState(long session);
 private int savedBonusIndex=-1;
 private static native int readBonusIndex(long session);
 private static native int readBonusBest(long session);
 private static native void setBonusBest(long session,int best);
 private static native boolean isLevelComplete(long session);
 private static native void setPussDoubleJump(long session,boolean enabled);
 private static native void setBonusResults(long session,boolean enabled);
 private int savedBonusBest=0;
 private static native boolean isDialogueActive(long session);
 private static native int[] readSessionSounds(long session,int cursor);
 private static final long STEP_NS=16666667L;
 private long session=0,lastFrame=0,elapsed=0;
 private boolean resumed=false,ready=false;
 private boolean wide=true,menuOpen=false,arenaWide=false;
 private boolean soundEnabled=true;
 private boolean worldMode=false,musicEnabled=true;
 private int soundCursor=0;private int[] pausedScene;private int pausedSceneWidth;
 private SessionAudio audio;
 private int buttons=0;
 private final TouchButtons inputs=new TouchButtons(),controllerInputs=new TouchButtons();
 private final int[] info=new int[8];
 private Button attackButton,jumpButton,skipDialogue;
 private boolean pendingDialogSkip=false;
 private TextView label;
 private GameView view;
 private OriginalMenu pauseMenu;
 private MenuSurface pauseSurface;
 private ScrollView optionsPane;
 private boolean campaign=false,completionPending=false;
 private int activeScene=0;
 private int campaignSlot=0;
 private boolean frontendEnabled=false,frontendOpen=false;private FrameLayout gameControls,rootFrame,controlPanel;private int controllerMask=0,settingsCursor=0;private boolean touchMenus=false;private LinearLayout settingsActions;
 private boolean browserOpen=false;private CampaignBrowser browser;private CampaignPanel browserPanel;private Button assetsEntry;
 private static native int[] pauseFrame(long h,int width,boolean hide);
 private static native int soundHead(long h);
 private static native int musicHint(long h);
 private static native void resetPresentation(long h);
 private static native void updateSession(long h,int buttons,int width,int[]info,int steps);
 private static native void presentSession(long h,int width,int alpha,int[]pixels);
 private int refreshChoice=0;private float requestedHz=60;private boolean smoothMotion=true;private int[] displayPixels;
 private void refreshDisplay(){if(session!=0)resetPresentation(session);if(view==null)return;android.view.Display display=view.getDisplay();if(display==null)return;java.util.ArrayList<Float> rates=new java.util.ArrayList<>();if(Build.VERSION.SDK_INT>=23){android.view.Display.Mode current=display.getMode();for(android.view.Display.Mode mode:display.getSupportedModes())if(mode.getPhysicalWidth()==current.getPhysicalWidth()&&mode.getPhysicalHeight()==current.getPhysicalHeight())rates.add(mode.getRefreshRate());}else{rates.add(display.getRefreshRate());}float[] values=new float[rates.size()];for(int i=0;i<values.length;i++)values[i]=rates.get(i);requestedHz=RefreshPolicy.choose(refreshChoice,values);WindowManager.LayoutParams attrs=getWindow().getAttributes();if(Build.VERSION.SDK_INT>=23)attrs.preferredDisplayModeId=0;attrs.preferredRefreshRate=requestedHz;getWindow().setAttributes(attrs);if(Build.VERSION.SDK_INT>=35)view.setRequestedFrameRate(requestedHz);}

 private boolean editBaselineReady=false;
 private static native int saveQuickState(long h,String path);
 private static native int quickStateScene(String path);
 private static native int loadQuickState(long h,String path);
 private static native int[] debugInfo(long h);
 private static native int[] editorEntities(long h);
 private static native int[] editorThumbnail(long h,int type);
 private static native void editorFrame(long h,int width,int x,int y,int[] pixels);
 private static native void editorView(long h,int width,int height,int x,int y,int id,int px,int py,int[] pixels);
 private MapEditorPanel mapEditor;private boolean visualUndoReady=false;
 private static native int[] debugActors(long h);
 private static native int debugEdit(long h,int command,int a,int b,int c);
 private static native int[] advanceFast(long h,int buttons,int width,int height,int[] info,int steps);
 private int speed=1,quickSlot=1,analogMask=0;private String qolPage="";private float deadzone=.25f;
 private final java.util.ArrayList<View> legacyOptions=new java.util.ArrayList<>();
 private android.hardware.input.InputManager gamepads;
 private ControlProfile controls;private final Button[] touchButtons=new Button[11];private int bindingAction=0;
 private final java.util.HashMap<Integer,Integer> heldKeys=new java.util.HashMap<>();
 private boolean padConnected(){for(int id:android.view.InputDevice.getDeviceIds()){android.view.InputDevice d=android.view.InputDevice.getDevice(id);if(d!=null&&((d.getSources()&android.view.InputDevice.SOURCE_GAMEPAD)==android.view.InputDevice.SOURCE_GAMEPAD||(d.getSources()&android.view.InputDevice.SOURCE_JOYSTICK)==android.view.InputDevice.SOURCE_JOYSTICK))return true;}return false;}
 private void layoutControls(){if(controls==null||controlPanel==null)return;clearInput();boolean show=controls.show(padConnected());for(int i=0;i<touchButtons.length;i++){Button b=touchButtons[i];if(b==null)continue;int size=dp(controls.size(i));FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(size,size,Gravity.TOP|Gravity.LEFT);lp.leftMargin=Math.max(0,controlPanel.getWidth()-controlPanel.getPaddingLeft()-controlPanel.getPaddingRight()-size)*controls.x(i)/100;lp.topMargin=Math.max(0,controlPanel.getHeight()-controlPanel.getPaddingTop()-controlPanel.getPaddingBottom()-size)*controls.y(i)/100;b.setLayoutParams(lp);b.setVisibility(show&&controls.visible(i)?View.VISIBLE:View.GONE);}}
 private Button touchControl(int i,String text){Button b=new Button(this);touchButtons[i]=b;b.setText(text);b.setTextSize(12);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(2,0,2,0);b.setAlpha(.8f);controlPanel.addView(b,new FrameLayout.LayoutParams(dp(52),dp(52)));b.setOnTouchListener((v,event)->{int a=event.getActionMasked();if(a==MotionEvent.ACTION_DOWN){routeButton(controls.action(i),true,1000+i);v.setPressed(true);}else if(a==MotionEvent.ACTION_UP||a==MotionEvent.ACTION_CANCEL){routeButton(controls.action(i),false,1000+i);v.setPressed(false);if(a==MotionEvent.ACTION_UP)v.performClick();}return true;});return b;}
 private boolean noTouchControls(){if(controls==null)return false;if(!controls.show(padConnected()))return true;for(int i=0;i<11;i++)if(controls.visible(i))return false;return true;}
 private void controlsPage(){description("Touch coordinates are percentages of the available screen. Changes persist across launches. Android Back opens QoL when controls are hidden; Select + Start opens QoL even when touch controls are hidden.");option("Touch controls: "+new String[]{"shown","hidden","hide with gamepad"}[controls.visibility()],()->{controls.visibility((controls.visibility()+1)%3);layoutControls();qol("Controls");});for(int i=0;i<11;i++){final int n=i;option(ControlProfile.NAMES[i]+" · "+(controls.visible(i)?controls.size(i)+" dp":"hidden"),()->new android.app.AlertDialog.Builder(this).setTitle(ControlProfile.NAMES[n]).setItems(new String[]{"Position and size","Assign action",controls.visible(n)?"Hide button":"Show button"},(d,choice)->{if(choice==0)numbers(ControlProfile.NAMES[n],new String[]{"Horizontal % (0–100)","Vertical % (0–100)","Size dp (24–144)"},new int[]{controls.x(n),controls.y(n),controls.size(n)},v->{controls.geometry(n,v[0],v[1],v[2]);layoutControls();qol("Controls");});else if(choice==1)new android.app.AlertDialog.Builder(this).setTitle("Touch action").setItems(ControlProfile.ACTION_NAMES,(dd,j)->{controls.action(n,ControlProfile.ALL_ACTIONS[j]);clearInput();qol("Controls");}).show();else{controls.visible(n,!controls.visible(n));layoutControls();qol("Controls");}}).show());}option("Remap gamepad buttons",()->qol("Gamepad mapping"));option("Reset control changes",()->{controls.reset();bindingAction=0;layoutControls();qol("Controls");});}

 private final android.hardware.input.InputManager.InputDeviceListener padListener=new android.hardware.input.InputManager.InputDeviceListener(){public void onInputDeviceAdded(int id){layoutControls();}public void onInputDeviceChanged(int id){layoutControls();}public void onInputDeviceRemoved(int id){layoutControls();if(pauseSurface!=null)pauseSurface.releaseButtons();}};
 private void note(String text){android.widget.Toast.makeText(this,text,android.widget.Toast.LENGTH_LONG).show();}
 private void option(String text,Runnable action){Button b=new Button(this);b.setText(text);b.setTextSize(12);settingsActions.addView(b);b.setOnClickListener(v->{try{action.run();}catch(Exception e){note(e.getMessage()==null?"Operation failed":e.getMessage());}});}
 private void description(String text){TextView t=new TextView(this);t.setText(text);t.setTextColor(0xffffffff);t.setPadding(dp(12),dp(8),dp(12),dp(8));settingsActions.addView(t);}
 private boolean editing(){if(session==0||frontendOpen||!ready){note("Start a level first");return false;}return true;}
 private static String heroName(int t){return new String[]{"Shrek","Puss in Boots","Gingy","Donkey","Human Shrek"}[Math.max(0,Math.min(4,t-3))];}
 private void qol(String page){qolPage=page;settingsActions.removeAllViews();description("Project Far Far Away · QoL"+(page.isEmpty()?"":" / "+page));option(page.isEmpty()?"Resume / Back":"Back to QoL",()->{if(page.isEmpty())closeSettings();else qol("");});
  if(page.isEmpty()){
   for(String name:new String[]{"Settings","Performance","Controls","Gamepad","Save states","Editor and trainer","Level music"})option(name,()->qol(name));
   option("Maps and characters",()->openBrowser(-1,0));option("Restart level",()->{if(session!=0&&!frontendOpen){loadChapter(activeScene);ready=true;soundCursor=0;if(audio!=null)audio.reset();closeSettings();}});option("Main menu",()->leaveCampaign(true,false));
  }else if(page.equals("Settings")){
   description("Optional gameplay and display settings");for(int i:new int[]{2,4,5,6,7,8,10,11})if(i<legacyOptions.size())settingsActions.addView(legacyOptions.get(i));
  }else if(page.equals("Performance")){
   description("The game simulation and original sprite animation timing stay at 60 Hz. Higher refresh rates interpolate positions and camera between simulation frames. Interpolation adds up to one simulation step of display latency. The display and system power settings determine the available rate.");
   option("Refresh rate: "+(refreshChoice==0?"Auto":refreshChoice+" Hz")+" ("+Math.round(requestedHz)+" Hz requested)",()->new android.app.AlertDialog.Builder(this).setTitle("Display refresh rate").setItems(new String[]{"Auto / highest supported","60 Hz","90 Hz","120 Hz","144 Hz","165 Hz","240 Hz"},(d,i)->{refreshChoice=new int[]{0,60,90,120,144,165,240}[i];getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt("refresh_rate",refreshChoice).apply();lastFrame=elapsed=0;refreshDisplay();qol("Performance");}).show());
   option("Smooth high-refresh motion: "+(smoothMotion?"on":"off"),()->{smoothMotion=!smoothMotion;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("smooth_motion",smoothMotion).apply();lastFrame=elapsed=0;qol("Performance");});
  }else if(page.equals("Controls")){controlsPage();
  }else if(page.equals("Gamepad mapping")){description(bindingAction==0?"Choose an action, then press a physical button. D-pad keys and triggers can also be reassigned. Select + Start and Android Back remain available.":"Press a gamepad button now. Android Back cancels.");for(int i=0;i<ControlProfile.ALL_ACTIONS.length;i++){final int a=ControlProfile.ALL_ACTIONS[i];option(ControlProfile.ACTION_NAMES[i],()->{clearInput();bindingAction=a;qol(page);});}option("Cancel binding",()->{bindingAction=0;qol("Controls");});
  }else if(page.equals("Gamepad")){option("Remap buttons",()->qol("Gamepad mapping"));
   description("D-pad / left stick: move\nA: jump / confirm · B: attack / back\nL1 or R1: next hero · L1 + R1: joint control\nSelect: interact · Start: original pause / release item\nSelect + Start: QoL · L2: quick load · R2: quick save\nStandard Android USB and Bluetooth gamepads are supported.");
   option("Stick deadzone: "+Math.round(deadzone*100)+"%",()->{deadzone=deadzone<.3f?.4f:.2f;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt("pad_deadzone",Math.round(deadzone*100)).apply();clearInput();qol(page);});
   int count=0;for(int id:android.view.InputDevice.getDeviceIds()){android.view.InputDevice d=android.view.InputDevice.getDevice(id);if(d!=null&&((d.getSources()&android.view.InputDevice.SOURCE_GAMEPAD)==android.view.InputDevice.SOURCE_GAMEPAD||(d.getSources()&android.view.InputDevice.SOURCE_JOYSTICK)==android.view.InputDevice.SOURCE_JOYSTICK)){description(d.getName());count++;}}if(count==0)description("No controller connected. Connect one and reopen this page.");
  }else if(page.equals("Save states")){
   description("Three slots per campaign save. Includes the party, enemies, items, dialogue and editor changes. Legacy world states remain supported; new slots also restore music.");option("Slot: "+quickSlot,()->{quickSlot=quickSlot%3+1;qol(page);});option("Quick save",()->quickSave());option("Quick load",()->quickLoad());option("Speed: "+speed+"×",()->{speed=speed%4+1;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt("speed",speed).apply();lastFrame=elapsed=0;qol(page);});description("Speed affects gameplay and transitions. Music keeps its original pitch and tempo.");
  }else if(page.equals("Editor and trainer")){
   if(!editing()){description("Enter a level to use the editor.");}else{
    int[]a=debugInfo(session);description("Scene "+a[0]+" · "+heroName(a[1])+" · "+a[2]+", "+a[3]+"\nHealth "+a[4]+" · Coins "+a[5]+" · Actors "+a[6]+" · Tick "+a[7]);description("Edits affect the live scene. Save to a quick slot to keep them. Reset changes returns to before the first edit; Restart restores the level. Release carried items and finish dialogue before changing heroes.");
    option("Visual map editor",()->openMapEditor());option("Add by coordinates (advanced)",()->spawnPicker());option("Object list (advanced)",()->actorPicker());
    option("Change selected character",()->new android.app.AlertDialog.Builder(this).setTitle("Character").setItems(new String[]{"Shrek","Puss in Boots","Gingy","Donkey","Human Shrek"},(d,i)->edit(3,i+3,0,0)).show());
    option("Character coordinates (advanced)",()->numbers("Teleport",new String[]{"X (pixels)","Y (pixels)"},new int[]{a[2],a[3]},v->edit(0,v[0],v[1],0)));
    option("Health",()->numbers("Health",new String[]{"Health (within hero maximum)"},new int[]{a[4]},v->edit(1,v[0],0,0)));
    option("Coins / score",()->numbers("Coins / score",new String[]{"Value (0–999999)"},new int[]{a[5]},v->edit(2,v[0],0,0)));
    option("Attack strength: "+new String[]{"Original","0.5× damage","1× damage","2× damage","4× damage"}[a[13]+1],()->new android.app.AlertDialog.Builder(this).setTitle("Attack strength").setItems(new String[]{"Original","0.5× damage","1× damage","2× damage","4× damage"},(d,i)->edit(9,a[1],i-1,0)).show());description("Higher damage is easiest to compare on tougher enemies and bosses. Strength is saved separately for each hero.");option("Movement / jump stats",()->numbers(heroName(a[1]),new String[]{"Speed % (25–300)","Jump % (25–200)"},new int[]{a[10],a[11]},v->edit(7,a[1],v[0],v[1])));
    for(int flag:new int[]{1,2,4}){String name=flag==1?"Ignore contact damage":flag==2?"Freeze enemies":"Freeze level timer";option(name+": "+((a[12]&flag)!=0?"on":"off"),()->edit(6,a[12]^flag,0,0));}option("Save edited scene",()->quickSave());option("Reset changes",()->resetEdits());
   }
  }else if(page.equals("Level music")){
   description("Choose a track for this level. Selection persists between sessions.");option("Default track",()->setTrack(-1));for(int i=0;i<TRACKS.length;i++){final int song=TRACKS[i];option(TRACK_NAMES[i],()->setTrack(song));}
  }
  settingsCursor=1;settingsActions.getChildAt(1).requestFocus();
 }
 private static final int[] TRACKS={0x08209428,0x08209b78,0x0820a320,0x0820af48,0x0820bf90,0x0820c5f0,0x0820d4dc,0x0820dc94,0x0820e3e8,0x0820e9b8,0x0820f388,0x0820f7b8,0x0820fc5c,0x08210364,0x082106c0,0x0820b76c,0x0820cf24};
 private static final String[] TRACK_NAMES={"Track 01","Track 02","Track 03","Track 04","Track 05 / Opening","Track 06","Track 07","Track 08","Minigames","Track 10","Track 11","Track 12","Track 13","Epilogue","Menu","Unused track 1","Unused track 2"};
 private void applyLevelTrack(){if(audio!=null)audio.setLevelOverride(getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt("music_scene_"+activeScene,-1));}
 private void setTrack(int song){if(!editing())return;if(audio==null){note("Audio unavailable");return;}audio.setLevelOverride(song);getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt("music_scene_"+activeScene,song).apply();note(song<0?"Original track restored":"Track changed");}
 private String quickPath(){return new File(getFilesDir(),"quick_"+campaignSlot+"_"+quickSlot+".s2qs").getAbsolutePath();}
 private static byte[] hashFile(File file)throws Exception{java.security.MessageDigest md=java.security.MessageDigest.getInstance("SHA-256");try(java.io.InputStream in=new java.io.FileInputStream(file)){byte[] buffer=new byte[65536];int n;while((n=in.read(buffer))!=-1)md.update(buffer,0,n);}return md.digest();}
 private byte[] stateHash(String path)throws Exception{return hashFile(new File(path));}
 private void saveAudio(String path)throws Exception{if(audio==null)return;File out=new File(path+".audio"),temp=new File(path+".audio.tmp");try(java.io.DataOutputStream d=new java.io.DataOutputStream(new FileOutputStream(temp))){d.writeInt(0x53324138);d.write(stateHash(path));for(int x:audio.snapshot())d.writeInt(x);}if(!temp.renameTo(out))throw new IOException("Could not save audio state");}
 private int[] loadAudio(String path){try(java.io.DataInputStream d=new java.io.DataInputStream(new java.io.FileInputStream(path+".audio"))){int magic=d.readInt();if(magic!=0x53324137&&magic!=0x53324138)return null;byte[]hash=new byte[32];d.readFully(hash);if(!java.util.Arrays.equals(hash,stateHash(path)))return null;int[]v=new int[magic==0x53324138?7:5];for(int i=0;i<v.length;i++)v[i]=d.readInt();for(int i=1;i<5;i++)if(v[i]<0)return null;return v;}catch(Exception e){return null;}}
 private void quickSave(){if(!editing())return;clearInput();String path=quickPath();if(saveQuickState(session,path)!=0){note("Could not save state");return;}try{saveAudio(path);note("Saved slot "+quickSlot);}catch(Exception e){note("World saved; audio snapshot unavailable");}}
 private void quickLoad(){if(session==0)return;String path=quickPath();int scene=quickStateScene(path);if(scene<0){note("Empty slot or invalid state");return;}try{int[]musicState=loadAudio(path);boolean changed=scene!=activeScene||frontendOpen;if(changed)loadChapter(scene);if(loadQuickState(session,path)!=0){note("Could not restore state");return;}activeScene=scene;editBaselineReady=false;pausedScene=null;frontendOpen=false;ready=true;completionPending=pendingDialogSkip=false;clearInput();soundCursor=soundHead(session);lastFrame=elapsed=0;if(audio!=null){audio.deathRestart();audio.setFrontendMode(false);audio.setBonusScene(readMinigameState(session)!=0);if(musicState!=null){audio.restore(musicState);getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt("music_scene_"+activeScene,musicState[0]).apply();}else if(changed)applyLevelTrack();}gameControls.setVisibility(View.VISIBLE);if(pauseSurface!=null)pauseSurface.overlay=true;setGamePaused(false);int w=gameWidth();view.setPixels(advanceFast(session,0,w,160,info,0),w);note("Loaded slot "+quickSlot);}catch(Exception e){note("Could not load state: "+e.getMessage());}}
 private String baselinePath(){return new File(getFilesDir(),"editor_baseline.s2qs").getAbsolutePath();}
 private void resetEdits(){if(!editing())return;if(!editBaselineReady){note("No editor changes to reset");return;}if(loadQuickState(session,baselinePath())!=0){note("Could not reset changes");return;}soundCursor=soundHead(session);if(audio!=null)audio.deathRestart();editBaselineReady=false;pausedScene=null;int w=gameWidth();view.setPixels(advanceFast(session,0,w,160,info,0),w);qol("Editor and trainer");note("Scene restored to before the first edit");}
 private void edit(int cmd,int a,int b,int c){if(!editing())return;if(!editBaselineReady){if(saveQuickState(session,baselinePath())!=0){note("Could not create undo snapshot");return;}editBaselineReady=true;}int result=debugEdit(session,cmd,a,b,c);if(result<0){note("Change rejected: check limits, finish dialogue, or release the carried object. Actor slots may be full.");return;}pausedScene=null;int w=gameWidth();view.setPixels(advanceFast(session,0,w,160,info,0),w);qol("Editor and trainer");}
 private interface Values{void apply(int[]v);}
 private void numbers(String title,String[]names,int[]initial,Values action){LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);android.widget.EditText[]fields=new android.widget.EditText[names.length];for(int i=0;i<names.length;i++){TextView t=new TextView(this);t.setText(names[i]);box.addView(t);fields[i]=new android.widget.EditText(this);fields[i].setInputType(android.text.InputType.TYPE_CLASS_NUMBER|android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);fields[i].setText(Integer.toString(initial[i]));box.addView(fields[i]);}new android.app.AlertDialog.Builder(this).setTitle(title).setView(box).setNegativeButton("Cancel",null).setPositiveButton("Apply",(d,w)->{try{int[]v=new int[fields.length];for(int i=0;i<v.length;i++)v[i]=Integer.parseInt(fields[i].getText().toString().trim());action.apply(v);}catch(Exception e){note("Enter valid whole numbers");}}).show();}
 private static final int[] SPAWN_TYPES={16,17,14,13,76,77,78,79,80,81,82,83,84,85,89,52,53,54,55,56,57,58,59,60,61,62};
 private void spawnPicker(){new android.app.AlertDialog.Builder(this).setTitle("Add object").setItems(new String[]{"Mushroom","Spring","Stump","Crate","Key","Apple","Flight fairy","Rubber duck","Shield","Invisibility","Clover","Potion","Flask","Heart jar","Coin","Enemy 52","Enemy 53","Enemy 54","Enemy 55","Enemy 56","Enemy 57","Enemy 58","Enemy 59","Enemy 60","Enemy 61","Enemy 62"},(d,i)->{int[]a=debugInfo(session);numbers("Spawn type "+SPAWN_TYPES[i],new String[]{"X (pixels)","Y (pixels)"},new int[]{Math.min(a[8]-1,a[2]+40),a[3]},v->edit(4,SPAWN_TYPES[i],v[0],v[1]));}).show();}
 private String visualUndoPath(){return new File(getFilesDir(),"editor_undo.s2qs").getAbsolutePath();}
 private int visualEdit(int cmd,int a,int b,int c){if(!editing())return -1;if(!editBaselineReady){if(saveQuickState(session,baselinePath())!=0){note("Could not create reset snapshot");return -1;}editBaselineReady=true;}if(saveQuickState(session,visualUndoPath()+".pending")!=0){note("Could not create undo snapshot");return -1;}int result=debugEdit(session,cmd,a,b,c);if(result<0){note("Cannot edit this object now. Release carried items and finish dialogue first.");return result;}visualUndoReady=new File(visualUndoPath()+".pending").renameTo(new File(visualUndoPath()));pausedScene=null;return result;}
 private void restoreVisual(boolean reset){if(reset&&!editBaselineReady||!reset&&!visualUndoReady){note(reset?"No changes to reset":"Nothing to undo");return;}if(loadQuickState(session,reset?baselinePath():visualUndoPath())!=0){note("Could not restore scene");return;}soundCursor=soundHead(session);pausedScene=null;visualUndoReady=false;if(reset)editBaselineReady=false;resetPresentation(session);}
 private void openMapEditor(){if(!editing())return;clearInput();visualUndoReady=false;mapEditor=new MapEditorPanel(this,new MapEditorPanel.Host(){public int[] info(){return debugInfo(session);}public int[] entities(){return editorEntities(session);}public int[] thumbnail(int type){return editorThumbnail(session,type);}public void frame(int w,int x,int y,int[]p){editorFrame(session,w,x,y,p);}public void preview(int w,int height,int x,int y,int id,int px,int py,int[]p){editorView(session,w,height,x,y,id,px,py,p);}public int edit(int cmd,int a,int b,int c){return visualEdit(cmd,a,b,c);}public void undo(){restoreVisual(false);}public void save(){quickSave();}public void reset(){restoreVisual(true);}public void close(){closeMapEditor();}});mapEditor.setPadding(controlPanel.getPaddingLeft(),controlPanel.getPaddingTop(),controlPanel.getPaddingRight(),controlPanel.getPaddingBottom());optionsPane.setVisibility(View.GONE);gameControls.setVisibility(View.GONE);controlPanel.setVisibility(View.GONE);rootFrame.addView(mapEditor,new FrameLayout.LayoutParams(-1,-1));}
 private void closeMapEditor(){if(mapEditor==null)return;rootFrame.removeView(mapEditor);mapEditor.dispose();mapEditor=null;clearInput();resetPresentation(session);gameControls.setVisibility(View.VISIBLE);controlPanel.setVisibility(View.VISIBLE);layoutControls();qol("Editor and trainer");optionsPane.setVisibility(View.VISIBLE);}
 private void actorPicker(){int[]a=debugActors(session);String[]names=new String[a.length/4];for(int i=0;i<names.length;i++)names[i]="#"+a[4*i]+" · type "+a[4*i+1]+" · "+a[4*i+2]+", "+a[4*i+3];new android.app.AlertDialog.Builder(this).setTitle("Live objects").setItems(names,(d,i)->new android.app.AlertDialog.Builder(this).setTitle(names[i]).setItems(new String[]{"Move","Remove"},(dd,choice)->{if(choice==1)edit(5,a[4*i],0,0);else numbers("Move object",new String[]{"X (pixels)","Y (pixels)"},new int[]{a[4*i+2],a[4*i+3]},v->edit(8,a[4*i],v[0],v[1]));}).show()).show();}
 @Override public boolean onGenericMotionEvent(MotionEvent e){if(session==0)return super.onGenericMotionEvent(e);if((e.getSource()&android.view.InputDevice.SOURCE_JOYSTICK)==android.view.InputDevice.SOURCE_JOYSTICK&&e.getActionMasked()==MotionEvent.ACTION_MOVE){int next=GamepadAxes.mask(e.getAxisValue(MotionEvent.AXIS_X),e.getAxisValue(MotionEvent.AXIS_Y),e.getAxisValue(MotionEvent.AXIS_HAT_X),e.getAxisValue(MotionEvent.AXIS_HAT_Y),deadzone);int changed=next^analogMask;analogMask=next;for(int m:new int[]{16,32,64,128})if((changed&m)!=0)routeButton(m,(next&m)!=0,-10000-m);return true;}return super.onGenericMotionEvent(e);}

 protected boolean startsInFrontend(){return false;}
 @Override public void onCreate(Bundle saved){
  super.onCreate(saved);if(!RomAccess.require(this))return;refreshChoice=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt("refresh_rate",0);smoothMotion=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("smooth_motion",true);arenaWide=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("arena_wide",false);frontendEnabled=startsInFrontend();frontendOpen=frontendEnabled&&(saved==null||saved.getBoolean("frontend_open",true));campaign=frontendEnabled||getIntent().getBooleanExtra("campaign",false);campaignSlot=Math.max(0,Math.min(2,getIntent().getIntExtra("slot",0)));worldMode=frontendEnabled||getIntent().getBooleanExtra("world",false);wide=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("wide",true);soundEnabled=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("sound",true);musicEnabled=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("music",true);
  controls=new ControlProfile(getSharedPreferences("SessionActivity",MODE_PRIVATE));
  FrameLayout root=new FrameLayout(this);rootFrame=root;root.setMotionEventSplittingEnabled(true);
  view=new GameView(this);root.addView(view,new FrameLayout.LayoutParams(-1,-1));
  controlPanel=new FrameLayout(this);controlPanel.setMotionEventSplittingEnabled(true);touchMenus=getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("touch_menus",false);FrameLayout stage=new FrameLayout(this);gameControls=stage;stage.setMotionEventSplittingEnabled(true);
  stage.setOnApplyWindowInsetsListener((v,insets)->{
   if(Build.VERSION.SDK_INT>=30){Insets safe=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());v.setPadding(safe.left,safe.top,safe.right,safe.bottom);controlPanel.setPadding(safe.left,safe.top,safe.right,safe.bottom);}
   else {
    int l=insets.getSystemWindowInsetLeft(),t=insets.getSystemWindowInsetTop(),r=insets.getSystemWindowInsetRight(),b=insets.getSystemWindowInsetBottom();
    if(Build.VERSION.SDK_INT>=28&&insets.getDisplayCutout()!=null){android.view.DisplayCutout cutout=insets.getDisplayCutout();l=Math.max(l,cutout.getSafeInsetLeft());t=Math.max(t,cutout.getSafeInsetTop());r=Math.max(r,cutout.getSafeInsetRight());b=Math.max(b,cutout.getSafeInsetBottom());}
    v.setPadding(l,t,r,b);controlPanel.setPadding(l,t,r,b);
   }
   return insets;
  });
  LinearLayout actions=new LinearLayout(this);settingsActions=actions;actions.setOrientation(LinearLayout.VERTICAL);actions.setBackgroundColor(0xcc202020);optionsPane=new ScrollView(this);optionsPane.addView(actions);optionsPane.setVisibility(View.GONE);
  label=new TextView(this);label.setTextSize(12);label.setPadding(12,4,12,4);label.setText("First scene");label.setBackgroundColor(0x88202020);stage.addView(label,new FrameLayout.LayoutParams(-2,-2,Gravity.TOP|Gravity.LEFT));
  TextView buildVersion=new TextView(this);buildVersion.setText("Version 1.07 · Select + Start: QoL");buildVersion.setPadding(12,8,12,8);actions.addView(buildVersion);
  Button closeOptions=new Button(this);closeOptions.setText("Back");actions.addView(closeOptions);closeOptions.setOnClickListener(v->closeSettings());
  Button format=new Button(this);format.setText(wide?"Display: wide":"Display: 3:2");format.setTextSize(12);actions.addView(format);
  format.setOnClickListener(v->{clearInput();wide=!wide;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("wide",wide).apply();format.setText(wide?"Display: wide":"Display: 3:2");view.fill=wide;view.invalidate();});
  Button restart=new Button(this);restart.setText("Restart");restart.setTextSize(12);actions.addView(restart);
  restart.setOnClickListener(v->{if(session!=0)try{clearInput();restartSession(session);pendingDialogSkip=false;soundCursor=0;if(audio!=null)audio.reset();ready=true;lastFrame=elapsed=0;attackButton.setEnabled(true);label.setText("First scene");setGamePaused(false);}catch(Exception e){ready=false;label.setText(e.getMessage());}});
  Button sound=new Button(this);sound.setText(soundEnabled?"Sound: on":"Sound: off");sound.setTextSize(11);actions.addView(sound);
  sound.setOnClickListener(v->{soundEnabled=!soundEnabled;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("sound",soundEnabled).apply();sound.setText(soundEnabled?"Sound: on":"Sound: off");if(audio!=null)audio.setEnabled(soundEnabled);});
  Button music=new Button(this);music.setText(musicEnabled?"Music: on":"Music: off");music.setTextSize(11);actions.addView(music);music.setOnClickListener(v->{musicEnabled=!musicEnabled;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("music",musicEnabled).apply();music.setText(musicEnabled?"Music: on":"Music: off");if(audio!=null)audio.setMusicEnabled(musicEnabled);});
  Button touch=new Button(this);touch.setText(touchMenus?"Touch menus: on":"Touch menus: off");actions.addView(touch);touch.setOnClickListener(v->{touchMenus=!touchMenus;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("touch_menus",touchMenus).apply();touch.setText(touchMenus?"Touch menus: on":"Touch menus: off");if(pauseSurface!=null)pauseSurface.touchEnabled(touchMenus);});
  skipDialogue=new Button(this);skipDialogue.setText("Skip dialogue");skipDialogue.setTextSize(11);skipDialogue.setEnabled(false);actions.addView(skipDialogue);
  skipDialogue.setOnClickListener(v->{if(session!=0&&isDialogueActive(session)){pendingDialogSkip=true;setGamePaused(false);}});
  Button testBooks=new Button(this);testBooks.setText("Unlock all books: "+(getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("test_books",false)?"on":"off"));actions.addView(testBooks);testBooks.setOnClickListener(v->{boolean on=!getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("test_books",false);getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("test_books",on).apply();if(pauseMenu!=null)pauseMenu.testBooks(on);testBooks.setText("Unlock all books: "+(on?"on":"off"));});
  Button worlds=new Button(this);worlds.setText("Maps and characters");actions.addView(worlds);worlds.setOnClickListener(v->openBrowser(-1,0));
  Button arena=new Button(this);arena.setText("Wide bosses and minigames: "+(arenaWide?"on":"off"));actions.addView(arena);arena.setOnClickListener(v->{arenaWide=!arenaWide;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("arena_wide",arenaWide).apply();arena.setText("Wide bosses and minigames: "+(arenaWide?"on":"off"));gameWidth();});
  Button extraJump=new Button(this);extraJump.setText("Puss double jump: "+(getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("puss_double_jump",false)?"on":"off"));actions.addView(extraJump);extraJump.setOnClickListener(v->{boolean on=!getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("puss_double_jump",false);getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putBoolean("puss_double_jump",on).apply();extraJump.setText("Puss double jump: "+(on?"on":"off"));if(session!=0)setPussDoubleJump(session,on);});
  Button back=new Button(this);back.setText("Main menu");back.setTextSize(12);actions.addView(back);back.setOnClickListener(v->leaveCampaign(true,false));FrameLayout.LayoutParams options=new FrameLayout.LayoutParams(-2,-1,Gravity.TOP|Gravity.CENTER_HORIZONTAL);options.topMargin=dp(44);options.bottomMargin=dp(68);stage.addView(optionsPane,options);
  for(int i=0;i<ControlProfile.NAMES.length;i++){String[] labels={"←","↓","→","↑","B","A","Select","Start","L","R","≡"};touchControl(i,labels[i]);}attackButton=touchButtons[4];jumpButton=touchButtons[5];controlPanel.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{if(r-l!=or-ol||b-t!=ob-ot)layoutControls();});
  for(int i=0;i<actions.getChildCount();i++)legacyOptions.add(actions.getChildAt(i));actions.removeAllViews();qol("");deadzone=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt("pad_deadzone",25)/100f;speed=Math.max(1,Math.min(4,getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt("speed",1)));gamepads=(android.hardware.input.InputManager)getSystemService(Context.INPUT_SERVICE);if(gamepads!=null)gamepads.registerInputDeviceListener(padListener,null);root.addView(stage,new FrameLayout.LayoutParams(-1,-1));view.fill=wide;setContentView(root);fullscreen();stage.requestApplyInsets();
  try{audio=new SessionAudio(this,soundEnabled,musicEnabled,frontendEnabled);}catch(IOException e){audio=null;}
  try{
   File dir=new File(getFilesDir(),"native_session");if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("Could not load or update resources");
   copyTree("session",dir);copy("scenes/scene_00.s2lv",new File(dir,"scene.s2lv"));copy("collision/scene_00.s2cl",new File(dir,"collision.s2cl"));
   String resources=new File(dir,"resources.s2pk").getAbsolutePath(),scene=new File(dir,"scene.s2lv").getAbsolutePath(),collision=new File(dir,"collision.s2cl").getAbsolutePath(),sprites=new File(dir,"sprites").getAbsolutePath();
   if(worldMode){copy("objects/scene_00.s2ob",new File(dir,"objects.s2ob"));session=createWorldSession(resources,scene,collision,sprites,new File(dir,"objects.s2ob").getAbsolutePath());}
   else session=createSession(resources,scene,collision,sprites);ready=session!=0;if(ready&&worldMode){savedBonusBest=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt("bonus_00_best",0);setBonusBest(session,savedBonusBest);setBonusResults(session,false);setPussDoubleJump(session,getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("puss_double_jump",false));}
   File menuFile=new File(getFilesDir(),"pause.s2ui");copy("frontend/menu.s2ui",menuFile);pauseMenu=new OriginalMenu(menuFile.getAbsolutePath(),new File(dir,"sprites/bank_328294/bank.s2sp").getAbsolutePath());pauseMenu.open(5,0);pauseSurface=new MenuSurface(this,pauseMenu,(action,state)->{if(frontendOpen){frontendAction(action,state);return;}if(action==2)setGamePaused(false);else if(action==3||action==4)leaveCampaign(action==4,false);else if(action==5){qol("");pauseSurface.pause();pauseSurface.setVisibility(View.GONE);optionsPane.setVisibility(View.VISIBLE);}});pauseSurface.audio(audio);pauseSurface.touchEnabled(touchMenus);pauseSurface.overlay=true;pauseSurface.setVisibility(View.GONE);root.addView(pauseSurface,new FrameLayout.LayoutParams(-1,-1));
   root.addView(controlPanel,new FrameLayout.LayoutParams(-1,-1));
   assetsEntry=new Button(this);assetsEntry.setText("Maps and characters");assetsEntry.setTextSize(11);assetsEntry.setVisibility(View.GONE);root.addView(assetsEntry,new FrameLayout.LayoutParams(-2,-2,Gravity.TOP|Gravity.LEFT));assetsEntry.setOnClickListener(v->openBrowser(-1,0));pauseSurface.onChanged(()->assetsEntry.setVisibility(touchMenus&&frontendOpen&&!browserOpen&&pauseMenu.state()[0]==1?View.VISIBLE:View.GONE));
   if(frontendEnabled){reloadProgress();if(frontendOpen){pauseMenu.open(11,0);if(saved==null)pauseMenu.startupFade();if(saved!=null&&saved.getIntArray("menu_state")!=null)pauseMenu.restore(saved.getIntArray("menu_state"));pauseSurface.overlay=false;pauseSurface.setVisibility(View.VISIBLE);gameControls.setVisibility(View.GONE);pauseSurface.refresh();pauseSurface.requestFocus();if(audio!=null)audio.setFrontendBoot(pauseMenu.state()[0]==11);}else{campaignSlot=Math.max(0,Math.min(2,saved.getInt("campaign_slot",0)));if(audio!=null){audio.setFrontendBoot(false);audio.setFrontendMode(false);}}}
  }catch(Exception e){label.setText("Could not open scene: "+e.getMessage());}
  if(saved!=null&&saved.getInt("active_scene",0)!=0&&session!=0){try{loadChapter(saved.getInt("active_scene",0));}catch(Exception e){label.setText(e.getMessage());}}
  if(saved!=null&&saved.getBoolean("browser_open",false)){openBrowser(-1,0);if(browser!=null&&saved.getIntArray("browser_state")!=null){browser.restore(saved.getIntArray("browser_state"));if(browser.info()[0]==2&&saved.getIntArray("browser_walk")!=null)browser.restoreWalk(saved.getIntArray("browser_walk"));browserPanel.update();}}
 }
 private void copy(String asset,File target)throws IOException{
  try(InputStream in=getAssets().open(asset);OutputStream out=new FileOutputStream(target)){byte[] bytes=new byte[65536];int n;while((n=in.read(bytes))!=-1)out.write(bytes,0,n);}
 }
 private void copyTree(String asset,File target)throws IOException{
  String[] names=getAssets().list(asset);if(names==null)throw new IOException("Could not load or update resources");
  if(names.length==0){copy(asset,target);return;}
  if(!target.isDirectory()&&!target.mkdirs())throw new IOException("Could not load or update resources");
  for(String name:names)copyTree(asset+"/"+name,new File(target,name));
 }
 private Button control(LinearLayout row,String text,int mask){
  Button b=new Button(this);b.setText(text);b.setTextSize(12);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(2,0,2,0);b.setAlpha(.8f);row.addView(b,new LinearLayout.LayoutParams(dp(52),dp(52)));
  b.setOnTouchListener((v,event)->{int action=event.getActionMasked(),index=event.getActionIndex();if(action==MotionEvent.ACTION_DOWN||action==MotionEvent.ACTION_POINTER_DOWN){routeButton(mask,true,event.getPointerId(index));v.setPressed(true);}else if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_POINTER_UP){routeButton(mask,false,event.getPointerId(index));if(action==MotionEvent.ACTION_UP){v.setPressed(false);v.performClick();}}else if(action==MotionEvent.ACTION_CANCEL){routeButton(mask,false,event.getPointerId(index));v.setPressed(false);}return true;});return b;
 }
 private void closeSettings(){if(session!=0&&!ready&&!frontendOpen){leaveCampaign(true,false);return;}optionsPane.setVisibility(View.GONE);if(frontendOpen){gameControls.setVisibility(View.GONE);pauseSurface.setVisibility(View.VISIBLE);pauseSurface.refresh();if(resumed)pauseSurface.resume();}else setGamePaused(false);}
 private void openSettings(){if(browserOpen)return;qol("");if(!frontendOpen)setGamePaused(true);if(pauseSurface!=null){pauseSurface.pause();pauseSurface.setVisibility(View.GONE);}gameControls.setVisibility(View.VISIBLE);optionsPane.setVisibility(View.VISIBLE);settingsCursor=1;settingsActions.getChildAt(settingsCursor).requestFocus();}
 private static native void cancelShoulderGesture(long h);
 private void clearInput(){if(session!=0)cancelShoulderGesture(session);if(mapEditor!=null)mapEditor.releaseInput();heldKeys.clear();analogMask=0;inputs.clear();controllerInputs.clear();controllerMask=buttons=0;}
 private void routeButton(int mask,boolean down,int pointer){if(mapEditor!=null){mapEditor.input(mask,down);return;}if(mask==4096||mask==1024||mask==2048){if(down){if(mask==4096)openSettings();else if(mask==1024)quickLoad();else quickSave();}return;}if(down)controllerInputs.press(pointer,mask);else controllerInputs.release(pointer);controllerMask=controllerInputs.held();
  if(down&&((mask==8&&(controllerMask&4)!=0)||(mask==4&&(controllerMask&8)!=0))){openSettings();return;}
  if(optionsPane.getVisibility()==View.VISIBLE){if(!down)return;if(mask==2||mask==8){closeSettings();return;}if(mask==1){settingsActions.getChildAt(settingsCursor).performClick();return;}if(mask==64||mask==128){int count=settingsActions.getChildCount();do{settingsCursor=(settingsCursor+(mask==128?1:count-1))%count;}while(!(settingsActions.getChildAt(settingsCursor) instanceof Button));settingsActions.getChildAt(settingsCursor).requestFocus();}return;}
  if(browserOpen)return;if(frontendOpen||menuOpen){if(pauseSurface!=null)pauseSurface.held(mask,(controllerMask&mask)!=0);return;}
  if(mask==8){if(down){if(session!=0&&isDialogueActive(session))pendingDialogSkip=true;else setGamePaused(true);}return;}
  if(session!=0&&isDialogueActive(session)&&mask!=1){if(!down)inputs.releaseMask(mask);return;}
  if(down)inputs.press(pointer,mask);else inputs.release(pointer);
 }
 private int keyMask(int key){int original=defaultKeyMask(key);return controls==null?original:controls.pad(key,original);}
 private static int defaultKeyMask(int key){switch(key){case android.view.KeyEvent.KEYCODE_BUTTON_L2:return 1024;case android.view.KeyEvent.KEYCODE_BUTTON_R2:return 2048;case android.view.KeyEvent.KEYCODE_BUTTON_A:case android.view.KeyEvent.KEYCODE_ENTER:case android.view.KeyEvent.KEYCODE_DPAD_CENTER:return 1;case android.view.KeyEvent.KEYCODE_BUTTON_B:return 2;case android.view.KeyEvent.KEYCODE_BUTTON_SELECT:return 4;case android.view.KeyEvent.KEYCODE_BUTTON_START:return 8;case android.view.KeyEvent.KEYCODE_DPAD_RIGHT:return 16;case android.view.KeyEvent.KEYCODE_DPAD_LEFT:return 32;case android.view.KeyEvent.KEYCODE_DPAD_UP:return 64;case android.view.KeyEvent.KEYCODE_DPAD_DOWN:return 128;case android.view.KeyEvent.KEYCODE_BUTTON_R1:return 256;case android.view.KeyEvent.KEYCODE_BUTTON_L1:return 512;default:return 0;}}

 private void setGamePaused(boolean value){
  if(!value&&session!=0)resetPresentation(session);boolean wasPaused=menuOpen;menuOpen=value;clearInput();lastFrame=elapsed=0;optionsPane.setVisibility(View.GONE);if(session!=0&&ready&&!frontendOpen){int width=gameWidth();if(value){if(!wasPaused){pausedScene=view.pixels==null?null:view.pixels.clone();pausedSceneWidth=view.frame.getWidth();}view.setPixels(pauseFrame(session,width,true),width);}else{view.setPixels(pausedScene!=null&&pausedSceneWidth==width?pausedScene:pauseFrame(session,width,false),width);pausedScene=null;}}
  if(pauseSurface!=null){if(value){pauseMenu.open(5,0);pauseSurface.setVisibility(View.VISIBLE);pauseSurface.refresh();pauseSurface.resume();pauseSurface.requestFocus();}else{pauseSurface.pause();pauseSurface.setVisibility(View.GONE);}}else optionsPane.setVisibility(value?View.VISIBLE:View.GONE);
  if(audio!=null){audio.setMenuPaused(value);if(resumed)audio.resume();}
 }
 private void leaveCampaign(boolean main,boolean won){
  if(won&&session!=0&&standaloneBonusIndex(activeScene)<0){android.content.SharedPreferences save=getSharedPreferences("campaign",MODE_PRIVATE);int collected=readCoinCount(session),chapter=chapterOrdinal(activeScene);int best=Math.max(save.getInt("slot_"+campaignSlot+"_coins",0),collected);save.edit().putInt("slot_"+campaignSlot+"_chapter_0_coins",save.getInt("slot_"+campaignSlot+"_chapter_0_coins",save.getInt("slot_"+campaignSlot+"_coins",0))).putInt("slot_"+campaignSlot+"_chapter_"+chapter+"_coins",Math.max(save.getInt("slot_"+campaignSlot+"_chapter_"+chapter+"_coins",0),collected)).putBoolean("slot_"+campaignSlot+"_used",true).putInt("slot_"+campaignSlot+"_complete",save.getInt("slot_"+campaignSlot+"_complete",0)|(1<<chapterOrdinal(activeScene))).putInt("slot_"+campaignSlot+"_coins",best).apply();}
  if(frontendEnabled){ready=false;clearInput();menuOpen=false;frontendOpen=true;completionPending=false;pendingDialogSkip=false;lastFrame=elapsed=0;optionsPane.setVisibility(View.GONE);gameControls.setVisibility(View.GONE);reloadProgress();int[] state=pauseMenu.state();state[0]=main?1:4;state[1]=main?0:menuOrdinal(activeScene)%5;state[2]=main?0:menuOrdinal(activeScene)/5;state[4]=0;pauseMenu.restore(state);if(won)pauseMenu.epilogue(activeScene);pauseSurface.overlay=false;pauseSurface.setVisibility(View.VISIBLE);pauseSurface.refresh();pauseSurface.requestFocus();if(resumed)pauseSurface.resume();if(audio!=null){audio.setFrontendBoot(false);audio.setFrontendMode(true);audio.setMenuPaused(false);if(resumed)audio.resume();}return;}
  ready=false;clearInput();setResult(RESULT_OK,new android.content.Intent().putExtra("main_menu",main));finish();
 }
 @Override public boolean dispatchKeyEvent(android.view.KeyEvent event){if(bindingAction!=0||keyMask(event.getKeyCode())!=0||event.getKeyCode()==android.view.KeyEvent.KEYCODE_BUTTON_L2||event.getKeyCode()==android.view.KeyEvent.KEYCODE_BUTTON_R2){if(event.getAction()==android.view.KeyEvent.ACTION_DOWN)return onKeyDown(event.getKeyCode(),event);if(event.getAction()==android.view.KeyEvent.ACTION_UP)return onKeyUp(event.getKeyCode(),event);}return super.dispatchKeyEvent(event);}
 @Override public boolean onKeyDown(int key,android.view.KeyEvent event){if(bindingAction!=0&&key!=android.view.KeyEvent.KEYCODE_BACK){if(event.getRepeatCount()==0){controls.bind(key,bindingAction);bindingAction=0;clearInput();note("Gamepad button assigned");qol("Gamepad mapping");}return true;}if(session==0)return super.onKeyDown(key,event);int mask=keyMask(key);if(mask!=0){if(event.getRepeatCount()==0){heldKeys.put(key,mask);routeButton(mask,true,-key-100);}return true;}return super.onKeyDown(key,event);}
 @Override public boolean onKeyUp(int key,android.view.KeyEvent event){Integer held=heldKeys.remove(key);int mask=held==null?keyMask(key):held;if(mask!=0){routeButton(mask,false,-key-100);return true;}return super.onKeyUp(key,event);}
 @Override public void onBackPressed(){if(mapEditor!=null){closeMapEditor();return;}if(bindingAction!=0){bindingAction=0;qol("Gamepad mapping");return;}if(session==0){super.onBackPressed();return;}if(browserOpen){closeBrowser();return;}if(optionsPane.getVisibility()==View.VISIBLE){closeSettings();return;}if(noTouchControls()){openSettings();return;}if(frontendOpen){if(pauseMenu.state()[0]==1)super.onBackPressed();else pauseSurface.press(2);return;}if(menuOpen&&pauseSurface!=null){if(optionsPane.getVisibility()==View.VISIBLE)setGamePaused(false);else pauseSurface.press(2);}else setGamePaused(!menuOpen);}
 private void reloadProgress(){pauseMenu.testBooks(getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("test_books",false));android.content.SharedPreferences save=getSharedPreferences("campaign",MODE_PRIVATE);int[] p=new int[7];for(int i=0;i<3;i++){if(save.getBoolean("slot_"+i+"_used",false))p[0]|=1<<i;p[1+i]=save.getInt("slot_"+i+"_complete",0);p[4+i]=save.getInt("slot_"+i+"_coins",0);}pauseMenu.progress(p);int[] chapterCoins=new int[75];for(int i=0;i<3;i++)for(int j=0;j<25;j++)chapterCoins[i*25+j]=save.getInt("slot_"+i+"_chapter_"+j+"_coins",j==0?p[4+i]:0);pauseMenu.chapterCoins(chapterCoins);int[] bonusBests=new int[5];for(int i=0;i<5;i++)bonusBests[i]=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt(String.format(java.util.Locale.ROOT,"bonus_%02d_best",i),0);pauseMenu.bonusBests(bonusBests);StringBuilder names=new StringBuilder();for(int i=0;i<3;i++)names.append(save.getString("slot_"+i+"_name","AAA"));pauseMenu.names(names.toString());}
 static boolean playableChapter(int scene){return scene==0||scene==1||scene==2||scene==13||scene==17||scene==25||scene==14||scene==9||scene==11||scene==8||scene==4||scene==10||scene==23||scene==21||scene==29||scene==24||scene==3||scene==19||scene==22||scene==28||scene==12||scene==5||scene==20||scene==15||scene==16;}
 private static int standaloneBonusIndex(int scene){switch(scene){case 26:return 0;case 7:return 1;case 6:return 2;case 18:return 3;case 27:return 4;default:return -1;}}
 static boolean playableScene(int scene){return playableChapter(scene)||standaloneBonusIndex(scene)>=0;}
 private static int menuOrdinal(int scene){int bonus=standaloneBonusIndex(scene);return bonus<0?chapterOrdinal(scene):25+bonus;}
 private static int chapterOrdinal(int scene){switch(scene){case 0:return 0;case 1:return 1;case 2:return 2;case 13:return 3;case 17:return 4;case 25:return 5;case 14:return 6;case 9:return 7;case 11:return 8;case 8:return 10;case 4:return 11;case 10:return 12;case 23:return 13;case 21:return 14;case 29:return 15;case 24:return 16;case 3:return 17;case 19:return 18;case 22:return 19;case 28:return 21;case 12:return 22;case 5:return 9;case 20:return 20;case 15:return 23;case 16:return 24;default:throw new IllegalArgumentException("Unknown chapter");}}
 private void loadChapter(int scene){menuOrdinal(scene);pausedScene=null;editBaselineReady=false;try{File base=new File(getFilesDir(),"native_session"),folder=scene==0?base:new File(base,String.format(java.util.Locale.ROOT,"chapter_%02d",scene));if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Could not load or update resources");copy(String.format(java.util.Locale.ROOT,"scenes/scene_%02d.s2lv",scene),new File(folder,"scene.s2lv"));copy(String.format(java.util.Locale.ROOT,"collision/scene_%02d.s2cl",scene),new File(folder,"collision.s2cl"));copy(String.format(java.util.Locale.ROOT,"objects/scene_%02d.s2ob",scene),new File(folder,"objects.s2ob"));for(String mini:new String[]{"minigame_00","minigame_01","minigame_02","minigame_03","minigame_04"})copyTree("session/"+mini,new File(folder,mini));loadWorldSession(session,new File(base,"resources.s2pk").getAbsolutePath(),new File(folder,"scene.s2lv").getAbsolutePath(),new File(folder,"collision.s2cl").getAbsolutePath(),new File(base,"sprites").getAbsolutePath(),new File(folder,"objects.s2ob").getAbsolutePath());activeScene=scene;savedBonusIndex=readBonusIndex(session);savedBonusBest=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt(String.format(java.util.Locale.ROOT,"bonus_%02d_best",savedBonusIndex),0);setBonusBest(session,savedBonusBest);setBonusResults(session,false);setPussDoubleJump(session,getSharedPreferences("SessionActivity",MODE_PRIVATE).getBoolean("puss_double_jump",false));if(audio!=null){audio.setChapterMusic(standaloneBonusIndex(scene)>=0?0:scene);applyLevelTrack();}}catch(IOException e){throw new IllegalStateException(e.getMessage(),e);}}
 private void showGameError(Exception error){qol("");ready=false;clearInput();pendingDialogSkip=completionPending=false;lastFrame=elapsed=0;menuOpen=frontendOpen=false;if(pauseSurface!=null){pauseSurface.pause();pauseSurface.setVisibility(View.GONE);}gameControls.setVisibility(View.VISIBLE);optionsPane.setVisibility(View.VISIBLE);settingsCursor=10;settingsActions.getChildAt(settingsCursor).requestFocus();label.setVisibility(View.VISIBLE);label.setText(error.getMessage());if(audio!=null){audio.reset();audio.setMenuPaused(true);audio.setFrontendBoot(false);audio.setFrontendMode(false);}}
 private void resumeGameFrames(){if(resumed){Choreographer.getInstance().removeFrameCallback(this);Choreographer.getInstance().postFrameCallback(this);}}
 private static boolean fixedArena(int scene){return scene==5||scene==15||scene==16||scene==17||scene==20||scene==26||scene==7||scene==6||scene==18||scene==27;}
 private int gameWidth(){boolean expanded=wide&&(arenaWide||(!fixedArena(activeScene)&&(session==0||readMinigameState(session)==0)));if(activeScene==16)expanded=false;view.fill=expanded;return Viewport.width(view.getWidth(),view.getHeight(),expanded);}
 private void enterChapter(int scene,int slot){try{loadChapter(scene);campaignSlot=slot;soundCursor=0;pendingDialogSkip=completionPending=false;clearInput();lastFrame=elapsed=0;attackButton.setEnabled(true);ready=true;int width=gameWidth();view.setPixels(advanceSession(session,0,width,160,info),width);label.setText(scene==0?"First chapter":scene==23?"Puss in Boots level":"Donkey level");label.setVisibility(View.GONE);pauseSurface.pause();pauseSurface.setVisibility(View.GONE);pauseSurface.overlay=true;frontendOpen=false;menuOpen=false;gameControls.setVisibility(View.VISIBLE);view.requestFocus();resumeGameFrames();if(audio!=null){audio.setMenuPaused(false);audio.setFrontendMode(false);audio.reset();audio.setBonusScene(standaloneBonusIndex(scene)>=0);if(resumed)audio.resume();}}catch(Exception e){showGameError(e);}}
 private void frontendAction(int action,int[] state){
  android.content.SharedPreferences save=getSharedPreferences("campaign",MODE_PRIVATE);int slot=state[3];
  if(action==11){enterChapter(state[5],slot);return;}
  if(action==10){pauseMenu.open(4,state[1]);openBrowser(state[5],0);}
  else if(action==9){if(audio!=null)audio.setFrontendBoot(false);}
  else if(action==7)save.edit().putBoolean("slot_"+slot+"_used",true).putString("slot_"+slot+"_name",pauseMenu.initials(slot)).apply();
  else if(action==6){android.content.SharedPreferences.Editor edit=save.edit().remove("slot_"+slot+"_used").remove("slot_"+slot+"_complete").remove("slot_"+slot+"_coins").remove("slot_"+slot+"_name");for(int chapter=0;chapter<25;chapter++)edit.remove("slot_"+slot+"_chapter_"+chapter+"_coins");edit.apply();reloadProgress();}
  else if(action==1&&session!=0){campaignSlot=slot;save.edit().putInt("selected_slot",slot).apply();if(activeScene!=0){loadChapter(0);}else restartSession(session);applyLevelTrack();soundCursor=0;pendingDialogSkip=completionPending=false;clearInput();lastFrame=elapsed=0;attackButton.setEnabled(true);ready=true;view.setPixels(advanceSession(session,0,gameWidth(),160,info),gameWidth());label.setVisibility(View.GONE);pauseSurface.pause();pauseSurface.setVisibility(View.GONE);pauseSurface.overlay=true;frontendOpen=false;gameControls.setVisibility(View.VISIBLE);view.requestFocus();resumeGameFrames();if(audio!=null){audio.setMenuPaused(false);audio.setFrontendMode(false);audio.reset();if(resumed)audio.resume();}}
 }
 @Override protected void onSaveInstanceState(Bundle out){super.onSaveInstanceState(out);out.putBoolean("browser_open",browserOpen);if(browser!=null){out.putIntArray("browser_state",browser.save());if(browser.info()[0]==2)out.putIntArray("browser_walk",browser.saveWalk());}out.putInt("active_scene",activeScene);out.putBoolean("frontend_open",frontendOpen);out.putInt("campaign_slot",campaignSlot);if(frontendOpen&&pauseMenu!=null)out.putIntArray("menu_state",pauseMenu.state());}
 private void openBrowser(int scene,int mode){
  try{
   if(browser==null){File folder=new File(getFilesDir(),"campaign_assets");copyTree("campaign",folder);browser=new CampaignBrowser(folder.getAbsolutePath());browserPanel=new CampaignPanel(this,browser,new CampaignPanel.Listener(){public void close(){closeBrowser();}public void launch(int scene){int slot=frontendOpen?pauseMenu.state()[3]:campaignSlot;closeBrowser();enterChapter(scene,slot);}public void song(int address){if(audio!=null)audio.setBrowserSong(address);}});browserPanel.setVisibility(View.GONE);rootFrame.addView(browserPanel,new FrameLayout.LayoutParams(-1,-1));}
   if(scene>=0)browser.select(scene);browser.mode(mode);browserOpen=true;clearInput();lastFrame=elapsed=0;gameControls.setVisibility(View.GONE);if(assetsEntry!=null)assetsEntry.setVisibility(View.GONE);if(pauseSurface!=null){pauseSurface.pause();pauseSurface.setVisibility(View.GONE);}browserPanel.setVisibility(View.VISIBLE);if(audio!=null){audio.setMenuPaused(false);audio.setBrowsing(true);}if(resumed)browserPanel.resume();else browserPanel.update();
  }catch(Exception e){if(browserPanel!=null)closeBrowser();browserOpen=false;label.setVisibility(View.VISIBLE);label.setText(e.getMessage());}
 }
 private void closeBrowser(){
  if(browserPanel!=null){browserPanel.pause();browserPanel.setVisibility(View.GONE);}browserOpen=false;lastFrame=elapsed=0;clearInput();if(audio!=null){audio.setBrowsing(false);audio.setMenuPaused(menuOpen);}
  if(frontendOpen){pauseSurface.setVisibility(View.VISIBLE);pauseSurface.refresh();if(resumed)pauseSurface.resume();pauseSurface.requestFocus();}else{gameControls.setVisibility(View.VISIBLE);if(menuOpen&&optionsPane.getVisibility()!=View.VISIBLE){pauseSurface.setVisibility(View.VISIBLE);if(resumed)pauseSurface.resume();}}
 }
 private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
 private void fullscreen(){
  if(Build.VERSION.SDK_INT>=28){WindowManager.LayoutParams attrs=getWindow().getAttributes();attrs.layoutInDisplayCutoutMode=WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;getWindow().setAttributes(attrs);}
  if(Build.VERSION.SDK_INT>=30){getWindow().setDecorFitsSystemWindows(false);WindowInsetsController c=getWindow().getInsetsController();if(c!=null){c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);c.hide(WindowInsets.Type.systemBars());}}
  else getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
 }
 @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);if(focus){fullscreen();refreshDisplay();if(resumed&&audio!=null)audio.resume();}else{clearInput();pendingDialogSkip=false;if(pauseSurface!=null)pauseSurface.releaseButtons();}}
 @Override public void doFrame(long time){
  if(!resumed)return;
  if(browserOpen||frontendOpen||menuOpen){lastFrame=elapsed=0;Choreographer.getInstance().postFrameCallback(this);return;}
  if(lastFrame!=0)elapsed+=Math.max(0,Math.min(time-lastFrame,STEP_NS*4));lastFrame=time;
  if(ready)try{
   int[] pixels=null;int count=0;
   int width=gameWidth();
   while(elapsed>=STEP_NS&&count<4){buttons=inputs.readForStep();if(standaloneBonusIndex(activeScene)>=0&&readMinigameState(session)==4){int best=readBonusBest(session);if(best>savedBonusBest)getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt(String.format(java.util.Locale.ROOT,"bonus_%02d_best",savedBonusIndex),best).apply();leaveCampaign(false,false);Choreographer.getInstance().postFrameCallback(this);return;}if(pendingDialogSkip){buttons|=64;pendingDialogSkip=false;}int deathsBefore=readDeathRestarts(session);boolean wasComplete=isLevelComplete(session);updateSession(session,buttons,width,info,speed);if(readDeathRestarts(session)!=deathsBefore){soundCursor=0;if(audio!=null)audio.deathRestart();}if(wasComplete&&!isLevelComplete(session)){soundCursor=0;if(audio!=null)audio.reset();}elapsed-=STEP_NS;count++;if(campaign&&isLevelComplete(session)){completionPending=true;break;}}

   if(count>0||(requestedHz>60.5f&&smoothMotion)){if(displayPixels==null||displayPixels.length!=width*160)displayPixels=new int[width*160];presentSession(session,width,requestedHz>60.5f&&smoothMotion?RefreshPolicy.alpha(elapsed):256,displayPixels);pixels=displayPixels;view.setPixels(pixels,width);}
   if(count>0){
    if(audio!=null)audio.setFinaleMenuMusic(musicHint(session)!=0);
    int bonusIndex=readBonusIndex(session);
    if(bonusIndex!=savedBonusIndex){savedBonusIndex=bonusIndex;savedBonusBest=getSharedPreferences("SessionActivity",MODE_PRIVATE).getInt(String.format(java.util.Locale.ROOT,"bonus_%02d_best",bonusIndex),0);setBonusBest(session,savedBonusBest);}
    int miniState=readMinigameState(session);
    if(audio!=null)audio.setBonusScene(miniState==1||miniState==2||miniState==4);
    int best=readBonusBest(session);
    if(best>savedBonusBest){savedBonusBest=best;getSharedPreferences("SessionActivity",MODE_PRIVATE).edit().putInt(String.format(java.util.Locale.ROOT,"bonus_%02d_best",savedBonusIndex),best).apply();}
    boolean dialogue=isDialogueActive(session);
    if(skipDialogue.isEnabled()!=dialogue)skipDialogue.setEnabled(dialogue);
    if(label.getVisibility()!=View.GONE)label.setVisibility(View.GONE);
    // Do not rebuild hidden debug text every tick.
    // No Java array/native audio scan when the request cursor has not moved.
    if(soundHead(session)!=soundCursor){int[] sounds=readSessionSounds(session,soundCursor);soundCursor=sounds[0];if(audio!=null)for(int i=1;i<sounds.length;i+=3)audio.play(sounds[i],sounds[i+1],sounds[i+2]);}
   }
   if(completionPending){completionPending=false;leaveCampaign(false,true);}
  }catch(Exception e){showGameError(e);}
  if(resumed)Choreographer.getInstance().postFrameCallback(this);
 }
 @Override protected void onResume(){super.onResume();if(session==0||!RomAccess.require(this))return;resumed=true;layoutControls();refreshDisplay();if(browserOpen&&browserPanel!=null)browserPanel.resume();if(!browserOpen&&(frontendOpen||menuOpen)&&pauseSurface!=null&&pauseSurface.getVisibility()==View.VISIBLE)pauseSurface.resume();if(audio!=null)audio.resume();lastFrame=elapsed=0;Choreographer.getInstance().removeFrameCallback(this);Choreographer.getInstance().postFrameCallback(this);}
 @Override protected void onPause(){if(browserPanel!=null)browserPanel.pause();if(pauseSurface!=null)pauseSurface.pause();resumed=false;clearInput();lastFrame=elapsed=0;if(audio!=null)audio.pause();Choreographer.getInstance().removeFrameCallback(this);super.onPause();}
 @Override protected void onDestroy(){if(mapEditor!=null){mapEditor.dispose();mapEditor=null;}if(gamepads!=null)gamepads.unregisterInputDeviceListener(padListener);if(browserPanel!=null)browserPanel.pause();if(browser!=null){browser.close();browser=null;}if(pauseSurface!=null)pauseSurface.pause();if(pauseMenu!=null){pauseMenu.close();pauseMenu=null;}ready=false;if(audio!=null){audio.close();audio=null;}if(session!=0){destroySession(session);session=0;}super.onDestroy();}
 private static final class GameView extends View {
  private int[] pixels;private final RectF destination=new RectF();private Bitmap frame=Bitmap.createBitmap(240,160,Bitmap.Config.ARGB_8888);private final Paint paint=new Paint();boolean fill=true;
  GameView(Context context){super(context);paint.setFilterBitmap(false);setContentDescription("Shrek game scene");}
  void setPixels(int[] pixels,int width){this.pixels=pixels;if(frame.getWidth()!=width){Bitmap old=frame;frame=Bitmap.createBitmap(width,160,Bitmap.Config.ARGB_8888);old.recycle();}frame.setPixels(pixels,0,width,0,0,width,160);invalidate();}
  @Override protected void onDraw(Canvas canvas){super.onDraw(canvas);canvas.drawColor(0xff181818);float scale=Viewport.scale(getWidth(),getHeight(),frame.getWidth(),fill);float w=frame.getWidth()*scale,h=160*scale,x=(getWidth()-w)/2,y=(getHeight()-h)/2;destination.set(x,y,x+w,y+h);canvas.drawBitmap(frame,null,destination,paint);}
 }
}
