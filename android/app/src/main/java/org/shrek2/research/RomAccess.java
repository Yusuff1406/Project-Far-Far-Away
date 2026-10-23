package org.shrek2.research;

import android.app.Activity;
import android.content.Intent;

final class RomAccess {
 static boolean require(Activity activity){
  if(RomStore.valid(activity.getFilesDir()))return true;
  activity.startActivity(new Intent(activity,RomImportActivity.class));activity.finish();return false;
 }
}
