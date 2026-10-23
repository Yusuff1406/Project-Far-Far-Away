// Source B67C/B624 integer line traversal used by original menu widgets.
#include <cstdint>
#include <algorithm>
extern "C" int s2_menu_line_begin(int32_t* s,int x,int y,int tx,int ty){if(!s)return -1;s[0]=x;s[1]=y;s[2]=tx;s[3]=ty;s[7]=(tx>x)-(tx<x);s[8]=(ty>y)-(ty<y);int dx=tx-x,dy=ty-y;if(dx<0)dx=-dx;if(dy<0)dy=-dy;if(dy<=dx){s[4]=2*dy-dx;s[5]=2*dy;s[6]=2*(dy-dx);s[9]=1;}else{s[4]=2*dx-dy;s[5]=2*dx;s[6]=2*(dx-dy);s[9]=0;}return 0;}
extern "C" int s2_menu_line_step(int32_t* s){if(!s)return -1;if(s[0]==s[2]&&s[1]==s[3])return 1;if(s[9]){if(s[4]<=0)s[4]+=s[5];else{s[4]+=s[6];s[1]+=s[8];}s[0]+=s[7];}else{if(s[4]<=0)s[4]+=s[5];else{s[4]+=s[6];s[0]+=s[7];}s[1]+=s[8];}return s[0]==s[2]&&s[1]==s[3];}
