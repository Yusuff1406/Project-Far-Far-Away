#include <cstdint>
#include <algorithm>
#include <cstddef>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
// Original091A4, including equal bounds as an unlimited upper threshold.
extern "C" int s2_bonus_rewards(int level,int score,Fetch fetch,void* ctx,int32_t* out){
 if(!out||!fetch||level<0||level>=5)return -1;std::fill_n(out,4,0);int32_t p;if(!fetch(0x0804d820+uint32_t(level)*4,&p,1,ctx))return -2;int n=0;
 for(int i=0;i<64;i++){int32_t row[3];if(!fetch(uint32_t(p)+uint32_t(i)*12,row,3,ctx))return -2;if(!row[2])return n;if(score>=row[0]&&(score<=row[1]||row[1]<=row[0])){if(n>=4)return -3;out[n++]=row[2];}}return -3;
}
extern "C" int s2_fade_step(int32_t* s){if(!s||s[0]<0||s[0]>64||(s[1]!=0&&s[1]!=64))return -1;s[0]+=s[0]<s[1]?4:s[0]>s[1]?-4:0;s[0]=std::clamp(s[0],0,64);return 0;}
extern "C" int s2_fade_argb(int alpha,uint32_t* p,size_t n){if(!p||alpha<0||alpha>64)return -1;for(size_t i=0;i<n;i++){uint32_t c=p[i],k=64-alpha;p[i]=0xff000000u|((((c>>16)&255)*k/64)<<16)|((((c>>8)&255)*k/64)<<8)|((c&255)*k/64);}return 0;}

// GBA-like square mosaic. Sample the top-left pixel; never blur or stretch artwork.
extern "C" int s2_mosaic_argb(int amount,uint32_t* p,int width,int height){
 if(!p||amount<0||amount>64||width<1||height<1)return -1;int block=1+amount*15/64;
 for(int y=0;y<height;y+=block)for(int x=0;x<width;x+=block){uint32_t c=p[y*width+x];for(int yy=y;yy<std::min(y+block,height);yy++)for(int xx=x;xx<std::min(x+block,width);xx++)p[yy*width+xx]=c;}return 0;
}
