package org.shrek2.research;
final class GamepadAxes {
 static int mask(float x,float y,float hx,float hy,float deadzone){int m=0;float dx=Math.abs(hx)>.5f?hx:x,dy=Math.abs(hy)>.5f?hy:y;if(dx>deadzone)m|=16;else if(dx < -deadzone)m|=32;if(dy>deadzone)m|=128;else if(dy < -deadzone)m|=64;return m;}
}
