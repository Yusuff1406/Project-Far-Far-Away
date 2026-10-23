package org.shrek2.research;
public final class TouchButtonsTest {
 private static int checks=0;
 private static void check(TouchButtons t,int n){if(t.readForStep()!=n)throw new AssertionError(n);checks++;}
 public static void main(String[]args){TouchButtons t=new TouchButtons();check(t,0);t.press(7,1);check(t,1);t.press(19,2);check(t,3);t.release(7);check(t,2);t.release(19);check(t,0);
 t.press(8,1);t.press(11,2);t.release(8);t.release(11);check(t,3);check(t,0);
 t.press(2,2);t.press(4,1);t.release(2);check(t,3);check(t,1);t.clear();check(t,0);
 t.press(1,16);t.press(5,16);t.release(1);check(t,16);t.release(5);check(t,0);
 t.press(100,32);t.press(101,1);t.press(102,2);check(t,35);t.releaseMask(2);check(t,33);t.release(102);check(t,33);t.releaseMask(32);check(t,1);t.clear();check(t,0);
 t.press(0,1);t.press(1,2);t.clear();check(t,0);
 for(int i=0;i<500;i++){t.press(12,1);t.press(31,2);t.release(12);t.release(31);check(t,3);check(t,0);}
 t.press(1,2);t.release(1);check(t,2);check(t,0);t.press(1,4);t.release(1);check(t,4);check(t,0);t.press(1,1);t.release(1);t.press(2,2);t.release(2);check(t,2);check(t,0);
 System.out.println("TouchButtons checks="+checks+" mismatches=0");}
}
