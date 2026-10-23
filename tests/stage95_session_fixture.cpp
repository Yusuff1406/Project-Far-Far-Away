#define main stage93_old_main
#include "stage93_session_fixture.cpp"
#undef main
static std::vector<uint8_t> snapshot(OwnedSession&s){QState q;qTransfer(q,s);return q.bytes;}
int main(){
 const char*path="scratch95/test.s2qs";
 for(int scene=0;scene<30;scene++){
  auto*h=create(scene);for(int t=0;t<80;t++)step(h,h->dialogue[64]?(t%2?64:0):(t%12==0?1:0));auto saved=snapshot(*h);assert(!s2_session_save_state(h,path));assert(s2_session_saved_scene(path)==scene);
  for(int t=0;t<30;t++)step(h,16|(t%10==0?1:0));auto future=snapshot(*h);std::vector<uint32_t>image(pixels,pixels+38400);
  assert(!s2_session_load_state(h,path));assert(snapshot(*h)==saved);
  for(int t=0;t<30;t++)step(h,16|(t%10==0?1:0));assert(snapshot(*h)==future);assert(std::equal(image.begin(),image.end(),pixels));s2_session_destroy(h);
 }
 std::cout<<"PASS deterministic full state + future frames, 30 scenes\n";
 auto*h=create(0);quiet(*h);auto before=snapshot(*h);assert(!s2_session_save_state(h,path));
 {std::fstream f(path,std::ios::in|std::ios::out|std::ios::binary);f.seekp(50);f.put('X');}assert(s2_session_load_state(h,path)<0&&snapshot(*h)==before);assert(s2_session_saved_scene(path)<0);
 int serial=0;for(int type:{16,17,14,10,76,77,78,79,80,81,82,83,84,85,89,52,53,54,55,56,57,58,59,60,61,62}){
  int id=s2_session_debug_edit(h,4,type,300,250);assert(id>0);int32_t actor[216];assert(!s2_session_actor_snapshot(h,id,actor));assert(!s2_session_debug_edit(h,8,id,400,250));assert(!s2_session_actor_snapshot(h,id,actor)&&actor[0]==400*256);for(int t=0;t<8;t++)step(h);assert(!s2_session_debug_edit(h,5,id,0,0));serial++;
 }
 assert(s2_session_debug_edit(h,4,999,10,10)<0);assert(s2_session_debug_edit(h,0,-1,10,0)<0);assert(s2_session_debug_edit(h,7,3,999,100)<0);
 for(int hero=3;hero<=7;hero++){h->dialogue[64]=0;h->extra()[1]=0;h->book()[6]=0;assert(!s2_session_debug_edit(h,3,hero,0,0));assert(h->playerType==hero);assert(!s2_session_debug_edit(h,7,hero,175,125));int32_t row[10];assert(fetch(heroTable(hero)+80,row,10,h));for(int t=0;t<30;t++)step(h,16);}
 assert(!s2_session_debug_edit(h,6,7,0,0));assert(!s2_session_debug_edit(h,2,123,0,0));int hp=h->state[89];int32_t hurt[]={1,37,0};assert(s2_session_player_event(h,hurt)==0&&h->state[89]==hp);
 assert(!s2_session_save_state(h,path));auto edited=snapshot(*h);assert(!s2_session_reset(h));assert(!s2_session_load_state(h,path));assert(snapshot(*h)==edited);s2_session_destroy(h);
 std::cout<<"PASS editor "<<serial<<" presets, delete/reuse/move, 5 heroes, trainer, corrupt state rejection\n";
 {auto*p=create(0);p->mini.reset(create(26));for(int i=0;i<20;i++)step(p);auto saved=snapshot(*p);assert(!s2_session_save_state(p,path));for(int i=0;i<20;i++)step(p);assert(!s2_session_load_state(p,path));assert(snapshot(*p)==saved);s2_session_destroy(p);}
 std::cout<<"PASS nested minigame restore\n";
}
