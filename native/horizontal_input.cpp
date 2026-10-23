// Original directional-parameter logic at 0x0800DE8C, static-world subset.
#include <cstdint>
#include <cstddef>
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_horizontal_input_file(const char* path,int buttons,const int32_t* position,int width,int height,int32_t* parameters,const int32_t* contacts,int32_t* facing){
 if(!path||!position||!parameters||!contacts||!facing||width<1||width>255||height<1||height>255)return -1;
 const int32_t idle[3]={0,0,0};
 if(buttons&32){
  *facing=1;int32_t left=int32_t(uint32_t(position[0])-uint32_t(width*128)-256u),top=int32_t(uint32_t(position[1])-uint32_t(height*128));int hit=s2_static_probe_q8(path,1,left,top,256,height*256);if(hit<0)return hit;
  if(hit)return s2_apply_axis_triple(parameters,idle,0,0);
  if(-435<parameters[3]){parameters[4]=51;parameters[5]=-435;}
 }else if(buttons&16){
  *facing=0;int32_t right=int32_t(uint32_t(position[0])+uint32_t(width*128)),top=int32_t(uint32_t(position[1])-uint32_t(height*128));int hit=s2_static_probe_q8(path,2,right,top,256,height*256);if(hit<0)return hit;
  if(hit)return s2_apply_axis_triple(parameters,idle,0,0);
  if(parameters[3]<435){parameters[4]=51;parameters[5]=435;}
 }else{
  if(contacts[1]||contacts[2])return s2_apply_axis_triple(parameters,idle,0,0);
  parameters[4]=0;
 }
 return 0;
}
