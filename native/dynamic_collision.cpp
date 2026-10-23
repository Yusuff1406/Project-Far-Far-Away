// Original 0x08004768, using Stage 6 normalized nine-word surfaces.
#include <cstdint>
#include <algorithm>
extern "C" int s2_segment_rect(const int32_t*,const int32_t*);
extern "C" int s2_project_segment_q8(const int32_t*,const int32_t*,int,int32_t*);
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" void s2_motion_step(int32_t*,int32_t*);
extern "C" int s2_resolve_static_file(const char*,const int32_t*,int32_t*,int,int,int32_t*);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
static bool point_on(const int32_t* s,int32_t x,int32_t y){x>>=8;y>>=8;return x>=s[0]&&x<=s[2]&&y>=std::min(s[1],s[3])&&y<=std::max(s[1],s[3]);}
extern "C" int s2_resolve_dynamic(const int32_t* old,int32_t* pos,int w,int h,const int32_t* surfaces,int n,int32_t* counts,int32_t* accepted){
 if(!old||!pos||(!surfaces&&n)||!counts||(!accepted&&n)||w<0||w>255||h<0||h>255||n<0||n>16)return -1;
 const int32_t l=sub(pos[0],w*128),t=sub(pos[1],h*128),r=add(l,w*256),b=add(t,h*256);
 int32_t sweep[4][4]={{l,t,w*256,sub(old[1],t)},{l,add(old[1],old[3]),w*256,sub(b,add(old[1],old[3]))},{l,t,sub(old[0],l),h*256},{add(old[0],old[2]),t,sub(r,add(old[0],old[2])),h*256}};
 const int types[4]={5,3,1,2},counter[4]={3,0,1,2};
 for(int pass=0;pass<4;pass++){
  if(sweep[pass][pass<2?3:2]<=0)continue;int32_t box[4]={sweep[pass][0]>>8,sweep[pass][1]>>8,add(sweep[pass][0],sweep[pass][2])>>8,add(sweep[pass][1],sweep[pass][3])>>8};
  for(int i=0;i<n;i++){
   const int32_t* s=surfaces+i*9;if(s[4]!=types[pass]||!s2_segment_rect(s,box))continue;int32_t p[2];int code=s2_project_segment_q8(s,pos,pass<2?0:1,p);if(code)return code;
   int half=(pass<2?w:h)*128;bool ok=point_on(s,p[0],p[1]);
   if(pass<2)ok=ok||point_on(s,sub(p[0],half),p[1])||point_on(s,add(p[0],half),p[1]);
   else ok=ok||point_on(s,p[0],sub(p[1],half))||point_on(s,p[0],add(p[1],half));
   if(!ok)continue;accepted[i]=1;counts[counter[pass]]=add(counts[counter[pass]],1);
   if(pass==0)pos[1]=add(add(p[1],256),h*128);
   else if(pass==1){if(!s[5])return -2;pos[1]=sub(sub(p[1],256),h*128);pos[0]=add(pos[0],s[6]);pos[1]=add(pos[1],s[7]);}
   else if(pass==2)pos[0]=add(add(p[0],256),w*128);
   else pos[0]=sub(sub(p[0],256),w*128);
  }
 }return 0;
}
extern "C" int s2_actor_probe_file(const char* path,int type,int32_t x,int32_t y,int32_t w,int32_t h,const int32_t* surfaces,int n){
 if(!path||n<0||n>16||(!surfaces&&n))return -1;int hit=s2_static_probe_q8(path,type,x,y,w,h);if(hit)return hit;
 int32_t box[4]={x>>8,y>>8,add(x,w)>>8,add(y,h)>>8};for(int i=0;i<n;i++){const auto* s=surfaces+i*9;if(s[4]==type&&s2_segment_rect(s,box))return 1;}return 0;
}
extern "C" int s2_actor_move_dynamic_file(const char* path,int32_t* p,int32_t* pos,int32_t* old,int32_t* previous,int w,int h,const int32_t* surfaces,int n,int32_t* stat,int32_t* dyn,int32_t* accepted){
 if(!path||!p||!pos||!old||!previous||!stat||!dyn||n<0||n>16||(!surfaces&&n)||(!accepted&&n)||w<0||w>255||h<0||h>255)return -1;s2_motion_step(p,pos);std::fill(stat,stat+4,0);std::fill(dyn,dyn+4,0);if(accepted)std::fill(accepted,accepted+n,0);
 int c=s2_resolve_dynamic(old,pos,w,h,surfaces,n,dyn,accepted);if(c)return c;c=s2_resolve_static_file(path,old,pos,w,h,stat);if(c)return c;
 old[0]=sub(pos[0],w*128);old[1]=sub(pos[1],h*128);old[2]=w*256;old[3]=h*256;previous[0]=pos[0];previous[1]=pos[1];return (stat[0]||dyn[0])?3:0;
}
extern "C" int s2_horizontal_input_dynamic_file(const char* path,int buttons,const int32_t* pos,int w,int h,int32_t* p,const int32_t* contacts,int32_t* facing,const int32_t* surfaces,int n){
 if(!path||!p||!pos||!contacts||!facing||w<1||w>255||h<1||h>255||n<0||n>16||(!surfaces&&n))return -1;
 const int32_t idle[3]={0,0,0};
 if(buttons&48){int left=buttons&32;*facing=left?1:0;int32_t x=left?sub(sub(pos[0],w*128),256):add(pos[0],w*128);int hit=s2_actor_probe_file(path,left?1:2,x,sub(pos[1],h*128),256,h*256,surfaces,n);if(hit<0)return hit;
  if(hit){for(int i=0;i<6;i++)p[i]=0;return 0;}int target=left?-435:435;if(left?target<p[3]:p[3]<target){p[4]=51;p[5]=target;}
 }else if(contacts[1]||contacts[2]){for(int i=0;i<6;i++)p[i]=idle[i%3];}else p[4]=0;return 0;
}

extern "C" int s2_resolve_puss_static_file(const char*,const int32_t*,int32_t*,int,int,int32_t*,int32_t*,int);
extern "C" int s2_actor_move_puss_file(const char* path,int32_t* s,const int32_t* surfaces,int n,int32_t* rail,int allowRail){
 if(!path||!s||!rail||n<0||n>16||(!surfaces&&n))return -1;std::fill_n(rail,3,0);int32_t previous[2]={s[36],s[37]},accepted[16];s2_motion_step(s+2,s);std::fill_n(s+14,4,0);std::fill_n(s+64,4,0);std::fill_n(accepted,16,0);
 int e=s2_resolve_dynamic(s+32,s,s[30],s[31],surfaces,n,s+64,accepted);if(e)return e;
 e=s2_resolve_puss_static_file(path,s+32,s,s[30],s[31],s+14,rail,allowRail);if(e)return e;
 s[32]=sub(s[0],s[30]*128);s[33]=sub(s[1],s[31]*128);s[34]=s[30]*256;s[35]=s[31]*256;s[36]=s[0];s[37]=s[1];s[60]=sub(s[0],previous[0]);s[61]=sub(s[1],previous[1]);return(s[14]||s[64])?3:0;
}
