package org.shrek2.research;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import java.io.InputStream;

/** Only exported entry point. Verification and copying run off the UI thread. */
public final class RomImportActivity extends Activity {
 private static final int PICK_ROM=100;
 private TextView status;private Button choose;private boolean busy,launched;private volatile boolean destroyed;
 @Override public void onCreate(Bundle saved){
  super.onCreate(saved);LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(32,24,32,24);box.setBackgroundColor(0xff14191d);
  TextView title=new TextView(this);title.setText("Original game ROM required");title.setTextSize(24);title.setTextColor(0xffffffff);box.addView(title);
  TextView help=new TextView(this);help.setText("Select your unmodified "+RomStore.TITLE+" .gba file. A verified copy is stored on this device for future launches.\n\nExpected size: 8 MiB\nSHA-256: "+RomStore.SHA256);help.setTextSize(14);help.setTextColor(0xffc7ced4);box.addView(help);
  status=new TextView(this);status.setTextSize(14);status.setTextColor(0xffffd275);status.setPadding(0,16,0,16);box.addView(status);
  choose=new Button(this);choose.setText("Import original .gba");choose.setOnClickListener(v->pick());box.addView(choose);
  Button exit=new Button(this);exit.setText("Exit");exit.setOnClickListener(v->finish());box.addView(exit);
  ScrollView scroll=new ScrollView(this);scroll.addView(box);setContentView(scroll);checkStored();
 }
 private void checking(String text){busy=true;choose.setEnabled(false);status.setText(text);}
 private void result(String error){if(destroyed||isFinishing())return;busy=false;choose.setEnabled(true);if(error==null){if(!launched){launched=true;startActivity(new Intent(this,FrontendActivity.class));finish();}}else status.setText(error);}
 private void checkStored(){checking("Checking stored ROM…");new Thread(()->{boolean valid=RomStore.valid(getFilesDir());runOnUiThread(()->result(valid?null:"Select the original ROM to continue."));},"rom-check").start();}
 private void pick(){if(busy)return;checking("Select an uncompressed .gba file…");try{Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("*/*");startActivityForResult(intent,PICK_ROM);}catch(RuntimeException e){result("No file picker is available. Install or enable a document provider and try again.");}}
 @Override protected void onActivityResult(int request,int code,Intent data){super.onActivityResult(request,code,data);if(request!=PICK_ROM)return;if(code!=RESULT_OK||data==null||data.getData()==null){result("Import cancelled. Select the original ROM to continue.");return;}checking("Verifying SHA-256 and importing ROM…");new Thread(()->{String error=null;try(InputStream in=getContentResolver().openInputStream(data.getData())){RomStore.importRom(getFilesDir(),in);}catch(Exception e){error=e.getMessage()==null?"Could not read the selected ROM.":e.getMessage();}final String message=error;runOnUiThread(()->result(message));},"rom-import").start();}
 @Override protected void onDestroy(){destroyed=true;super.onDestroy();}
}
