// Native resource presentation for every source map and sprite animation.
// Optional static-world traversal uses native protagonist locomotion.
// No world AI, hazards, boss scripts or completion for unported maps.
#include "campaign_view.h"
#include "campaign_player.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <iterator>
#include <memory>
#include <string>
#include <vector>
#include <cstdio>
#include <cstring>
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" void s2_actor_anchor_q8(const int32_t*,const int32_t*,int,int,int32_t*);
extern "C" void* s2_scene_create(const char*);
extern "C" void s2_scene_destroy(void*);
extern "C" int s2_scene_dimensions(void*,int32_t*);
extern "C" int s2_scene_render(void*,int,int,int,int,uint32_t*,size_t);
extern "C" void* s2_sprite_bank_create(const char*);
extern "C" void s2_sprite_bank_destroy(void*);
extern "C" int s2_sprite_bank_info(void*,int,int32_t*);
extern "C" int s2_sprite_composite_transform(void*,int,int,int,int,int,int,int,uint32_t*,size_t);
namespace {
struct SceneDelete{void operator()(void* p)const{s2_scene_destroy(p);}};
struct BankDelete{void operator()(void* p)const{s2_sprite_bank_destroy(p);}};
struct Bank{std::string name;int count=0;std::unique_ptr<void,BankDelete> handle;};
struct Object{int id,type,x,y,mirror,bank,animation;};
struct World{int scene,width,height,song,x,y;std::vector<Object> objects;int bound=0,walkable=-1;};
struct Reader{std::vector<uint8_t> bytes;size_t at=0;bool ok=true;
 int32_t word(){if(at+4>bytes.size()){ok=false;return 0;}uint32_t v=uint32_t(bytes[at])|(uint32_t(bytes[at+1])<<8)|(uint32_t(bytes[at+2])<<16)|(uint32_t(bytes[at+3])<<24);at+=4;return int32_t(v);}
 std::string text(int n){if(n<1||n>80||size_t(n)>bytes.size()-at){ok=false;return{};}std::string s(reinterpret_cast<const char*>(bytes.data()+at),size_t(n));at+=size_t(n);return s;}
};
struct MotionBlock{uint32_t address;std::vector<int32_t> words;};
struct Campaign{std::vector<MotionBlock> motion;int playerType=3,held=0,respawns=0;int32_t pose[80]={},extra[8]={},book[8]={};std::string root;std::vector<Bank> banks;std::vector<World> worlds;std::unique_ptr<void,SceneDelete> scene;int selected=0,mode=0,bank=0,animation=0,x=0,y=0,tick=0,mirror=0,zoom=2,viewport=240;bool paused=false,placements=true;
 static int fetch(uint32_t address,int32_t* out,int count,void* context){auto& c=*static_cast<Campaign*>(context);if(count<1||count>400||address%4)return 0;for(auto& block:c.motion)if(address>=block.address&&uint64_t(address)+count*4<=uint64_t(block.address)+block.words.size()*4){std::copy_n(block.words.data()+(address-block.address)/4,count,out);return 1;}return 0;}
 int canWalk(World& w){if(w.walkable>=0)return w.walkable;char path[64];std::snprintf(path,sizeof(path),"/scenes/scene_%02d.s2cl",w.scene);int result=s2_static_probe_q8((root+path).c_str(),3,0,0,w.width*256,w.height*256);if(result>=0)w.walkable=result;return result;}
 int walkStart(int type=0,bool keep=false){auto& w=worlds[size_t(selected)];int supported=canWalk(w);if(supported<=0)return supported<0?supported:-4;const Object* source=nullptr;for(auto& o:w.objects)if(o.type>=3&&o.type<=7){source=&o;break;}if(!type)type=source?source->type:3;if(!s2_campaign_player_table(type)||motion.empty())return -2;int32_t anchor[2]={w.x*256,w.y*256};if(source){anchor[0]=source->x*256;anchor[1]=source->y*256;}int flip=source?source->mirror&1:0;int bottom=pose[1]+pose[31]*128;if(keep){s2_actor_anchor_q8(pose+72,pose,pose[18],0,anchor);flip=pose[18];}int e=s2_campaign_player_init(type,anchor,flip,pose,extra,book,fetch,this);if(e)return e;if(keep)pose[1]=bottom-pose[31]*128;pose[32]=pose[0]-pose[30]*128;pose[33]=pose[1]-pose[31]*128;pose[34]=pose[30]*256;pose[35]=pose[31]*256;pose[36]=pose[0];pose[37]=pose[1];playerType=type;held=0;return 0;}
 int playerBank()const{return playerType==3?0:playerType==6?1:playerType==4?2:playerType==5?3:4;}
 int playerAnimation()const{uint32_t base=playerType==3?0x0834f25c:playerType==6?0x0832fee4:playerType==4?0x08344bd4:playerType==5?0x0833731c:0x08355b74;return int((uint32_t(pose[47])-base)/24);}
 void follow(){x=(pose[0]>>8)-viewport/2;y=(pose[1]>>8)-95;clamp();}
 void clamp(){auto& w=worlds[size_t(selected)];x=std::clamp(x,0,std::max(0,w.width-viewport));y=std::clamp(y,0,std::max(0,w.height-160));}
 int load(int index){char file[64];auto& w=worlds[size_t(index)];std::snprintf(file,sizeof(file),"/scenes/scene_%02d.s2lv",w.scene);std::unique_ptr<void,SceneDelete> next(s2_scene_create((root+file).c_str()));if(!next)return -2;int32_t dimensions[2];if(s2_scene_dimensions(next.get(),dimensions)||dimensions[0]!=w.width||dimensions[1]!=w.height)return -2;scene=std::move(next);selected=index;tick=0;x=w.x-viewport/2;y=w.y-95;clamp();held=0;respawns=0;if(mode==2){int e=walkStart();if(e==-4)mode=0;else if(e)return e;else follow();}return 0;}
 void* sprite(int index){auto& b=banks[size_t(index)];if(!b.handle)b.handle.reset(s2_sprite_bank_create((root+"/sprites/"+b.name+"/bank.s2sp").c_str()));return b.handle.get();}
 int frame(int b,int a,int32_t* info){void* h=sprite(b);if(!h||s2_sprite_bank_info(h,a,info))return -2;int f=tick/(info[2]+1);return(info[3]&1)?f%info[1]:std::min(f,info[1]-1);}
};
int wrapped(int index,int delta,int count){int64_t v=(int64_t(index)+delta)%count;return int(v<0?v+count:v);}
}
extern "C" void* s2_campaign_create(const char* root){
 if(!root)return nullptr;try{auto c=std::make_unique<Campaign>();c->root=root;std::ifstream in(c->root+"/catalog.s2cp",std::ios::binary);if(!in)return nullptr;Reader r;r.bytes.assign(std::istreambuf_iterator<char>(in),{});if(r.bytes.size()>1024*1024||r.word()!=0x50433253||r.word()!=1)return nullptr;int nb=r.word(),nw=r.word();if(nb<1||nb>32||nw!=30)return nullptr;
  for(int i=0;i<nb;i++){int n=r.word();Bank b;b.count=r.word();b.name=r.text(n);if(b.count<1||b.count>600||b.name.empty()||b.name.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789_")!=std::string::npos)return nullptr;c->banks.push_back(std::move(b));}
  std::array<bool,30> seen{};for(int i=0;i<nw;i++){World w;w.scene=r.word();w.width=r.word();w.height=r.word();w.song=r.word();w.x=r.word();w.y=r.word();int n=r.word();if(w.scene<0||w.scene>=30||seen[size_t(w.scene)]||w.width<1||w.width>16384||w.height<1||w.height>16384||n<0||n>1024||w.x<0||w.x>w.width||w.y<0||w.y>w.height)return nullptr;seen[size_t(w.scene)]=true;
   for(int j=0;j<n;j++){Object o;int* fields[7]={&o.id,&o.type,&o.x,&o.y,&o.mirror,&o.bank,&o.animation};for(auto p:fields)*p=r.word();if(o.id<1||o.type<0||o.type>=158||o.x<0||o.y<0||o.x>16384||o.y>16384||o.mirror<0||o.mirror>3||o.bank< -1||o.bank>=nb||(o.bank<0?o.animation!=-1:o.animation<0||o.animation>=c->banks[size_t(o.bank)].count))return nullptr;if(o.bank>=0)w.bound++;w.objects.push_back(o);}c->worlds.push_back(std::move(w));}
  if(!r.ok||r.at!=r.bytes.size()||c->load(0))return nullptr;
  std::ifstream pm(c->root+"/player.s2pm",std::ios::binary);if(!pm)return nullptr;Reader m;m.bytes.assign(std::istreambuf_iterator<char>(pm),{});if(m.bytes.size()>65536||m.word()!=0x4d503253||m.word()!=1)return nullptr;int blocks=m.word();if(blocks<5||blocks>512)return nullptr;uint32_t previousEnd=0;
  for(int i=0;i<blocks;i++){MotionBlock block;block.address=uint32_t(m.word());int size=m.word();if(block.address<0x08000000||block.address>=0x08800000||block.address%4||block.address<previousEnd||size<4||size>1640||size%4||size_t(size)>m.bytes.size()-m.at)return nullptr;for(int j=0;j<size/4;j++)block.words.push_back(m.word());previousEnd=block.address+size;c->motion.push_back(std::move(block));}if(!m.ok||m.at!=m.bytes.size())return nullptr;return c.release();
 }catch(...){return nullptr;}
}
extern "C" void s2_campaign_destroy(void* p){delete static_cast<Campaign*>(p);}
extern "C" int s2_campaign_select_scene(void* p,int id){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);for(size_t i=0;i<c.worlds.size();i++)if(c.worlds[i].scene==id)return c.load(int(i));return -1;}
extern "C" int s2_campaign_navigate(void* p,int delta){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);return c.load(wrapped(c.selected,delta,int(c.worlds.size())));}
extern "C" int s2_campaign_mode(void* p,int mode){if(!p||mode<0||mode>2)return -1;auto& c=*static_cast<Campaign*>(p);if(mode==2&&c.mode!=2){int e=c.walkStart();if(e)return e;c.paused=false;c.follow();}c.held=0;c.mode=mode;return 0;}
extern "C" int s2_campaign_bank(void* p,int delta){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);int b=wrapped(c.bank,delta,int(c.banks.size()));if(!c.sprite(b))return -2;c.bank=b;c.animation=0;c.tick=0;return 0;}
extern "C" int s2_campaign_animation(void* p,int delta){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);c.animation=wrapped(c.animation,delta,c.banks[size_t(c.bank)].count);c.tick=0;return 0;}
extern "C" int s2_campaign_pan(void* p,int dx,int dy){if(!p||dx< -16384||dx>16384||dy< -16384||dy>16384)return -1;auto& c=*static_cast<Campaign*>(p);if(c.mode==2)return 0;c.x+=dx;c.y+=dy;c.clamp();return 0;}
extern "C" int s2_campaign_option(void* p,int option,int value){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);if(option<0||option>3||(option<3?(value<0||value>1):(value<1||value>4)))return -1;if(option==0)c.paused=value;else if(option==1)c.mirror=value;else if(option==2)c.placements=value;else c.zoom=value;return 0;}
extern "C" int s2_campaign_step(void* p,int ticks){if(!p||ticks<0||ticks>4)return -1;auto& c=*static_cast<Campaign*>(p);if(c.paused)return 0;for(int i=0;i<ticks;i++){c.tick=std::min(10000000,c.tick+1);if(c.mode==2){char path[64];std::snprintf(path,sizeof(path),"/scenes/scene_%02d.s2cl",c.worlds[size_t(c.selected)].scene);int e=s2_campaign_player_step((c.root+path).c_str(),c.playerType,c.pose,c.extra,c.book,c.held,c.tick,Campaign::fetch,&c);if(e)return e;auto& w=c.worlds[size_t(c.selected)];if(c.pose[0]<-128*256||c.pose[0]>(w.width+128)*256||c.pose[1]>(w.height+128)*256){e=c.walkStart(c.playerType);if(e)return e;c.respawns++;}c.follow();}}return 0;}
extern "C" int s2_campaign_info(void* p,int32_t* out){if(!p||!out)return -1;auto& c=*static_cast<Campaign*>(p);auto& w=c.worlds[size_t(c.selected)];int32_t a[8];int f=c.frame(c.bank,c.animation,a);if(f<0)return f;int32_t row[16]={c.mode,w.scene,c.selected,w.width,w.height,int(w.objects.size()),w.bound,c.bank,c.animation,a[0],a[1],f,c.tick,w.song,c.x,c.y};std::copy_n(row,16,out);return 0;}
extern "C" int s2_campaign_save(void* p,int32_t* out){if(!p||!out)return -1;auto& c=*static_cast<Campaign*>(p);int32_t row[12]={c.worlds[size_t(c.selected)].scene,c.mode,c.bank,c.animation,c.x,c.y,c.tick,c.mirror,int(c.paused),int(c.placements),c.zoom,c.viewport};std::copy_n(row,12,out);return 0;}
extern "C" int s2_campaign_restore(void* p,const int32_t* s){if(!p||!s)return -1;auto& c=*static_cast<Campaign*>(p);if(s[0]<0||s[0]>=30||s[1]<0||s[1]>2||s[2]<0||size_t(s[2])>=c.banks.size()||s[3]<0||s[3]>=c.banks[size_t(s[2])].count||s[4]<0||s[4]>16384||s[5]<0||s[5]>16384||s[6]<0||s[6]>10000000||s[7]<0||s[7]>1||s[8]<0||s[8]>1||s[9]<0||s[9]>1||s[10]<1||s[10]>4||s[11]<240||s[11]>640)return -1;if(s[1]==2){for(auto& w:c.worlds)if(w.scene==s[0]&&c.canWalk(w)<=0)return -1;}int e=s2_campaign_select_scene(p,s[0]);if(e)return e;c.mode=s[1];if(c.mode==2){e=c.walkStart();if(e)return e;}c.bank=s[2];c.animation=s[3];c.x=s[4];c.y=s[5];c.tick=s[6];c.mirror=s[7];c.paused=s[8];c.placements=s[9];c.zoom=s[10];c.viewport=s[11];c.clamp();return 0;}
extern "C" int s2_campaign_render(void* p,int width,uint32_t* out,size_t count){if(!p||!out||width<240||width>640||count!=size_t(width)*160)return -1;auto& c=*static_cast<Campaign*>(p);c.viewport=width;c.clamp();int viewWidth=std::min(width,c.worlds[size_t(c.selected)].width),offset=(width-viewWidth)/2;std::vector<uint32_t> background(size_t(viewWidth)*160);int e=s2_scene_render(c.scene.get(),c.x,c.y,viewWidth,160,background.data(),background.size());if(e)return e;std::fill_n(out,count,0xff181818u);for(int y=0;y<160;y++)std::copy_n(background.data()+y*viewWidth,viewWidth,out+y*width+offset);
 if((c.mode==0||c.mode==2)&&c.placements){for(const auto& o:c.worlds[size_t(c.selected)].objects){if(o.bank<0||(c.mode==2&&o.type>=3&&o.type<=7))continue;int32_t a[8];int f=c.frame(o.bank,o.animation,a);if(f<0)return f;int x=o.x-c.x,y=o.y-c.y;if(x< -256||x>viewWidth+256||y< -256||y>416)continue;e=s2_sprite_composite_transform(c.sprite(o.bank),o.animation,f,o.mirror,viewWidth,160,x,y,background.data(),background.size());if(e)return e;}for(int y=0;y<160;y++)std::copy_n(background.data()+y*viewWidth,viewWidth,out+y*width+offset);}
 if(c.mode==2){int32_t anchor[2];s2_actor_anchor_q8(c.pose+72,c.pose,c.pose[18],0,anchor);e=s2_sprite_composite_transform(c.sprite(c.playerBank()),c.playerAnimation(),c.pose[22],c.pose[18],width,160,(anchor[0]>>8)-c.x+offset,(anchor[1]>>8)-c.y,out,count);if(e)return e;}
 if(c.mode==1){for(size_t i=0;i<count;i++)out[i]=0xff000000u|((out[i]>>2)&0x003f3f3fu);int32_t a[8];int f=c.frame(c.bank,c.animation,a);if(f<0)return f;std::vector<uint32_t> sprite(256*256);int center=a[4]+a[6]/2,ax=128+(c.mirror?center:-center),ay=128-(a[5]+a[7]/2);e=s2_sprite_composite_transform(c.sprite(c.bank),c.animation,f,c.mirror,256,256,ax,ay,sprite.data(),sprite.size());if(e)return e;
  for(int y=0;y<160;y++)for(int x=0;x<width;x++){int sx=(x-width/2+c.zoom*128)/c.zoom,sy=(y-80+c.zoom*128)/c.zoom;if(sx<0||sx>=256||sy<0||sy>=256)continue;uint32_t pixel=sprite[size_t(sy)*256+size_t(sx)];if(pixel>>24)out[size_t(y)*width+size_t(x)]=pixel;}
 }return 0;
}

extern "C" int s2_campaign_input(void* p,int held){if(!p||held<0||held>255)return -1;static_cast<Campaign*>(p)->held=held;return 0;}
extern "C" int s2_campaign_character(void* p,int type){if(!p||!s2_campaign_player_table(type))return -1;auto& c=*static_cast<Campaign*>(p);int e=c.walkStart(type,c.mode==2);if(!e)c.follow();return e;}
extern "C" int s2_campaign_walk_info(void* p,int32_t* out){if(!p||!out)return -1;auto& c=*static_cast<Campaign*>(p);int32_t row[10]={c.playerType,c.pose[0],c.pose[1],c.extra[0],c.pose[22],c.pose[47],c.pose[14],c.held,c.respawns,c.playerAnimation()};std::copy_n(row,10,out);return 0;}
extern "C" int s2_campaign_walk_save(void* p,int32_t* out){if(!p||!out)return -1;auto& c=*static_cast<Campaign*>(p);out[0]=0x31574b53;out[1]=c.playerType;out[2]=c.worlds[size_t(c.selected)].scene;out[3]=c.respawns;std::copy_n(c.pose,80,out+4);std::copy_n(c.extra,8,out+84);std::copy_n(c.book,8,out+92);return 0;}
extern "C" int s2_campaign_walk_restore(void* p,const int32_t* in){if(!p||!in)return -1;auto& c=*static_cast<Campaign*>(p);if(c.mode!=2||in[0]!=0x31574b53||!s2_campaign_player_table(in[1])||in[2]!=c.worlds[size_t(c.selected)].scene||in[3]<0||in[3]>1000000)return -1;
 int t=in[1];for(int i=6;i<18;i++)if(int64_t(in[i]) < -65536||int64_t(in[i])>65536)return -1;int32_t header[6];const int32_t* s=in+4;int32_t row[10];uint32_t table=s2_campaign_player_table(t);bool found=false;for(int i=0;i<40;i++){if(!Campaign::fetch(table+i*40,row,10,&c))return -1;if(row[0]==999)break;if(row[1]==s[47]){found=true;break;}}if(!found||!Campaign::fetch(uint32_t(s[47]),header,6,&c)||s[18]<0||s[18]>1||s[21]<0||s[21]>2||s[22]<0||s[22]>=int((uint32_t(header[5])>>8)&255)||s[40]!=10||s[30]<1||s[30]>255||s[31]<1||s[31]>255||s[0]<-128*256||s[0]>(c.worlds[size_t(c.selected)].width+128)*256||s[1]<-16384*256||s[1]>(c.worlds[size_t(c.selected)].height+128)*256||!((in[84]>=0&&in[84]<=5)||(t==6&&in[84]==16)||(t==4&&(in[84]==20||in[84]==21))))return -1;
 if(s[72]!=int16_t(uint32_t(header[3]))||s[73]!=int16_t(uint32_t(header[3])>>16)||s[74]!=int(uint32_t(header[4])&255)||s[75]!=int((uint32_t(header[4])>>8)&255)||s[76]!=int(uint32_t(header[5])&255)||s[77]!=int((uint32_t(header[5])>>8)&255)||s[78]!=int((uint32_t(header[5])>>16)&255))return -1;
 std::copy_n(in+4,80,c.pose);std::copy_n(in+84,8,c.extra);std::copy_n(in+92,8,c.book);c.book[4]=0;c.playerType=t;c.respawns=in[3];c.held=0;c.follow();return 0;}

extern "C" int s2_campaign_can_walk(void* p){if(!p)return -1;auto& c=*static_cast<Campaign*>(p);return c.canWalk(c.worlds[size_t(c.selected)]);}
