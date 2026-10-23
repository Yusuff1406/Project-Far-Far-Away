package org.shrek2.research;

/** Choose a supported refresh rate without changing physical resolution. */
final class RefreshPolicy {
 static float choose(int request,float[] rates){float best=0;for(float rate:rates)if(!Float.isNaN(rate)&&!Float.isInfinite(rate)&&rate>=30&&rate<=500&&(request==0||rate<=request+.6f))best=Math.max(best,rate);if(best==0)for(float rate:rates)if(!Float.isNaN(rate)&&!Float.isInfinite(rate)&&rate>=30&&rate<=500&&(best==0||rate<best))best=rate;return best==0?60:best;}
 static int alpha(long remainder){return (int)Math.max(0,Math.min(256,remainder*256/16666667L));}
}
