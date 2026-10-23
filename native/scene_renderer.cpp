// Native resource renderer: no GBA CPU emulation and no gameplay implementation.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
struct Layer { uint32_t slot,bg,sx,sy,flags,w,h; std::vector<uint16_t> cells;std::vector<uint8_t> unpacked; };
struct Scene { uint32_t w,h; std::vector<uint16_t> palette; std::vector<uint8_t> gfx8,gfx4; std::vector<Layer> layers;std::array<uint32_t,256> colors{}; };
struct Reader {
 std::vector<uint8_t> bytes; size_t pos=0;
 explicit Reader(const std::string& path) { std::ifstream f(path,std::ios::binary); if(!f)throw std::runtime_error("Cannot open scene");bytes.assign(std::istreambuf_iterator<char>(f),{}); }
 uint8_t u8(){if(pos>=bytes.size())throw std::runtime_error("Truncated scene");return bytes[pos++];}
 uint16_t u16(){uint16_t a=u8();return a|uint16_t(u8())<<8;}
 uint32_t u32(){uint32_t a=u16();return a|uint32_t(u16())<<16;}
 std::vector<uint8_t> data(uint32_t n){if(n>bytes.size()-pos)throw std::runtime_error("Invalid payload size");auto begin=bytes.begin()+pos;std::vector<uint8_t> d(begin,begin+n);pos+=n;return d;}
};
static int rawSample(const Scene&,const Layer&,int,int);
Scene load_scene(const std::string& path){
 Reader r(path);auto magic=r.data(4);if(magic!=std::vector<uint8_t>{'S','2','L','V'}||r.u32()!=1)throw std::runtime_error("Unsupported scene format");
 Scene s;s.w=r.u32();s.h=r.u32();uint32_t n8=r.u32(),n4=r.u32(),count=r.u32();
 if(!s.w||!s.h||s.w>16384||s.h>16384||count>4||n8%64||n4%32)throw std::runtime_error("Invalid scene dimensions");
 for(int i=0;i<256;i++)s.palette.push_back(r.u16());s.gfx8=r.data(n8);s.gfx4=r.data(n4);
 for(uint32_t i=0;i<count;i++){
  Layer l;l.slot=r.u32();l.bg=r.u32();l.sx=r.u32();l.sy=r.u32();l.flags=r.u32();l.w=r.u32();l.h=r.u32();
  if(!l.w||!l.h||l.w>2048||l.h>2048||l.slot>3)throw std::runtime_error("Invalid layer");
  for(uint32_t j=0;j<l.w*l.h;j++)l.cells.push_back(r.u16());s.layers.push_back(std::move(l));
 }
 if(r.pos!=r.bytes.size())throw std::runtime_error("Trailing scene data");
 for(int i=0;i<256;i++){uint16_t c=s.palette[i];s.colors[i]=0xff000000u|(((c&31)*255/31)<<16)|((((c>>5)&31)*255/31)<<8)|(((c>>10)&31)*255/31);}
 size_t budget=32*1024*1024;for(auto& l:s.layers){size_t size=size_t(l.w)*l.h*64;if(size>budget)continue;l.unpacked.resize(size);budget-=size;for(uint32_t y=0;y<l.h*8;y++)for(uint32_t x=0;x<l.w*8;x++){int p=rawSample(s,l,x,y);l.unpacked[size_t(y)*l.w*8+x]=p<0?0:uint8_t(p);}}
 return s;
}
// Returns palette index or -1 for transparency. Flag meanings remain subject to
// in-game comparison; all indices have been checked against bank lengths.
static int rawSample(const Scene& s,const Layer& l,int x,int y){
 if(x<0||y<0||x>=int(l.w*8)||y>=int(l.h*8))return -1;
 uint16_t word=l.cells[(y/8)*l.w+x/8];uint32_t tile=word&0xfff;int px=x%8,py=y%8;
 if(word&0x1000)px=7-px;if(word&0x2000)py=7-py;
 if(l.flags&0x10000){
  size_t off=size_t(tile)*64+py*8+px;if(off>=s.gfx8.size())throw std::runtime_error("8bpp tile outside bank");
  int p=s.gfx8[off];return p?p:-1;
 }
 size_t off=size_t(tile)*32+py*4+px/2;if(off>=s.gfx4.size())throw std::runtime_error("4bpp tile outside bank");
 int p=(s.gfx4[off]>>((px&1)*4))&15;return p?p+(word>>14)*16:-1;
}
int sample(const Scene& s,const Layer& l,int x,int y){if(x<0||y<0||x>=int(l.w*8)||y>=int(l.h*8))return -1;if(l.unpacked.empty())return rawSample(s,l,x,y);int p=l.unpacked[size_t(y)*l.w*8+x];return p?p:-1;}
// Draw directly into ARGB; foreground compositing keeps the existing pixels.
static void composite_scene(const Scene& s,int cx,int cy,int w,int h,uint32_t* out,int priority=-1){
 std::array<const Layer*,4> order{};size_t count=0;for(auto& l:s.layers)if(priority<0||int(l.bg)==priority)order[count++]=&l;
 // At most four layers: stable insertion order avoids stable_sort's heap buffer.
 for(size_t i=1;i<count;i++){const Layer* layer=order[i];size_t j=i;while(j&&order[j-1]->bg<layer->bg){order[j]=order[j-1];--j;}order[j]=layer;}
 for(size_t i=0;i<count;i++){const auto& l=*order[i];int ox=int(int64_t(cx)*l.sx/256),oy=int(int64_t(cy)*l.sy/256),lw=int(l.w*8),lh=int(l.h*8);bool repeat=priority<0&&w>240&&l.slot==0;
  int y0=std::max(0,-oy),y1=std::min(h,lh-oy),x0=repeat?0:std::max(0,-ox),x1=repeat?w:std::min(w,lw-ox);
  int start=repeat?(ox+x0)%lw:ox+x0;if(start<0)start+=lw;
  for(int y=y0;y<y1;y++){auto*dest=out+size_t(y)*w;int x=x0,sx=start;while(x<x1){int span=repeat?std::min(x1-x,lw-sx):x1-x;
   if(l.unpacked.empty()){for(int k=0;k<span;k++){int p=rawSample(s,l,sx+k,oy+y);if(p>0)dest[x+k]=s.colors[p];}}
   else{const uint8_t*source=l.unpacked.data()+size_t(oy+y)*lw+sx;for(int k=0;k<span;k++){int p=source[k];if(p)dest[x+k]=s.colors[p];}}
   x+=span;sx=0;
  }}
 }
}
std::vector<uint8_t> render(const Scene& s,int cx,int cy,int width,int height,int slot,int repeatSlot=-1,int priority=-1){
 if(width<=0||height<=0||width>16384||height>16384||uint64_t(width)*height>64000000)throw std::runtime_error("Invalid output dimensions");
 std::vector<uint8_t> rgba(size_t(width)*height*4,0);std::vector<const Layer*> layers;
 for(const auto& l:s.layers)if((slot<0||int(l.slot)==slot)&&(priority<0||int(l.bg)==priority))layers.push_back(&l);
 // BG number interpreted as stacking order for this research renderer.
 std::stable_sort(layers.begin(),layers.end(),[](auto a,auto b){return a->bg>b->bg;});
 for(auto l:layers){
  int ox=slot<0?int(int64_t(cx)*l->sx/256):cx,oy=slot<0?int(int64_t(cy)*l->sy/256):cy;
  for(int y=0;y<height;y++)for(int x=0;x<width;x++){
   int px=ox+x;if(int(l->slot)==repeatSlot){int period=int(l->w*8);px=((px%period)+period)%period;}
   int p=sample(s,*l,px,oy+y);if(p<0)continue;uint16_t c=s.palette[p];size_t o=(size_t(y)*width+x)*4;
   rgba[o]=uint8_t((c&31)*255/31);rgba[o+1]=uint8_t(((c>>5)&31)*255/31);rgba[o+2]=uint8_t(((c>>10)&31)*255/31);rgba[o+3]=255;
  }
 }
 return rgba;
}
extern "C" int s2_render_file(const char* path,int cx,int cy,int w,int h,int slot,uint8_t* rgba,size_t capacity){
 try{if(!path||!rgba||w<=0||h<=0||uint64_t(w)*h*4>capacity)return -1;auto s=load_scene(path);auto out=render(s,cx,cy,w,h,slot);std::copy(out.begin(),out.end(),rgba);return 0;}catch(...){return -2;}
}
// Immutable scene owned by a map browser. Decoded once on selection, never per frame.
extern "C" void* s2_scene_create(const char* path){
 try{if(!path)return nullptr;return new Scene(load_scene(path));}catch(...){return nullptr;}
}
extern "C" void s2_scene_destroy(void* handle){delete static_cast<Scene*>(handle);}
extern "C" int s2_scene_dimensions(void* handle,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<Scene*>(handle);out[0]=int32_t(s.w);out[1]=int32_t(s.h);return 0;}
extern "C" int s2_scene_dimensions_file(const char* path,int32_t* out){try{if(!path||!out)return -1;auto s=load_scene(path);out[0]=int32_t(s.w);out[1]=int32_t(s.h);return 0;}catch(...){return -2;}}
extern "C" int s2_scene_render(void* handle,int cx,int cy,int w,int h,uint32_t* argb,size_t capacity){
 try{if(!handle||!argb||w<240||w>640||h!=160||capacity!=size_t(w)*h)return -1;
  std::fill_n(argb,capacity,0xff181818u);composite_scene(*static_cast<Scene*>(handle),cx,cy,w,h,argb);return 0;
 }catch(...){return -2;}
}
// Port presentation option: repeat an explicitly selected decorative layer horizontally.
// The original renderer entry point stays unchanged; this does not wrap collision or actors.
extern "C" int s2_render_file_background_repeat(const char* path,int cx,int cy,int w,int h,int slot,int repeatSlot,uint8_t* rgba,size_t capacity){
 try{if(!path||!rgba||w<=0||h<=0||repeatSlot<0||repeatSlot>3||uint64_t(w)*h*4>capacity)return -1;auto s=load_scene(path);auto out=render(s,cx,cy,w,h,slot,repeatSlot);std::copy(out.begin(),out.end(),rgba);return 0;}catch(...){return -2;}
}
#ifndef S2_LIBRARY_ONLY
int main(int argc,char** argv){
 try{
  if(argc!=8){std::cerr<<"Usage: scene_renderer SCENE OUTPUT.ppm CAMERA_X CAMERA_Y WIDTH HEIGHT SLOT(-1=composite)\n";return 1;}
  auto s=load_scene(argv[1]);int w=std::stoi(argv[5]),h=std::stoi(argv[6]);auto rgba=render(s,std::stoi(argv[3]),std::stoi(argv[4]),w,h,std::stoi(argv[7]));
  std::ofstream out(argv[2],std::ios::binary);if(!out)throw std::runtime_error("Cannot write image");out<<"P6\n"<<w<<" "<<h<<"\n255\n";
  for(size_t i=0;i<rgba.size();i+=4){if(rgba[i+3])out.write(reinterpret_cast<const char*>(&rgba[i]),3);else{char bg[3]={24,24,24};out.write(bg,3);}}
  if(!out)throw std::runtime_error("Failed image write");return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 2;}
}
#endif

extern "C" int s2_render_file_foreground(const char* path,int cx,int cy,int w,int h,uint8_t* rgba,size_t capacity){try{if(!path||!rgba||w<=0||h<=0||uint64_t(w)*h*4>capacity)return -1;auto s=load_scene(path);auto out=render(s,cx,cy,w,h,-1,-1,0);std::copy(out.begin(),out.end(),rgba);return 0;}catch(...){return -2;}}

extern "C" int s2_scene_camera_right(void* h,int width){if(!h||width<1)return 0;auto& s=*static_cast<Scene*>(h);int right=std::max(0,int(s.w)-width);for(auto& l:s.layers)if((l.slot!=0||width<=240)&&l.sx)right=std::min(right,std::max(0,(int(l.w*8)-width)*256/int(l.sx)));return right;}
extern "C" int s2_scene_render_front(void* handle,int cx,int cy,int w,int h,uint8_t* rgba,size_t capacity){try{if(!handle||!rgba||w<=0||h<=0||uint64_t(w)*h*4>capacity)return -1;auto out=render(*static_cast<Scene*>(handle),cx,cy,w,h,-1,-1,0);std::copy(out.begin(),out.end(),rgba);return 0;}catch(...){return -2;}}

// Limit scrolling to finite map artwork, including the laboratory's last row.
extern "C" int s2_scene_camera_bottom(void* h,int height){if(!h||height<1)return 0;auto& s=*static_cast<Scene*>(h);int bottom=std::max(0,int(s.h)-height);for(auto& l:s.layers)if(l.slot!=0&&l.sy)bottom=std::min(bottom,std::max(0,(int(l.h*8)-height)*256/int(l.sy)));return bottom;}

extern "C" int s2_scene_composite_front(void*handle,int cx,int cy,int w,int h,uint32_t*out,size_t capacity){try{if(!handle||!out||w<=0||h<=0||size_t(w)*h>capacity)return -1;composite_scene(*static_cast<Scene*>(handle),cx,cy,w,h,out,0);return 0;}catch(...){return -2;}}

// Wider/taller read-only canvas used by the paused map editor's zoom controls.
extern "C" int s2_scene_render_editor(void*handle,int cx,int cy,int w,int h,uint32_t*out,size_t capacity){try{if(!handle||!out||w<60||w>1280||h<40||h>640||capacity!=size_t(w)*h)return -1;std::fill_n(out,capacity,0xff181818u);composite_scene(*static_cast<Scene*>(handle),cx,cy,w,h,out);return 0;}catch(...){return -2;}}
