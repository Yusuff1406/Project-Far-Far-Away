// Original decoded FLC art/OBJ thumbnails/fonts with a native touch menu owner.
#include "frontend.h"
#include "level_rules.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <iterator>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <cstring>
extern "C" int s2_menu_line_begin(int32_t*,int,int,int,int);
extern "C" int s2_menu_line_step(int32_t*);
extern "C" int s2_fade_argb(int,uint32_t*,size_t);
extern "C" int s2_mosaic_argb(int,uint32_t*,int,int);
extern "C" void* s2_sprite_bank_create(const char*);
extern "C" void s2_sprite_bank_destroy(void*);
extern "C" int s2_sprite_composite_bank(void*,int,int,int,int,int,int,int,uint32_t*,size_t);
namespace {
struct Picture{int w=0,h=0,frames=0,period=1;std::vector<uint8_t> pixels;};
struct Font{int w=0,h=0,glyphs=0;std::array<uint8_t,256> index{},advance{};uint32_t colors[3][16]={};std::vector<uint8_t> tiles;};
static const int epilogueStart[6]={19,23,26,30,33,35},epilogueCount[6]={4,3,4,3,2,4};
static const int bookX[6]={40,62,83,105,125,178},bookY[6]={68,84,93,102,108,115};
struct Menu{std::map<int,Picture> images;Font fonts[2];std::map<std::string,std::string> labels;int scenes[30]={};std::vector<std::string> credits;void* sprites=nullptr;void* fairy=nullptr;
 int page=11,cursor=0,book=0,slot=0,tick=0,held=0,action=0,confirm=0,returnPage=0;int used=0,complete[3]={},coins[3]={},chapterCoins[3][25]={},bonusBests[5]={};bool separateCoins=false;
 int startupHold=0;int transition=0,transitionTick=0,pendingPage=0,pendingCursor=0,pendingAction=0;bool fadeIn=false,waiting=false;int32_t line[10]={};int storyOffset=0,storyRevealed=0,selectionTick=16,previousCursor=0;
 int titleTick=0,sound=0,storySoundPending=0,creditScroll=0;std::string names[3]={"AAA","AAA","AAA"},draft;
 bool testBooks=false;
 void storySound(){storySoundPending=0;if(page!=14)return;static const int sounds[6][4]={{0,0,102,0},{3,0,0,0},{90,0,83,0},{0,84,0,0},{0,100,0,0},{26,58,0,83}};int effect=sounds[book][cursor];sound=0;if((book==2&&cursor==0)||(book==3&&cursor==1))storySoundPending=effect;else sound=effect;}
 int bookCount()const{if(testBooks)return 6;int count=1;for(int i=1;i<5;i++){int mask=(1<<(i*5))-1;if((complete[slot]&mask)==mask)count=i+1;else break;}if((complete[slot]&0x1ffffff)==0x1ffffff)count=6;return count;}
 bool chapterAvailable(int row)const{if(testBooks)return true;if(book==5)return true;int chapter=book*5+row;if(chapter<=0)return true;int mask=(1<<chapter)-1;return (complete[slot]&mask)==mask;}
 int selectedPalette(int row)const{return row==cursor?((tick/16)%2?0:2):1;}
 int chapterPalette(int row)const{return !chapterAvailable(row)?2:row==cursor?((tick/16)%2?1:0):1;}
 int clip[4]={0,0,240,160};std::vector<std::array<int32_t,8>> textBoxes;
 ~Menu(){if(sprites)s2_sprite_bank_destroy(sprites);if(fairy)s2_sprite_bank_destroy(fairy);}
 void enter(int p,int c=0){if(p==0)p=1;if(p==7)p=4;if(p==1&&page!=0&&page!=1)titleTick=0;page=p;cursor=c;tick=0;creditScroll=0;storyOffset=storyRevealed=0;selectionTick=16;previousCursor=c;storySound();if(page==3)s2_menu_line_begin(line,bookX[c],bookY[c],bookX[c],bookY[c]);else s2_menu_line_begin(line,94,12+c*22,94,12+c*22);}
 void change(int p,int c=0){if((page==5||page==6||page==10)&&(p==5||p==6||p==10)){enter(p,c);transition=0;return;}transition=(page==3&&p==4)||(page==4&&p==3)?2:1;transitionTick=0;fadeIn=false;pendingPage=p;pendingCursor=c;pendingAction=0;}
 void exit(int a){if(a==2){action=a;waiting=true;transition=0;return;}transition=1;transitionTick=0;fadeIn=false;pendingAction=a;}
 int selectableChapters()const{int n=0;while(n<5&&chapterAvailable(n))++n;return std::max(1,n);}
 int rows()const{switch(page){case 1:return 2;case 2:return 4;case 3:return bookCount();case 4:return selectableChapters();case 5:return 3;case 13:return 32;case 6:return 2;case 9:return 3;case 11:case 12:return 4;case 14:return epilogueCount[std::min(book,5)];default:return 1;}}
 void back(){if(page!=11&&page!=12&&page!=14)sound=8;switch(page){case 0:break;case 1:break;case 2:change(1);break;case 3:change(2,slot);break;case 4:change(3,book);break;case 5:exit(2);break;case 6:change(returnPage,confirm==3?1:0);break;case 7:change(4,cursor);break;case 8:change(1,1);break;case 9:change(2,3);break;case 10:change(5);break;case 11:change(0);break;case 12:change(3);break;case 14:if(book==5){change(3,5);}else change(4,book==4?3:4);break;case 13:if(!draft.empty())draft.pop_back();else change(2,slot);break;default:break;}}
 void storyNext();
 void accept(){if(page!=11&&page!=12&&page!=14)sound=63;switch(page){case 0:change(1);break;case 1:change(cursor?8:2);break;case 2:if(cursor==3)change(9);else{slot=cursor;bool fresh=!(used&(1<<slot));if(fresh){draft.clear();change(13);}else change(3);}break;case 3:book=cursor;change(4);break;case 4:{if(!chapterAvailable(cursor)){sound=0;break;}int scene=scenes[book*5+cursor];exit(scene==0?1:11);break;}
 case 5:if(cursor==0)exit(2);else{confirm=cursor==1?3:8;returnPage=5;change(6);}break;
 case 6:if(confirm==3){if(cursor==0)back();else exit(3);break;}if(confirm==6){if(cursor==0)back();else{used&=~(1<<slot);complete[slot]=coins[slot]=0;std::fill_n(chapterCoins[slot],25,0);names[slot]="AAA";action=6;change(2,slot);}break;}if(cursor==1)back();else if(confirm==8)change(10);else if(confirm==6){used&=~(1<<slot);complete[slot]=coins[slot]=0;std::fill_n(chapterCoins[slot],25,0);action=6;change(2,slot);}else exit(confirm);break;
 case 7:if(!chapterAvailable(cursor)){sound=0;break;}exit(scenes[book*5+cursor]==0?1:11);break;case 8:back();break;case 9:slot=cursor;confirm=6;returnPage=9;change(6);break;case 10:change(5);break;case 11:change(cursor<3?11:0,cursor<3?cursor+1:0);break;case 12:case 14:storyNext();break;case 13:if(cursor==31){if(draft.size()==3){names[slot]=draft;used|=1<<slot;action=7;change(12);}}else if(draft.size()<3){draft+="ABCDEFGHIJKLMNOPQRSTUVWXYZ.!?$&"[cursor];if(draft.size()==3)cursor=31;}break;default:break;}}
};
struct Reader{std::vector<uint8_t> b;size_t p=0;bool ok=true;uint32_t word(){if(p+4>b.size()){ok=false;return 0;}uint32_t v=uint32_t(b[p])|(uint32_t(b[p+1])<<8)|(uint32_t(b[p+2])<<16)|(uint32_t(b[p+3])<<24);p+=4;return v;}
 bool read(void* out,size_t n){if(!ok||n>b.size()-p){ok=false;return false;}std::memcpy(out,b.data()+p,n);p+=n;return true;}
 std::string text(size_t n){if(n>100000||n>b.size()-p){ok=false;return {};}std::string s(reinterpret_cast<const char*>(b.data()+p),n);p+=n;return s;}};
void image(Menu& m,int id,int frame,uint32_t* out){auto i=m.images.find(id);if(i==m.images.end())return;auto& p=i->second;frame=std::clamp(frame,0,p.frames-1);const uint8_t* data=p.pixels.data()+size_t(frame)*39424;uint32_t colors[256];for(int i=0;i<256;i++){auto b=data+i*4;colors[i]=uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24);}for(int i=0;i<38400;i++)out[i]=colors[data[1024+i]];}
int textWidth(const Font& f,const std::string& s){int n=0;for(unsigned char c:s)n+=f.advance[c];return n;}
void clip(Menu& m,int l=0,int t=0,int r=240,int b=160){m.clip[0]=l;m.clip[1]=t;m.clip[2]=r;m.clip[3]=b;}
void text(Menu& m,const std::string& s,int x,int y,int palette,uint32_t* out,bool center=false,int font=0,bool fit=true){const auto& f=m.fonts[font];if(center)x-=textWidth(f,s)/2;int stride=f.w*f.h/2;int left=100000,right=-100000,top=100000,bottom=-100000,pen=0;
 for(unsigned char ch:s){int glyph=f.index[ch];if(ch!=' '&&glyph<f.glyphs)for(int py=0;py<f.h;py++)for(int px=0;px<f.w;px++){int at=glyph*stride+((py/8)*(f.w/8)+px/8)*32+(py%8)*4+px%8/2;if((f.tiles[size_t(at)]>>((px&1)*4))&15){left=std::min(left,pen+px);right=std::max(right,pen+px+1);top=std::min(top,py);bottom=std::max(bottom,py+1);}}pen+=f.advance[ch];}
 if(right<=left)return;if(!fit&&(y+bottom<=m.clip[1]||y+top>=m.clip[3]))return;if(x+right>m.clip[2])x=m.clip[2]-right;if(x+left<m.clip[0])x=m.clip[0]-left;if(fit&&y+bottom>m.clip[3])y=m.clip[3]-bottom;if(fit&&y+top<m.clip[1])y=m.clip[1]-top;m.textBoxes.push_back({x+left,y+top,x+right,y+bottom,m.clip[0],m.clip[1],m.clip[2],m.clip[3]});
 for(unsigned char ch:s){int glyph=f.index[ch];if(ch!=' '&&glyph<f.glyphs)for(int py=0;py<f.h;py++)for(int px=0;px<f.w;px++){int at=glyph*stride+((py/8)*(f.w/8)+px/8)*32+(py%8)*4+px%8/2;int c=(f.tiles[size_t(at)]>>((px&1)*4))&15;int xx=x+px,yy=y+py;if(c&&xx>=m.clip[0]&&xx<m.clip[2]&&yy>=m.clip[1]&&yy<m.clip[3])out[yy*240+xx]=f.colors[palette][c];}x+=f.advance[ch];}}
// Original 17218/17198/11CB0 paged captions: 240x48 at (0,112),
// strict right/bottom bounds and three complete 12px rows. No typewriter.
std::vector<std::string> storyLines(Menu& m){
 const auto& caption=m.labels.at(m.page==14?"epilogue_"+std::to_string(m.book)+"_"+std::to_string(m.cursor):"intro_"+std::to_string(m.cursor));std::vector<std::string> lines;
 for(size_t begin=0;begin<caption.size();){size_t end=begin,lastSpace=std::string::npos;int width=0;
  while(end<caption.size()&&caption[end]!='\n'&&caption[end]!='\f'){
   if(caption[end]==' ')lastSpace=end;width+=m.fonts[0].advance[uint8_t(caption[end])];
   if(width>=240){if(lastSpace!=std::string::npos)end=lastSpace;break;}++end;
  }
  lines.push_back(caption.substr(begin,end-begin));begin=end<caption.size()?end+1:end;
 }
 return lines;
}
void Menu::storyNext(){auto lines=storyLines(*this);if(storyOffset+3<int(lines.size())){storyOffset+=3;storyRevealed=0;}else if(cursor<(page==14?epilogueCount[book]-1:3))change(page,cursor+1);else if(page==14){if(book==5){change(3,5);}else change(4,book==4?3:4);}else change(3);}
void label(Menu& m,const char* key,int x,int y,int color,uint32_t* out,bool center=false){auto i=m.labels.find(key);if(i!=m.labels.end())text(m,i->second,x,y,color,out,center);}
void sprite(Menu& m,int anim,int x,int y,uint32_t* out){if(m.sprites)s2_sprite_composite_bank(m.sprites,anim,0,0,240,160,x,y,out,38400);}
void candle(Menu& m,uint32_t* out){if(!m.sprites)return;uint32_t flame[38400]={};s2_sprite_composite_bank(m.sprites,3,(m.tick/6)%13,0,240,160,0,0,flame,38400);
 for(int i=0;i<38400;i++)if(flame[i]>>24){int v=int(flame[i]&255);uint32_t c=out[i];int r=(c>>16)&255,g=(c>>8)&255,b=c&255;out[i]=0xff000000u|((r+(255-r)*v/255)<<16)|((g+(255-g)*v/255)<<8)|(b+(255-b)*v/255);}}

void footer(Menu& m,uint32_t* out){if(m.page==4){clip(m,136,116,216,144);label(m,"back",140,120,0,out);}else{clip(m,72,128,168,152);label(m,"back",120,132,0,out,true);}clip(m);}
void selection(Menu& m,const std::vector<std::string>& list,int x,int y,int step,uint32_t* out,bool center=true){for(size_t i=0;i<list.size();i++)text(m,list[i],x,y+int(i)*step,m.selectedPalette(int(i)),out,center);}
std::string get(Menu& m,const char* key){return m.labels.at(key);}
}
extern "C" void* s2_frontend_create(const char* path,const char* spritePath){
 if(!path||!spritePath)return nullptr;std::ifstream in(path,std::ios::binary);if(!in)return nullptr;Reader r;r.b.assign(std::istreambuf_iterator<char>(in),{});if(r.b.size()>64000000||r.word()!=0x49553253||r.word()!=2)return nullptr;
 uint32_t ni=r.word(),nf=r.word(),ns=r.word(),nl=r.word(),nc=r.word();if(ni!=39||nf!=2||ns>64||nl!=30||nc>20000)return nullptr;auto m=std::make_unique<Menu>();
 for(uint32_t i=0;i<ni;i++){int id=int(r.word());Picture p;p.w=int(r.word());p.h=int(r.word());p.frames=int(r.word());p.period=int(r.word());if(p.w!=240||p.h!=160||p.frames<1||p.frames>100||p.period<1||m->images.count(id))return nullptr;p.pixels.resize(size_t(p.frames)*39424);r.read(p.pixels.data(),p.pixels.size());m->images.emplace(id,std::move(p));}
 for(auto& f:m->fonts){f.w=int(r.word());f.h=int(r.word());f.glyphs=int(r.word());uint32_t n=r.word();if((f.w!=16&&f.w!=8)||f.h!=f.w||f.glyphs<1||f.glyphs>256||n!=uint32_t(f.w*f.h*f.glyphs/2))return nullptr;r.read(f.index.data(),256);r.read(f.advance.data(),256);for(auto& p:f.colors)for(auto& c:p)c=r.word();f.tiles.resize(n);r.read(f.tiles.data(),n);}
 for(uint32_t i=0;i<ns;i++){uint32_t k=r.word(),n=r.word();auto key=r.text(k),value=r.text(n);m->labels.emplace(key,value);}
 for(int i=0;i<30;i++){m->scenes[i]=int(r.word());if(m->scenes[i]<0||m->scenes[i]>=30||r.word()!=uint32_t(17+i)||r.word()!=uint32_t(i>=25))return nullptr;}
 auto credits=r.text(nc);std::string clean;for(size_t i=0;i<credits.size();i++){if(credits[i]==1){if(i+1>=credits.size()||credits[++i]!=1)return nullptr;}else clean+=credits[i];}credits=std::move(clean);size_t start=0;for(size_t i=0;i<=credits.size();i++)if(i==credits.size()||credits[i]=='\n'){m->credits.push_back(credits.substr(start,i-start));start=i+1;}
 if(!r.ok||r.p!=r.b.size()||m->labels.size()!=51)return nullptr;m->sprites=s2_sprite_bank_create(spritePath);if(!m->sprites)return nullptr;std::string fairyPath=spritePath;size_t slash=fairyPath.find_last_of('/');if(slash==std::string::npos)return nullptr;fairyPath=fairyPath.substr(0,slash);slash=fairyPath.find_last_of('/');if(slash==std::string::npos)return nullptr;fairyPath=fairyPath.substr(0,slash)+"/bank_334304/bank.s2sp";m->fairy=s2_sprite_bank_create(fairyPath.c_str());if(!m->fairy)return nullptr;m->enter(11);m->transition=1;m->fadeIn=true;return m.release();
}
extern "C" void s2_frontend_destroy(void* h){delete static_cast<Menu*>(h);}
extern "C" int s2_frontend_open(void* h,int page,int cursor){if(!h||page<0||page>14)return -1;auto& m=*static_cast<Menu*>(h);m.enter(page);m.enter(page,std::clamp(cursor,0,m.rows()-1));m.startupHold=0;if(m.page==1)m.titleTick=0;m.held=0;m.action=0;m.sound=0;m.waiting=false;m.transition=0;return 0;}
extern "C" int s2_frontend_restore(void* h,const int32_t* p){if(!h||!p||p[0]<0||p[0]>14||p[2]<0||p[2]>5||p[3]<0||p[3]>2||(p[0]==14&&p[2]>5))return -1;auto& m=*static_cast<Menu*>(h);m.book=p[2];m.slot=p[3];m.enter(p[0]==6||p[0]==10?5:p[0]);m.enter(m.page,std::clamp(int(p[1]),0,m.rows()-1));m.tick=std::clamp(int(p[4]),0,999999);if(m.page==1)m.titleTick=m.tick;if(m.page==8)m.creditScroll=m.tick;m.startupHold=0;m.held=m.action=0;m.waiting=false;m.transition=1;m.fadeIn=true;m.transitionTick=0;return 0;}
extern "C" int s2_frontend_progress(void* h,const int32_t* p){if(!h||!p)return -1;auto& m=*static_cast<Menu*>(h);m.used=p[0]&7;for(int i=0;i<3;i++){m.complete[i]=p[1+i]&0x1ffffff;m.coins[i]=std::clamp(p[4+i],0,40);}return 0;}
extern "C" int s2_frontend_chapter_coins(void* h,const int32_t* counts){if(!h||!counts)return -1;auto& m=*static_cast<Menu*>(h);for(int slot=0;slot<3;slot++)for(int chapter=0;chapter<25;chapter++)m.chapterCoins[slot][chapter]=std::clamp(counts[slot*25+chapter],0,40);m.separateCoins=true;return 0;}
extern "C" int s2_frontend_bonus_bests(void* h,const int32_t* scores){if(!h||!scores)return -1;auto& m=*static_cast<Menu*>(h);for(int i=0;i<5;i++)m.bonusBests[i]=std::max(0,scores[i]);return 0;}
static int selectedCoins(const Menu& m){int chapter=m.book*5+std::min(m.cursor,4);return chapter>=25?m.bonusBests[chapter-25]:!levelCoinTarget(m.scenes[chapter])?0:m.separateCoins?m.chapterCoins[m.slot][chapter]:chapter==0?m.coins[m.slot]:0;}
extern "C" int s2_frontend_step(void* h,int buttons){if(!h)return -1;auto& m=*static_cast<Menu*>(h);if(m.page==4&&!m.chapterAvailable(m.cursor))m.cursor=std::min(m.cursor,m.selectableChapters()-1);int pressed=buttons&~m.held;m.held=buttons;if(m.waiting)return 0;
 if(m.startupHold>0){--m.startupHold;return 0;}if(m.transition){if(++m.transitionTick>=16){if(!m.fadeIn){if(m.pendingAction){m.action=m.pendingAction;m.pendingAction=0;m.waiting=true;return 0;}int old=m.page;if(old==14&&m.pendingPage==4&&m.book==5)m.book=4;m.enter(m.pendingPage,m.pendingCursor);if(old==11&&m.page!=11)m.action=9;m.fadeIn=true;m.transitionTick=0;}else{m.transition=0;m.transitionTick=0;if(m.storySoundPending){m.sound=m.storySoundPending;m.storySoundPending=0;}}}return 0;}
 m.tick=(m.tick+1)%1000000;if(m.page==1)m.titleTick=std::min(100000,m.titleTick+1);m.selectionTick=std::min(16,m.selectionTick+1);s2_menu_line_step(m.line);if(m.page==3)s2_menu_line_step(m.line);if(m.page==8){m.creditScroll+=(buttons&1)?2:1;if((pressed&8)||m.creditScroll>=(160+int(m.credits.size())*12)*2)m.change(1,1);return 0;}
 if(m.page==13){if(pressed&2)m.back();else if(pressed&1)m.accept();else if(pressed&(16|32|64|128)){int x=m.cursor%8,y=m.cursor/8;if(pressed&16)x=(x+1)%8;if(pressed&32)x=(x+7)%8;if(pressed&64)y=(y+3)%4;if(pressed&128)y=(y+1)%4;int next=y*8+x;if(next!=m.cursor)m.sound=63;m.cursor=next;}return 0;}
 if(m.page==11){auto& p=m.images.at(9+m.cursor);int duration=int((int64_t(p.frames)*p.period*60+999)/1000)+(m.cursor==0?120:0);if(pressed&8)m.change(0);else if((pressed&1)||m.tick>=duration)m.change(m.cursor<3?11:0,m.cursor<3?m.cursor+1:0);return 0;}
 if((m.page==12||m.page==14)&&(pressed&8)){if(m.page==14){if(m.book==5)m.change(3,5);else {int c=m.book==4?3:4;m.change(4,c);}}else m.change(3);return 0;}
 if(m.page==5&&(pressed&8)){m.exit(2);return 0;}if(pressed&2)m.back();else if(pressed&(1|8))m.accept();else if(pressed&(16|32|64|128)){if(m.page!=12&&m.page!=14&&m.page!=0&&m.page!=8){int delta=(pressed&(16|128))?1:-1;int next=(m.cursor+delta+m.rows())%m.rows();if(next==m.cursor){m.sound=63;m.tick=0;m.selectionTick=0;return 0;}m.sound=63;m.previousCursor=m.cursor;m.cursor=next;m.tick=0;m.selectionTick=0;if(m.page==3)s2_menu_line_begin(m.line,m.line[0],m.line[1],bookX[m.cursor],bookY[m.cursor]);else s2_menu_line_begin(m.line,m.line[0],m.line[1],94,12+m.cursor*22);}}return 0;}
extern "C" int s2_frontend_touch(void* h,int x,int y){if(!h||x<0||x>=240||y<0||y>=160)return -1;auto& m=*static_cast<Menu*>(h);if(m.transition||m.waiting)return 0;m.held=0;
 if(m.page==13){if(y>=128){if(x<120)m.back();else m.accept();}else if(x>=62&&x<190&&y>=58&&y<122){m.cursor=((y-58)/16)*8+(x-62)/16;m.accept();}return 0;}
 if(m.page==12&&y>=149&&x<105){m.back();return 0;}if(m.page==11||m.page==12||m.page==14){m.accept();return 0;}if(m.page==0||m.page==7||m.page==10){m.accept();return 0;}if(m.page==8){m.back();return 0;}if(y>=128&&m.page!=1&&m.page!=5){m.back();return 0;}
 int row=-1;switch(m.page){case 1:if(y>=129&&y<160)row=(y-129)/16;break;case 2:case 9:if(y>=63&&y<63+16*m.rows())row=(y-63)/16;break;case 3:{const int pos[6]={39,62,83,105,126,178};int best=20;for(int i=0;i<6;i++)if(std::abs(x-pos[i])<best){best=std::abs(x-pos[i]);row=i;}if(y<20||y>130)row=-1;break;}case 4:if(x>=91&&y>=8&&y<118)row=(y-8)/22;break;case 5:if(y>=52&&y<112)row=(y-52)/20;break;case 6:if(m.confirm==3){if(y>=66&&y<102)row=(y-66)/16;}else if(m.confirm==6){if(y>=76&&y<112)row=(y-76)/16;}else if(y>=72&&y<112)row=(y-72)/20;break;default:break;}
 if(row>=0&&row<m.rows()&&(m.page!=4||m.chapterAvailable(row))){if(row>=m.rows())return 0;if(m.cursor!=row&&m.page==3)s2_menu_line_begin(m.line,m.line[0],m.line[1],bookX[row],bookY[row]);m.cursor=row;m.accept();}return 0;}
extern "C" int s2_frontend_action(void* h){if(!h)return -1;auto& m=*static_cast<Menu*>(h);int a=m.action;m.action=0;return a;}
extern "C" int s2_frontend_sound(void* h){if(!h)return -1;auto& m=*static_cast<Menu*>(h);int sound=m.sound;m.sound=0;return sound;}
extern "C" int s2_frontend_snapshot(void* h,int32_t* out){if(!h||!out)return -1;auto& m=*static_cast<Menu*>(h);int32_t s[9]={m.page,m.cursor,m.book,m.slot,m.tick,m.scenes[m.book*5+std::min(m.cursor,4)],m.used,m.complete[m.slot],selectedCoins(m)};std::copy_n(s,9,out);return 0;}
extern "C" int s2_frontend_presentation(void* h,int32_t* out){if(!h||!out)return -1;auto& m=*static_cast<Menu*>(h);int alpha=m.transition?std::min(64,m.fadeIn?64-m.transitionTick*4:m.transitionTick*4):0;int32_t row[8]={m.transition,m.transitionTick,alpha,m.pendingPage,m.line[0],m.line[1],m.storyOffset,m.storyRevealed};std::copy_n(row,8,out);return 0;}
extern "C" int s2_frontend_text_boxes(void* h,int32_t* out,int capacity){if(!h||capacity<0)return -1;auto& m=*static_cast<Menu*>(h);if(!out)return int(m.textBoxes.size());int n=std::min(capacity,int(m.textBoxes.size()));for(int i=0;i<n;i++)std::copy_n(m.textBoxes[size_t(i)].data(),8,out+i*8);return n;}
extern "C" int s2_frontend_render(void* h,uint32_t* out,size_t n){if(!h||!out||n!=38400)return -1;auto& m=*static_cast<Menu*>(h);m.textBoxes.clear();clip(m);std::fill_n(out,n,(m.page==5||m.page==6||m.page==10)?0u:0xff000000u);
 if(m.page==11){auto& p=m.images.at(9+m.cursor);int frame=std::min(p.frames-1,int(int64_t(std::max(0,m.tick-(m.cursor==0?120:0)))*1000/(60*p.period)));image(m,9+m.cursor,m.cursor==0?std::max(1,frame):frame,out);}
 else if(m.page==12||m.page==14){image(m,m.page==14?epilogueStart[m.book]+m.cursor:13+m.cursor,0,out);clip(m,0,112,240,160);auto lines=storyLines(m);for(int i=m.storyOffset;i<std::min(int(lines.size()),m.storyOffset+3);i++)text(m,lines[size_t(i)],120-textWidth(m.fonts[0],lines[size_t(i)])/2,112+(i-m.storyOffset)*12,0,out,false,0,false);clip(m);}
 else if(m.page==13){image(m,8,0,out);text(m,"Enter Initials: "+m.draft+std::string(3-m.draft.size(),'-'),120,16,0,out,true);for(int i=0;i<32;i++){std::string ch(1,i==31?char(0x89):"ABCDEFGHIJKLMNOPQRSTUVWXYZ.!?$&"[i]);text(m,ch,64+(i%8)*16,60+(i/8)*16,m.selectedPalette(i),out);}text(m,std::string(1,char(0x81))+" - back        "+char(0x80)+" - select",120,132,0,out,true);}

 else if(m.page==0||m.page==1){auto& p=m.images.at(0);image(m,0,std::min(p.frames-1,std::max(0,m.titleTick-60)/std::max(1,(p.period*60+999)/1000)),out);clip(m,24,128,216,159);selection(m,{get(m,"start"),get(m,"credits")},120,132,16,out);clip(m);}
 else if(m.page==3){image(m,1,m.bookCount()-1,out);clip(m,6,2,234,23);label(m,"books",120,4,0,out,true);clip(m,6,16,234,32);text(m,m.labels.at("book_"+std::to_string(m.cursor)),120,16,0,out,true);clip(m);candle(m,out);if(m.fairy)s2_sprite_composite_bank(m.fairy,0,(m.tick/4)%16,0,240,160,m.line[0],m.line[1],out,n);footer(m,out);}
 else if(m.page==4||m.page==7){image(m,2+m.book,0,out);int preview=std::min(m.cursor,m.selectableChapters()-1);if(m.chapterAvailable(preview))sprite(m,17+m.book*5+preview,40,m.book==5?40:42,out);clip(m,116,8,228,119);for(int i=0;i<5;i++)text(m,(m.book==5?"Game ":"Chapter ")+std::to_string(i+1),128,12+i*22,m.chapterPalette(i),out);clip(m,12,116,80,144);text(m,std::to_string(selectedCoins(m))+(m.book==5?"":"/"+std::to_string(levelCoinTarget(m.scenes[m.book*5+std::min(m.cursor,4)]))),20,120,0,out);footer(m,out);
  if(m.page==7){for(size_t i=0;i<n;i++)out[i]=0xff000000u|((out[i]>>2)&0x3f3f3fu);sprite(m,0,0,0,out);clip(m,32,30,208,132);int scene=m.scenes[m.book*5+m.cursor];bool playable=scene==0||scene==1||scene==2||scene==13||scene==17||scene==25||scene==14||scene==9||scene==11||scene==8||scene==4||scene==10||scene==23||scene==21||scene==29||scene==24||scene==3||scene==19||scene==22||scene==28||scene==12||scene==5||scene==20||scene==15||scene==16;text(m,playable?"Play chapter":"Explore this map",120,52,2,out,true);text(m,playable?"A: Play":"A: Preview",120,76,1,out,true);text(m,"B: Back",120,98,1,out,true);}}
 else if(m.page==2||m.page==9){image(m,8,0,out);clip(m,12,12,228,29);label(m,m.page==9?"erase_slots":"slots",120,16,0,out,true);clip(m,18,63,222,127);std::vector<std::string> lines;for(int i=0;i<3;i++)lines.push_back((m.used&(1<<i))?(m.names[i]+" - "+std::to_string(__builtin_popcount(unsigned(m.complete[i]))*100/25)+"%"):get(m,"new_game"));if(m.page==2)lines.push_back(get(m,"erase"));selection(m,lines,120,64,16,out);footer(m,out);}
 else if(m.page==5){sprite(m,0,0,0,out);clip(m,34,30,206,132);selection(m,{"Resume","Quit Level",get(m,"sleep")},120,54,20,out);}
 else if(m.page==6){if(m.confirm==3){sprite(m,0,0,0,out);clip(m,34,30,206,132);label(m,"quit_level_confirm",120,30,0,out,true);selection(m,{get(m,"cancel"),get(m,"quit")},120,70,16,out);}else if(m.confirm==6){image(m,8,0,out);text(m,"Erase Slot "+std::to_string(m.slot+1)+"?",120,16,0,out,true);selection(m,{get(m,"cancel"),get(m,"erase")},120,80,16,out);}else{sprite(m,0,0,0,out);clip(m,34,30,206,132);label(m,m.confirm==3?"quit_level_confirm":m.confirm==4?"quit_game_confirm":"sleep_confirm",120,44,2,out,true);selection(m,{m.confirm==8?get(m,"sleep"):get(m,"quit"),get(m,"cancel")},120,76,20,out);}}

 else if(m.page==10){sprite(m,0,0,0,out);clip(m,34,30,206,132);text(m,"Sleep",120,60,2,out,true);text(m,"A: Resume",120,85,1,out,true);}
 else if(m.page==8){if(m.tick<480)image(m,17,m.tick/6,out);else image(m,18,((m.tick-480)/6)%80,out);int top=160-m.creditScroll/2;for(size_t i=0;i<m.credits.size();i++){int y=top+int(i)*12;text(m,m.credits[i],(240-textWidth(m.fonts[0],m.credits[i]))/2,y,0,out,false,0,false);}}
 clip(m);if(m.transition){int alpha=std::min(64,m.fadeIn?64-m.transitionTick*4:m.transitionTick*4);if(m.transition==2)s2_mosaic_argb(alpha,out,240,160);else if(m.page==5||m.page==6||m.page==10){for(size_t i=0;i<n;i++)if(out[i]>>24)s2_fade_argb(alpha,out+i,1);}else s2_fade_argb(alpha,out,n);}return 0;
}

extern "C" int s2_frontend_names(void* h,const char* packed){if(!h||!packed||std::strlen(packed)!=9)return -1;auto& m=*static_cast<Menu*>(h);for(int i=0;i<9;i++)if(!std::strchr("ABCDEFGHIJKLMNOPQRSTUVWXYZ.!?$&",packed[i]))return -1;for(int i=0;i<3;i++)m.names[i]=std::string(packed+i*3,3);return 0;}
extern "C" int s2_frontend_initials(void* h,int slot,char* out){if(!h||!out||slot<0||slot>2)return -1;std::memcpy(out,static_cast<Menu*>(h)->names[slot].c_str(),4);return 0;}

extern "C" int s2_frontend_test_books(void* h,int enabled){if(!h)return -1;static_cast<Menu*>(h)->testBooks=enabled!=0;return 0;}

extern "C" int s2_frontend_startup_fade(void* h){if(!h)return -1;auto& m=*static_cast<Menu*>(h);m.startupHold=12;m.transition=1;m.transitionTick=0;m.fadeIn=true;return 0;}

extern "C" int s2_frontend_epilogue(void* h,int scene){if(!h)return -1;int group=-1;const int scenes[6]={17,5,21,22,15,16};for(int i=0;i<6;i++)if(scenes[i]==scene)group=i;if(group<0)return 0;auto& m=*static_cast<Menu*>(h);m.book=group;m.enter(14,0);m.held=m.action=0;m.waiting=false;m.transition=1;m.fadeIn=true;m.transitionTick=0;return 1;}
