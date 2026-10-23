#define main old
#include "stage93_session_fixture.cpp"
#undef main
#include <new>
#include <cstdlib>
static bool measureAllocs=false;static size_t allocations=0;
void* operator new(std::size_t n){if(measureAllocs)++allocations;if(auto*p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void*p)noexcept{std::free(p);}void operator delete[](void*p)noexcept{std::free(p);}
void operator delete(void*p,std::size_t)noexcept{std::free(p);}void operator delete[](void*p,std::size_t)noexcept{std::free(p);}
static OwnedSession* pickup(int hero,int type){for(int dy:{-16,0,-24})for(int dx:{-16,0,16,-24,24}){auto*s=create(0);quiet(*s);for(auto&a:s->actors)a.state[40]|=1;for(int t=0;t<30;t++)step(s);assert(!s2_session_debug_edit(s,3,hero,0,0));qPlace(s->state,200,300);s->state[18]=dx>0?1:0;for(int t=0;t<60;t++)step(s);int x=s->state[0]/256,y=s->state[1]/256;int id=s2_session_debug_edit(s,4,type,x-dx,y+dy);assert(id>0);for(int t=0;t<80;t++)step(s);for(int t=0;t<90;t++)step(s,t==2?4:0);if(s->extra()[3]==id&&s->extra()[1])return s;s2_session_destroy(s);}return nullptr;}

int main(){
 for(bool combo:{false,true}){
  auto*s=pickup(3,76);assert(s&&s->extra()[1]==6);int id=s->extra()[3];s->trainerFlags=1;
  step(s,2);assert(s->extra()[0]==7&&s->extra()[3]==id);for(int t=0;t<70;t++)step(s);
  bool pressed=false,stomp=false,fallingHit=false,landed=false;
  for(int t=0;t<140;t++){
   int buttons=t==0?(combo?3:1):0;
   if(!combo&&!pressed&&(s->extra()[0]==3||s->extra()[0]==4)){buttons=2;pressed=true;}
   step(s,buttons);stomp|=s->extra()[0]==19;fallingHit|=s->extra()[0]==20&&s->state[42]==9;landed|=s->extra()[0]==21;
   assert(s->extra()[1]==6&&s->extra()[3]==id);
  }
  assert(stomp&&fallingHit&&landed);
  // The retained physical key still follows the lock consume/detach callback.
  assert(!consumeKey(s)&&!s->extra()[3]&&!s->extra()[1]);
  auto key=std::find_if(s->actors.begin(),s->actors.end(),[&](auto&a){return a.spawn[0]==id;});assert(key!=s->actors.end()&&(key->state[40]&1));
  s2_session_destroy(s);
 }
 std::cout<<"PASS actual key pickup: ground B, jump+B and A+B stomp with impact event, landing, retention and consume\n";
 // Render caches must survive repeated presentation without allocating each frame.
 for(int scene=0;scene<30;scene++)for(int width:{240,356,640}){
  auto*s=create(scene);quiet(*s);assert(!s2_session_set_viewport(s,width,160));std::vector<uint32_t> out(size_t(width)*160);int32_t data[8];
  for(int t=0;t<30;t++){assert(!s2_session_update(s,0,out.data(),out.size(),data,1));assert(!s2_session_present(s,128,out.data(),out.size()));}
  for(int t=0;t<4;t++)assert(!s2_session_present(s,t*64,out.data(),out.size()));
  QState before;qTransfer(before,*s);allocations=0;measureAllocs=true;
  for(int t=0;t<20;t++)assert(!s2_session_present(s,(t%5)*64,out.data(),out.size()));
  measureAllocs=false;if(allocations){std::cerr<<"render allocations scene "<<scene<<" width "<<width<<": "<<allocations<<std::endl;return 1;}
  QState after;qTransfer(after,*s);assert(before.bytes==after.bytes);s2_session_destroy(s);
 }
 std::cout<<"PASS 30 scenes x 3 widths: warmed repeated presentation allocates no C++ heap and preserves state\n";
 for(int mini:{26,7,6,18,27})for(int width:{240,356}){
  auto*a=create(0);auto*b=create(0);quiet(*a);quiet(*b);a->mini.reset(create(mini));b->mini.reset(create(mini));s2_session_set_viewport(a,width,160);s2_session_set_viewport(b,width,160);std::vector<uint32_t> oldFrame(size_t(width)*160),newFrame(oldFrame.size());int32_t data[8];
  for(int t=0;t<40;t++){int buttons=t%20==10?1:0;assert(!s2_session_step(a,buttons,oldFrame.data(),oldFrame.size(),data));assert(!s2_session_update(b,buttons,newFrame.data(),newFrame.size(),data,1));assert(!s2_session_present(b,256,newFrame.data(),newFrame.size()));assert(oldFrame==newFrame);QState x,y;qTransfer(x,*a);qTransfer(y,*b);assert(x.bytes==y.bytes);}
  assert(!s2_session_pause_frame(a,1,oldFrame.data(),oldFrame.size()));assert(!s2_session_pause_frame(b,1,newFrame.data(),newFrame.size()));assert(oldFrame==newFrame);
  for(int t=0;t<4;t++)assert(!s2_session_present(b,t*64,newFrame.data(),newFrame.size()));allocations=0;measureAllocs=true;for(int t=0;t<20;t++)assert(!s2_session_present(b,(t%5)*64,newFrame.data(),newFrame.size()));measureAllocs=false;assert(!allocations);
  s2_session_destroy(a);s2_session_destroy(b);
 }
 std::cout<<"PASS five child minigames at two widths: exact step/present and pause; warmed presentation has no C++ heap allocation\n";

}
