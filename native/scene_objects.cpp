// Original scene spawn traversal at 0x08007084; constructors remain external.
#include <cstdint>
#include <cstddef>
#include <fstream>
#include <vector>
#include <stdexcept>
#include <algorithm>
#include "object_categories.inc"
extern "C" int s2_object_category(int type){return type>=0&&type<158?object_categories[type]:11;}
struct ObjectReader{
 std::vector<uint8_t> b;size_t p=0;
 explicit ObjectReader(const char* path){if(!path)throw std::runtime_error("Missing path");std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("Missing object file");b.assign(std::istreambuf_iterator<char>(f),{});}
 uint16_t half(){if(p+2>b.size())throw std::runtime_error("Truncated object file");uint16_t v=b[p]|uint16_t(b[p+1])<<8;p+=2;return v;}
 uint32_t word(){uint32_t v=half();return v|uint32_t(half())<<16;}
};
struct SpawnRow{int32_t v[8];int32_t params[8];};
static std::vector<SpawnRow> load_objects(const char* path){
 ObjectReader r(path);if(r.word()!=0x424f3253||r.word()!=1)throw std::runtime_error("Unsupported object format");uint32_t n=r.word();r.word();if(n>20000)throw std::runtime_error("Object count out of range");std::vector<SpawnRow> rows;
 for(uint32_t i=0;i<n;i++){
  SpawnRow row{};row.v[0]=int32_t(i+1);row.v[1]=r.half();row.v[2]=int32_t(r.half())*256;row.v[3]=int32_t(r.half())*256;r.half();row.v[4]=int32_t(r.word());uint32_t params[8];for(auto& v:params)v=r.word();for(int j=0;j<8;j++)row.params[j]=int32_t(params[j]);row.v[5]=int32_t(params[0]&255);row.v[6]=int32_t(params[2]);row.v[7]=int16_t(params[3]&65535);rows.push_back(row);
 }if(r.p!=r.b.size())throw std::runtime_error("Trailing object data");return rows;
}
// Output eight words per request: ID,type,anchorXQ8,anchorYQ8,paramROM,flags,tag,secondary.
// A set removal bit suppresses creation; ID still equals original row index+1.
extern "C" int s2_scene_spawn_plan_file(const char* path,const uint32_t* removed,size_t words,int32_t* out,size_t capacity){
 try{if((!out&&capacity)||(!removed&&words))return -1;auto rows=load_objects(path);if(removed&&words<(rows.size()+32)/32)return -1;int n=0;
  for(const auto& row:rows){uint32_t id=uint32_t(row.v[0]);if(removed&&((removed[id/32]>>(id%32))&1))continue;if(size_t(n)<capacity)std::copy_n(row.v,8,out+n*8);n++;}return n;
 }catch(...){return -2;}
}
// Original 0x08006F0C / 0x08007014 count both primary and secondary type.
extern "C" int s2_scene_type_count_file(const char* path,int type,int byCategory){
 try{auto rows=load_objects(path);int n=0;for(const auto& row:rows){int a=row.v[1],b=row.v[7];if(byCategory){a=s2_object_category(a);b=s2_object_category(b);}if(a==type)n++;if(b==type)n++;}return n;}catch(...){return -2;}
}

extern "C" int s2_scene_object_params_file(const char* path,int id,int32_t* out){
 if(!path||!out||id<1)return -1;try{auto rows=load_objects(path);if(size_t(id)>rows.size())return -2;std::copy_n(rows[size_t(id)-1].params,8,out);return 0;}catch(...){return -2;}
}
