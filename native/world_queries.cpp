// Original 0x15C24 / 0x15C90 / 0x15CDC / 0x15E40 / 0x15F50 and 0x7580.
#include <cstdint>
#include <algorithm>
using Bounds=int(*)(uint32_t,int32_t*,void*);
using Pair=void(*)(uint32_t,uint32_t,void*);
using Exclude=int(*)(uint32_t,void*);
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_actor_current_frame(const int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_actor_box_q8(const int32_t*,const int32_t*,int32_t*);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
// Envelope order: left,top,right,bottom. Original 18208: union body/frame + 4px.
extern "C" int s2_actor_envelope_q8(const int32_t* s,Fetch fetch,void* ctx,int32_t* out){
 if(!s||!fetch||!out)return -1;int32_t frame[11];int e=s2_actor_current_frame(s,fetch,ctx,frame);if(e)return e;
 int32_t box[4]={int16_t(uint32_t(frame[2])),int16_t(uint32_t(frame[2])>>16),int32_t(uint32_t(frame[3])&255),int32_t((uint32_t(frame[3])>>8)&255)},rect[4];s2_actor_box_q8(s,box,rect);
 int32_t x=sub(s[0],(s[30]&255)*128),y=sub(s[1],(s[31]&255)*128);
 out[0]=sub(std::min(x,rect[0]),1024);out[1]=sub(std::min(y,rect[1]),1024);out[2]=add(std::max(add(x,(s[30]&255)*256),add(rect[0],rect[2])),1024);out[3]=add(std::max(add(y,(s[31]&255)*256),add(rect[1],rect[3])),1024);return 0;
}
// 128 endpoint rows, each [signed X key, actor ID, opening byte]. Even count.
extern "C" int s2_sweep_add(uint32_t id,const int32_t* bounds,int32_t* endpoints,int32_t* count){
 if(!bounds||!endpoints||!count||*count<0||*count>128||(*count&1))return -1;if(*count==128)return 0;
 int32_t* p=endpoints+(*count)*3;p[0]=bounds[0];p[1]=int32_t(id);p[2]=1;p[3]=bounds[2];p[4]=int32_t(id);p[5]=0;*count+=2;return 1;
}
extern "C" int s2_sweep_remove(uint32_t id,int32_t* endpoints,int32_t* count){
 if(!endpoints||!count||*count<0||*count>128)return -1;int removed=0;
 for(int i=0;i<*count;)if(uint32_t(endpoints[i*3+1])==id){std::move(endpoints+(i+1)*3,endpoints+(*count)*3,endpoints+i*3);--*count;++removed;}else ++i;return removed;
}
extern "C" int s2_sweep_sort(int32_t* endpoints,int count){
 if(!endpoints||count<0||count>128)return -1;
 for(int i=1;i<count;i++){int32_t row[3];std::copy_n(endpoints+i*3,3,row);int j=i;while(j>0&&row[0]<endpoints[(j-1)*3]){std::copy_n(endpoints+(j-1)*3,3,endpoints+j*3);--j;}std::copy_n(row,3,endpoints+j*3);}return 0;
}
// Stable input frame only. Callback owns virtual dispatch/this adjustments/lifetime.
extern "C" int s2_sweep_run(int32_t* endpoints,int count,Bounds bounds,Pair pair,void* ctx){
 if(!endpoints||!bounds||!pair||count<0||count>128)return -1;if(!count)return 0;
 uint32_t active[16];int n=1,calls=0;active[0]=uint32_t(endpoints[1]);
 for(int i=1;i<count;i++){
  uint32_t id=uint32_t(endpoints[i*3+1]);
  if(endpoints[i*3+2]&255){
   for(int a=0;a<n;a++){int32_t current[4],other[4];if(!bounds(id,current,ctx)||!bounds(active[a],other,ctx))return -2;
    if(current[1]>other[3]||current[3]<other[1])continue;pair(id,active[a],ctx);pair(active[a],id,ctx);calls+=2;
   }if(n<16)active[n++]=id;
  }else{for(int a=0;a<n;a++)if(active[a]==id){active[a]=active[--n];break;}}
 }return calls;
}
extern "C" int s2_sweep_frame(int32_t* endpoints,int count,Bounds bounds,Pair pair,void* ctx){
 if(!endpoints||!bounds||!pair||count<0||count>128)return -1;
 for(int i=0;i<count;i++){int32_t b[4];if(!bounds(uint32_t(endpoints[i*3+1]),b,ctx))return -2;endpoints[i*3]=b[(endpoints[i*3+2]&255)?0:2];}
 int e=s2_sweep_sort(endpoints,count);return e?e:s2_sweep_run(endpoints,count,bounds,pair,ctx);
}
// Original active-category nearest list slots. Categories 10/11 have no route.
extern "C" int s2_nearest_category_slot(int category){static const int slots[10]={4,8,12,16,24,20,28,28,32,36};return category>=0&&category<10?slots[category]:-1;}
// Rows [ID,centerXQ8,centerYQ8], original list order. Filter true means excluded.
extern "C" int s2_world_nearest(const int32_t* pointPixels,const int32_t* rows,int n,Exclude exclude,void* ctx,uint32_t* selected){
 if(!pointPixels||(!rows&&n)||n<0||!exclude||!selected)return -1;*selected=0;int32_t best=0;const int32_t sentinel=0x0fffffff;
 for(int i=0;i<n;i++){const int32_t* row=rows+i*3;int32_t dx=sub(pointPixels[0],row[1]>>8),dy=sub(pointPixels[1],row[2]>>8);int32_t distance=int32_t(uint32_t(dx)*uint32_t(dx)+uint32_t(dy)*uint32_t(dy));
  if(exclude(uint32_t(row[0]),ctx)&255)distance=sentinel;if(i==0)best=distance;if(distance<=best&&distance!=sentinel){best=distance;*selected=uint32_t(row[0]);}
 }return 0;
}

// Original13B2C: marker-rectangle top-left, or actor center if absent.
extern "C" int s2_actor_spawn_point_q8(const int32_t* actor,Fetch fetch,void* ctx,int32_t* xy){
 if(!actor||!fetch||!xy)return -1;int32_t frame[11],metadata;
 int e=s2_actor_current_frame(actor,fetch,ctx,frame);if(e)return e;
 if(!fetch(uint32_t(frame[5]),&metadata,1,ctx))return -2;
 if(!((uint32_t(metadata)>>16)&255)){xy[0]=actor[0];xy[1]=actor[1];return 0;}
 int32_t packed[2],rect[4],box[4];if(!fetch(uint32_t(frame[8]),packed,2,ctx))return -2;
 box[0]=int16_t(uint32_t(packed[0]));box[1]=int16_t(uint32_t(packed[0])>>16);box[2]=uint32_t(packed[1])&255;box[3]=(uint32_t(packed[1])>>8)&255;
 e=s2_actor_box_q8(actor,box,rect);if(e)return e;xy[0]=rect[0];xy[1]=rect[1];return 0;
}

// Original generic queries71/72 after owner-selected nearest target.
// Target is center Q8, not pixels. Null means no eligible actor.
extern "C" int s2_actor_target_query(const int32_t* actor,const int32_t* target,int id,int32_t* out){
 if(!actor||!out)return -1;if(id!=71&&id!=72)return -4;
 if(!target){*out=id==71?90000:0;return 0;}
 if(id==72){*out=target[0]>actor[0]?1:2;return 0;}
 int32_t dx=sub(target[0],actor[0]),dy=sub(target[1],actor[1]);
 if(dx<0)dx=int32_t(0u-uint32_t(dx));if(dy<0)dy=int32_t(0u-uint32_t(dy));dx>>=8;dy>>=8;
 *out=int32_t(uint32_t(dx)*uint32_t(dx)+uint32_t(dy)*uint32_t(dy));return 0;
}

// Source051E0 /07B0: center in expanded camera rectangle, or forced flags.
extern "C" int s2_actor_camera_active(const int32_t* s,const int32_t* camera){
 if(!s||!camera)return -1;return (s[39]&8)||(s[40]&32)||(s[0]>=camera[0]&&s[1]>=camera[1]&&s[0]<=add(camera[0],camera[2])&&s[1]<=add(camera[1],camera[3]));
}
// D438 broadcasts original defeat packet when body is beyond the level bounds.
extern "C" int s2_actor_outside_world(const int32_t* s,int32_t width,int32_t height){
 if(!s)return -1;int w=(s[30]&255)*128,h=(s[31]&255)*128;return sub(s[1],h)>height||sub(s[0],w)>width||add(s[0],w)<0;
}
