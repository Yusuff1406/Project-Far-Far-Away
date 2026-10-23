package org.shrek2.research;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
// Physical pointer ownership and a one-tick latch for short A+B overlaps.
final class TouchButtons {
 private final Map<Integer,Integer> pointers=new HashMap<>();
 private int held=0,pending=0,lastAction=0;private boolean comboPending=false;
 void press(int pointer,int mask){int before=held;pointers.put(pointer,mask);recompute();pending|=held&~before;if((mask&3)!=0)lastAction=mask&3;if((before&3)!=3&&(held&3)==3)comboPending=true;}
 void release(int pointer){pointers.remove(pointer);recompute();}
 void releaseMask(int mask){Iterator<Map.Entry<Integer,Integer>> it=pointers.entrySet().iterator();while(it.hasNext()){Map.Entry<Integer,Integer> p=it.next();int value=p.getValue()&~mask;if(value==0)it.remove();else p.setValue(value);}recompute();pending&=~mask;if((mask&3)!=0)comboPending=false;}
 void clear(){pointers.clear();held=0;pending=lastAction=0;comboPending=false;}
 int held(){return held;}
 int readForStep(){int taps=pending;pending=0;if((taps&3)==3&&!comboPending)taps=(taps&~3)|lastAction;int value=held|taps;if(comboPending){value|=3;comboPending=false;}return value;}
 private void recompute(){held=0;for(int mask:pointers.values())held|=mask;}
}
