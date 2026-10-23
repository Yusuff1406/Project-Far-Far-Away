#include <cstdint>
#include <array>
#include <cstddef>
#include <algorithm>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
struct SpriteReader{
 std::vector<uint8_t> b;size_t p=0;
 explicit SpriteReader(const char* path){std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("Sprite file missing");b.assign(std::istreambuf_iterator<char>(f),{});}
 uint8_t byte(){if(p>=b.size())throw std::runtime_error("Truncated sprite");return b[p++];}
 uint16_t half(){uint16_t v=byte();return v|uint16_t(byte())<<8;}
 int16_t signed_half(){return int16_t(half());}
 uint32_t word(){uint32_t v=half();return v|uint32_t(half())<<16;}
 std::vector<uint8_t> data(uint32_t n){if(n>b.size()-p)throw std::runtime_error("Invalid sprite payload");auto it=b.begin()+p;std::vector<uint8_t> r(it,it+n);p+=n;return r;}
};
struct Animation{int rate,count,flags;int32_t bounds[4];std::vector<uint16_t> palette,sequence;std::array<uint32_t,16> colors{};};
struct Piece{int x,y;uint32_t shape;std::vector<uint8_t> pixels,unpacked;};
struct SpriteBank{std::vector<Animation> animations;std::vector<std::vector<Piece>> frames;};
static const int shapes[12][2]={{8,8},{16,16},{32,32},{64,64},{16,8},{32,8},{32,16},{64,32},{8,16},{8,32},{16,32},{32,64}};
SpriteBank load_sprite(const char* path){
 SpriteReader r(path);if(r.data(4)!=std::vector<uint8_t>{'S','2','S','P'}||r.word()!=1)throw std::runtime_error("Unknown sprite version");
 uint32_t na=r.word(),nf=r.word();if(!na||na>600||!nf||nf>10000)throw std::runtime_error("Invalid sprite counts");SpriteBank bank;
 for(uint32_t n=0;n<na;n++){
  Animation a;a.rate=r.byte();a.count=r.byte();a.flags=r.byte();r.byte();a.bounds[0]=r.signed_half();a.bounds[1]=r.signed_half();a.bounds[2]=r.byte();a.bounds[3]=r.byte();r.half();if(!a.count)throw std::runtime_error("Empty sequence");
  for(int i=0;i<16;i++){uint16_t c=r.half();a.palette.push_back(c);a.colors[i]=0xff000000u|(((c&31)*255/31)<<16)|((((c>>5)&31)*255/31)<<8)|(((c>>10)&31)*255/31);}
  for(int i=0;i<a.count;i++){uint16_t k=r.half();if(k>=nf)throw std::runtime_error("Invalid frame index");a.sequence.push_back(k);}bank.animations.push_back(std::move(a));
 }
 for(uint32_t n=0;n<nf;n++){
  r.data(8);uint32_t count=r.word();if(count>100)throw std::runtime_error("Invalid part count");std::vector<Piece> parts;
  for(uint32_t k=0;k<count;k++){Piece p;p.x=r.signed_half();p.y=r.signed_half();p.shape=r.word();uint32_t bytes=r.word();if(p.shape>=12||bytes!=uint32_t(shapes[p.shape][0]*shapes[p.shape][1]/2))throw std::runtime_error("Invalid part shape");p.pixels=r.data(bytes);int sw=shapes[p.shape][0],sh=shapes[p.shape][1];p.unpacked.resize(size_t(sw)*sh);for(int y=0;y<sh;y++)for(int x=0;x<sw;x++){size_t off=((y/8)*(sw/8)+x/8)*32+(y%8)*4+(x%8)/2;p.unpacked[size_t(y)*sw+x]=(p.pixels[off]>>((x&1)*4))&15;}parts.push_back(std::move(p));}bank.frames.push_back(std::move(parts));
 }
 if(r.p!=r.b.size())throw std::runtime_error("Trailing sprite data");return bank;
}
extern "C" int s2_sprite_info(const char* path,int animation,int32_t* out){
 try{auto b=load_sprite(path);if(!out||animation<0||size_t(animation)>=b.animations.size())return -1;auto& a=b.animations[animation];out[0]=int32_t(b.animations.size());out[1]=a.count;out[2]=a.rate;out[3]=a.flags;return 0;}catch(...){return -2;}
}
extern "C" int s2_sprite_render_file(const char* path,int animation,int sequenceIndex,int flip,int width,int height,int anchorX,int anchorY,uint8_t* out,size_t capacity){
 try{
  if(!out||width<=0||height<=0||uint64_t(width)*height>64000000||uint64_t(width)*height*4>capacity)return -1;
  auto bank=load_sprite(path);if(animation<0||size_t(animation)>=bank.animations.size())return -1;auto& a=bank.animations[animation];if(sequenceIndex<0||sequenceIndex>=a.count)return -1;
  std::fill(out,out+size_t(width)*height*4,0);
  for(const auto& p:bank.frames[a.sequence[sequenceIndex]]){
   int sw=shapes[p.shape][0],sh=shapes[p.shape][1];
   for(int y=0;y<sh;y++)for(int x=0;x<sw;x++){
    size_t offset=((y/8)*(sw/8)+x/8)*32+(y%8)*4+(x%8)/2;int index=(p.pixels[offset]>>((x&1)*4))&15;if(!index)continue;
    int dx=anchorX+(flip?-1-p.x-x:p.x+x),dy=anchorY+p.y+y;if(dx<0||dy<0||dx>=width||dy>=height)continue;
    uint16_t c=a.palette[index];size_t o=(size_t(dy)*width+dx)*4;out[o]=uint8_t((c&31)*255/31);out[o+1]=uint8_t(((c>>5)&31)*255/31);out[o+2]=uint8_t(((c>>10)&31)*255/31);out[o+3]=255;
   }
  }return 0;
 }catch(...){return -2;}
}

// Session-owned immutable bank, with no global cache or shared mutable state.
extern "C" void* s2_sprite_bank_create(const char* path){
 if(!path)return nullptr;try{return new SpriteBank(load_sprite(path));}catch(...){return nullptr;}
}
extern "C" void s2_sprite_bank_destroy(void* bank){delete static_cast<SpriteBank*>(bank);}
extern "C" int s2_sprite_bank_info(void* handle,int animation,int32_t* out){
 if(!handle||!out)return -1;auto& bank=*static_cast<SpriteBank*>(handle);if(animation<0||size_t(animation)>=bank.animations.size())return -1;
 const auto& a=bank.animations[size_t(animation)];int32_t row[8]={int(bank.animations.size()),a.count,a.rate,a.flags,a.bounds[0],a.bounds[1],a.bounds[2],a.bounds[3]};std::copy_n(row,8,out);return 0;
}
// Both source mirror bits are supported by the campaign artwork path.
extern "C" int s2_sprite_composite_transform(void* handle,int animation,int sequenceIndex,int mirror,int width,int height,int anchorX,int anchorY,uint32_t* out,size_t capacity){
 if(!handle||!out||mirror<0||mirror>3||width<1||height<1||width>640||height>256||capacity!=size_t(width)*height)return -1;
 auto& bank=*static_cast<SpriteBank*>(handle);if(animation<0||size_t(animation)>=bank.animations.size())return -1;auto& a=bank.animations[size_t(animation)];if(sequenceIndex<0||sequenceIndex>=a.count)return -1;
 for(const auto& p:bank.frames[a.sequence[size_t(sequenceIndex)]]){int sw=shapes[p.shape][0],sh=shapes[p.shape][1];
  int64_t left=int64_t(anchorX)+((mirror&1)?-p.x-sw:p.x),top=int64_t(anchorY)+((mirror&2)?-p.y-sh:p.y);if(left>=width||left+sw<=0||top>=height||top+sh<=0)continue;
  for(int y=0;y<sh;y++)for(int x=0;x<sw;x++){int64_t dx=int64_t(anchorX)+((mirror&1)?-1-p.x-x:p.x+x),dy=int64_t(anchorY)+((mirror&2)?-1-p.y-y:p.y+y);if(dx<0||dx>=width||dy<0||dy>=height)continue;
   int index=p.unpacked[size_t(y)*sw+x];if(index)out[size_t(dy)*width+size_t(dx)]=a.colors[index];
  }
 }return 0;
}
// Composite only opaque sprite pixels directly into the destination ARGB frame.
extern "C" int s2_sprite_composite_bank_palette(void* handle,int animation,int sequenceIndex,int flip,int width,int height,int anchorX,int anchorY,uint32_t* out,size_t capacity,int paletteAnimation){
 if(!handle||!out||width<=0||height<=0||uint64_t(width)*height>64000000||uint64_t(width)*height>capacity)return -1;
 auto& bank=*static_cast<SpriteBank*>(handle);if(animation<0||size_t(animation)>=bank.animations.size())return -1;if(paletteAnimation< -1||(paletteAnimation>=0&&size_t(paletteAnimation)>=bank.animations.size()))return -1;auto& a=bank.animations[animation];const auto& palette=paletteAnimation<0?a.colors:bank.animations[paletteAnimation].colors;if(sequenceIndex<0||sequenceIndex>=a.count)return -1;
 for(const auto& p:bank.frames[a.sequence[sequenceIndex]]){
  int sw=shapes[p.shape][0],sh=shapes[p.shape][1];
  int64_t left=int64_t(anchorX)+(flip?-p.x-sw:p.x),top=int64_t(anchorY)+p.y;
  if(left>=width||left+sw<=0||top>=height||top+sh<=0)continue;
  int x0=int(std::max<int64_t>(0,-left)),x1=int(std::min<int64_t>(sw,int64_t(width)-left)),y0=int(std::max<int64_t>(0,-top)),y1=int(std::min<int64_t>(sh,int64_t(height)-top));
  for(int y=y0;y<y1;y++){auto*dest=out+size_t(top+y)*width+size_t(left+x0);const auto*src=p.unpacked.data()+size_t(y)*sw;
   if(flip){for(int x=x0;x<x1;x++){int index=src[sw-1-x];if(index)dest[x-x0]=palette[index];}}
   else{for(int x=x0;x<x1;x++){int index=src[x];if(index)dest[x-x0]=palette[index];}}
  }

 }return 0;
}

extern "C" int s2_sprite_composite_bank(void* handle,int animation,int sequenceIndex,int flip,int width,int height,int anchorX,int anchorY,uint32_t* out,size_t capacity){return s2_sprite_composite_bank_palette(handle,animation,sequenceIndex,flip,width,height,anchorX,anchorY,out,capacity,-1);}

extern "C" int s2_sprite_bounds(const char* path,int animation,int32_t* out){
 try{auto b=load_sprite(path);if(!out||animation<0||size_t(animation)>=b.animations.size())return -1;std::copy_n(b.animations[animation].bounds,4,out);return 0;}catch(...){return -2;}
}
