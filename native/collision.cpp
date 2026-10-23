// Static collision queries reconstructed from 0x08017A30/0x08017BC8.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <vector>
#include <string>
static int32_t wrap_sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
static int32_t wrap_add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t product_div(int32_t a,int32_t b,int32_t c){
 if(!c)throw std::runtime_error("Invalid clipping division");int32_t numerator=int32_t(uint32_t(a)*uint32_t(b));return int32_t(int64_t(numerator)/c);
}
static int outcode(int32_t x,int32_t y,const int32_t* r){int code=0;if(y>r[3])code|=1;else if(y<r[1])code|=2;if(x>r[2])code|=4;else if(x<r[0])code|=8;return code;}
extern "C" int s2_rect_overlap(const int32_t* a,const int32_t* b){if(!a||!b)return 0;return !(a[0]>b[2]||b[0]>a[2]||a[1]>b[3]||b[1]>a[3]);}
extern "C" int s2_segment_rect(const int32_t* segment,const int32_t* rect){
 if(!segment||!rect)return 0;int32_t x1=segment[0],y1=segment[1],x2=segment[2],y2=segment[3];
 if(x1>rect[2]||x2<rect[0])return 0;int a=outcode(x1,y1,rect),b=outcode(x2,y2,rect);
 for(int iteration=0;iteration<64;iteration++){
  if(a&b)return 0;if(!(a|b))return 1;int code=a?a:b;int32_t x,y;
  if(code&1){y=rect[3];x=wrap_add(x1,product_div(wrap_sub(x2,x1),wrap_sub(y,y1),wrap_sub(y2,y1)));}
  else if(code&2){y=rect[1];x=wrap_add(x1,product_div(wrap_sub(x2,x1),wrap_sub(y,y1),wrap_sub(y2,y1)));}
  else{x=(code&4)?rect[2]:rect[0];y=wrap_add(y1,product_div(wrap_sub(y2,y1),wrap_sub(x,x1),wrap_sub(x2,x1)));}
  if(code==a){x1=x;y1=y;a=outcode(x1,y1,rect);}else{x2=x;y2=y;b=outcode(x2,y2,rect);}
 }
 throw std::runtime_error("Collision clipping did not converge");
}
struct CollisionReader{
 std::vector<uint8_t> b;size_t p=0;
 explicit CollisionReader(const char* path){std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("Collision file missing");b.assign(std::istreambuf_iterator<char>(f),{});}
 uint32_t word(){if(p+4>b.size())throw std::runtime_error("Truncated collision data");uint32_t v=uint32_t(b[p])|(uint32_t(b[p+1])<<8)|(uint32_t(b[p+2])<<16)|(uint32_t(b[p+3])<<24);p+=4;return v;}
};
struct CollisionNode{int32_t box[4];uint32_t first,count;int32_t children[4];};
struct CollisionSegment{int32_t line[4];uint32_t type,romOffset,auxiliary;};
struct CollisionWorld{std::vector<CollisionNode> nodes;std::vector<CollisionSegment> segments;};
CollisionWorld load_collision(const char* path){
 CollisionReader r(path);if(r.word()!=0x4c433253||r.word()!=1)throw std::runtime_error("Invalid collision format");uint32_t nn=r.word(),ns=r.word();if(!nn||nn>20000||ns>20000)throw std::runtime_error("Invalid collision counts");CollisionWorld w;
 for(uint32_t i=0;i<nn;i++){CollisionNode n;for(auto& v:n.box)v=int32_t(r.word());n.first=r.word();n.count=r.word();if(uint64_t(n.first)+n.count>ns)throw std::runtime_error("Node segment range invalid");for(auto& v:n.children){v=int32_t(r.word());if(v< -1||v>=int32_t(nn))throw std::runtime_error("Child index invalid");}w.nodes.push_back(n);}
 for(uint32_t i=0;i<ns;i++){CollisionSegment s;for(auto& v:s.line)v=int32_t(r.word());s.type=r.word();s.romOffset=r.word();s.auxiliary=r.word();w.segments.push_back(s);}if(r.p!=r.b.size())throw std::runtime_error("Trailing collision data");return w;
}
// Session-scoped immutable collision data. Standalone file APIs still reload;
// a nested bonus session restores its parent's binding on scope exit.
struct CollisionHandle{std::string path;CollisionWorld world;};
static thread_local CollisionHandle* activeCollision=nullptr;
extern "C" void* s2_collision_create(const char* path){try{if(!path)return nullptr;return new CollisionHandle{path,load_collision(path)};}catch(...){return nullptr;}}
extern "C" void s2_collision_destroy(void* h){delete static_cast<CollisionHandle*>(h);}
extern "C" void* s2_collision_bind(void* h){auto* old=activeCollision;activeCollision=static_cast<CollisionHandle*>(h);return old;}
struct CollisionAccess{CollisionWorld owned;const CollisionWorld* p;explicit CollisionAccess(const char* path){if(path&&activeCollision&&activeCollision->path==path)p=&activeCollision->world;else{owned=load_collision(path);p=&owned;}}};
static void query_node(const CollisionWorld& w,int32_t ni,int type,const int32_t* box,std::vector<uint32_t>& hits,int depth){
 if(ni<0)return;if(depth>100)throw std::runtime_error("Collision recursion overflow");const auto& node=w.nodes[ni];if(!s2_rect_overlap(box,node.box))return;
 for(uint32_t k=0;k<node.count;k++){const auto& s=w.segments[node.first+k];if(s.type==uint32_t(type)&&s2_segment_rect(s.line,box))hits.push_back(s.romOffset);}
 for(int child:node.children)if(child>=0)query_node(w,child,type,box,hits,depth+1);
}
extern "C" int s2_collision_query_file(const char* path,int type,int32_t x1,int32_t y1,int32_t x2,int32_t y2,uint32_t* out,size_t capacity){
 try{if(!path||(!out&&capacity))return -1;CollisionAccess access(path);const auto& world=*access.p;int32_t box[4]={x1,y1,x2,y2};std::vector<uint32_t> hits;query_node(world,0,type,box,hits,0);std::copy_n(hits.begin(),std::min(capacity,hits.size()),out);return int(hits.size());}catch(...){return -2;}
}
extern "C" int s2_static_probe_q8(const char* path,int type,int32_t x,int32_t y,int32_t width,int32_t height){
 uint32_t first;int count=s2_collision_query_file(path,type,x>>8,y>>8,wrap_add(x,width)>>8,wrap_add(y,height)>>8,&first,1);return count<0?count:count!=0;
}
static int32_t wrap_mul(int32_t a,int32_t b){return int32_t(uint32_t(a)*uint32_t(b));}
static int32_t wrap_shift(int32_t a,int bits){return int32_t(uint32_t(a)<<bits);}
// Original 0x08017F9C and its two helpers; point is Q8, segment in pixels.
extern "C" int s2_project_segment_q8(const int32_t* line,const int32_t* point,int mode,int32_t* output){
 try{
  if(!line||!point||!output)return -1;int32_t x=point[0],y=point[1];int32_t dx=wrap_sub(line[2],line[0]),dy=wrap_sub(line[3],line[1]);
  if(!dx)x=wrap_shift(line[0],8);
  else if(!dy)y=wrap_shift(line[1],8);
  else{
   int32_t slope=int32_t(int64_t(wrap_shift(dy,16))/dx);
   if(!mode){
    int32_t xi=x>>8;if(xi>=line[0]&&xi<=line[2])y=wrap_add(wrap_shift(line[1],8),wrap_mul(slope,wrap_sub(x,wrap_shift(line[0],8)))>>16);
   }else{
    int32_t yi=y>>8;if(yi>=std::min(line[1],line[3])&&yi<=std::max(line[1],line[3])){
     if(!slope)return -2;int32_t value=int32_t(int64_t(wrap_shift(wrap_sub(y,wrap_shift(line[1],8)),16))/slope);x=wrap_add(wrap_shift(line[0],8),value);
    }
   }
  }
  output[0]=x;output[1]=y;return 0;
 }catch(...){return -2;}
}
// Visual diagnostic only: draw the extracted geometry over a viewport.
extern "C" int s2_collision_overlay_file(const char* path,int32_t cameraX,int32_t cameraY,int width,int height,uint8_t* out,size_t capacity){
 try{
  if(!out||width<=0||height<=0||uint64_t(width)*height*4>capacity)return -1;CollisionAccess access(path);const auto& world=*access.p;std::fill(out,out+size_t(width)*height*4,0);
  const uint8_t colors[7][3]={{255,255,255},{255,89,105},{84,178,255},{93,255,128},{255,204,80},{204,111,255},{80,230,230}};
  for(const auto& s:world.segments){
   int x=s.line[0]-cameraX,y=s.line[1]-cameraY,x2=s.line[2]-cameraX,y2=s.line[3]-cameraY;
   int dx=std::abs(x2-x),sx=x<x2?1:-1,dy=-std::abs(y2-y),sy=y<y2?1:-1,error=dx+dy;
   for(int n=0;n<50000;n++){
    if(x>=0&&y>=0&&x<width&&y<height){size_t off=(size_t(y)*width+x)*4;uint32_t c=s.type<=6?s.type:0;out[off]=colors[c][0];out[off+1]=colors[c][1];out[off+2]=colors[c][2];out[off+3]=255;}
    if(x==x2&&y==y2)break;int e2=2*error;if(e2>=dy){error+=dy;x+=sx;}if(e2<=dx){error+=dx;y+=sy;}
   }
  }return 0;
 }catch(...){return -2;}
}
static bool original_point_in_segment_box(const CollisionSegment& s,const int32_t* p){
 int32_t x=p[0]>>8,y=p[1]>>8;return x>=s.line[0]&&x<=s.line[2]&&y>=std::min(s.line[1],s.line[3])&&y<=std::max(s.line[1],s.line[3]);
}
static bool accepts_contact(const CollisionSegment& s,const int32_t* p,int kind,int width,int height){
 if(original_point_in_segment_box(s,p))return true;if(kind==4)return false;
 int32_t a[2]={p[0],p[1]},b[2]={p[0],p[1]};
 if(kind==1||kind==2){a[1]=wrap_sub(p[1],height*128);b[1]=wrap_add(p[1],height*128);}
 else{a[0]=wrap_sub(p[0],width*128);b[0]=wrap_add(p[0],width*128);}
 return original_point_in_segment_box(s,a)||original_point_in_segment_box(s,b);
}
static void resolve_contact_list(const CollisionWorld& w,int type,const int32_t* query,int32_t* point,int width,int height,int32_t* contacts,int32_t* rail=nullptr){
 std::vector<uint32_t> hits;query_node(w,0,type,query,hits,0);
 for(uint32_t offset:hits){
  auto it=std::find_if(w.segments.begin(),w.segments.end(),[offset](const auto& s){return s.romOffset==offset;});if(it==w.segments.end())throw std::runtime_error("Unknown contact");int32_t projected[2];
  if(s2_project_segment_q8(it->line,point,(type==1||type==2)?1:0,projected))throw std::runtime_error("Projection failed");
  if(!accepts_contact(*it,projected,type==6?4:type,width,height))continue;
  if(type==3||type==4||type==6){if(type==6&&rail){rail[0]=int32_t(it->auxiliary);rail[1]=wrap_sub(it->line[2],it->line[0]);rail[2]=wrap_sub(it->line[3],it->line[1]);}point[1]=wrap_sub(wrap_sub(projected[1],256),height*128);contacts[0]++;}
  else if(type==5){point[1]=wrap_add(wrap_add(projected[1],height*128),256);contacts[3]++;}
  else if(type==1){point[0]=wrap_add(wrap_add(projected[0],width*128),256);contacts[1]++;}
  else if(type==2){point[0]=wrap_sub(wrap_sub(projected[0],256),width*128);contacts[2]++;}
 }
}
static void rect_from_center(const int32_t* point,int width,int height,int32_t* rect){rect[0]=wrap_sub(point[0],width*128);rect[1]=wrap_sub(point[1],height*128);rect[2]=width*256;rect[3]=height*256;}
static void query_from_q8(const int32_t* area,int32_t* query){query[0]=area[0]>>8;query[1]=area[1]>>8;query[2]=wrap_add(area[0],area[2])>>8;query[3]=wrap_add(area[1],area[3])>>8;}
// Original static-only 0x08004098 with its base virtual methods. Old rect is
// Q8 left/top/width/height; current point is the new center in Q8.
static int resolve_static(const char* path,const int32_t* oldRect,int32_t* current,int width,int height,int32_t* contacts,int32_t* rail,bool allowRail=true){
 try{
  if(!path||!oldRect||!current||!contacts||width<=0||width>255||height<=0||height>255)return -1;CollisionAccess access(path);const auto& world=*access.p;int32_t rect[4],area[4],query[4];rect_from_center(current,width,height,rect);
  int32_t amount=wrap_sub(oldRect[1],rect[1]);
  if(amount>0){area[0]=rect[0];area[1]=rect[1];area[2]=rect[2];area[3]=amount;query_from_q8(area,query);resolve_contact_list(world,5,query,current,width,height,contacts);rect_from_center(current,width,height,rect);}
  amount=wrap_sub(wrap_add(rect[1],rect[3]),wrap_add(oldRect[1],oldRect[3]));
  if(amount>0){area[0]=rect[0];area[1]=wrap_add(oldRect[1],oldRect[3]);area[2]=rect[2];area[3]=amount;query_from_q8(area,query);if(rail&&allowRail)resolve_contact_list(world,6,query,current,width,height,contacts,rail);if(!rail||!contacts[0])resolve_contact_list(world,4,query,current,width,height,contacts);if(!contacts[0])resolve_contact_list(world,3,query,current,width,height,contacts);rect_from_center(current,width,height,rect);}
  amount=wrap_sub(oldRect[0],rect[0]);
  if(amount>0){area[0]=rect[0];area[1]=rect[1];area[2]=amount;area[3]=rect[3];query_from_q8(area,query);resolve_contact_list(world,1,query,current,width,height,contacts);rect_from_center(current,width,height,rect);}
  amount=wrap_sub(wrap_add(rect[0],rect[2]),wrap_add(oldRect[0],oldRect[2]));
  if(amount>0){area[0]=wrap_add(oldRect[0],oldRect[2]);area[1]=rect[1];area[2]=amount;area[3]=rect[3];query_from_q8(area,query);resolve_contact_list(world,2,query,current,width,height,contacts);}
  return 0;
 }catch(...){return -2;}
}

extern "C" int s2_resolve_static_file(const char* path,const int32_t* oldRect,int32_t* current,int width,int height,int32_t* contacts){return resolve_static(path,oldRect,current,width,height,contacts,nullptr);}
extern "C" int s2_resolve_puss_static_file(const char* path,const int32_t* oldRect,int32_t* current,int width,int height,int32_t* contacts,int32_t* rail,int allowRail){if(!rail)return -1;std::fill_n(rail,3,0);return resolve_static(path,oldRect,current,width,height,contacts,rail,allowRail!=0);}
