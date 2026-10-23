#define main stage93_old_main
#include "stage93_session_fixture.cpp"
#undef main
static std::vector<uint8_t> encoded(OwnedSession&s){QState q;qTransfer(q,s);return q.bytes;}
int main(){int cases=0;for(int scene=0;scene<30;scene++)for(int width:{240,356}){
 auto*h=create(scene);s2_session_set_viewport(h,width,160);std::vector<uint32_t>hidden(width*160),live(width*160),again(width*160);auto before=encoded(*h);assert(!s2_session_pause_frame(h,1,hidden.data(),hidden.size()));assert(encoded(*h)==before);assert(!s2_session_pause_frame(h,1,again.data(),again.size()));assert(hidden==again&&encoded(*h)==before);
 // Render visible once first to populate the text cache, then verify pause/resume do not tick.
 assert(!s2_session_pause_frame(h,0,live.data(),live.size()));auto populated=encoded(*h);assert(!s2_session_pause_frame(h,1,hidden.data(),hidden.size()));assert(encoded(*h)==populated);assert(!s2_session_pause_frame(h,0,again.data(),again.size()));assert(again==live&&encoded(*h)==populated);assert(hidden!=live);
 int x,y;cameraTarget(*h,x,y);if(h->party.size()>1){x=h->cameraX;y=h->cameraY;}std::vector<uint32_t>tile(width*160);assert(!s2_scene_render(h->decodedScene.get(),x,y,width,160,tile.data(),tile.size()));if(!h->bonus){std::vector<uint8_t>front(width*160*4);assert(!s2_scene_render_front(h->decodedScene.get(),x,y,width,160,front.data(),front.size()));for(size_t i=0;i<tile.size();i++)if(front[4*i+3])tile[i]=0xff000000u|(uint32_t(front[4*i])<<16)|(uint32_t(front[4*i+1])<<8)|front[4*i+2];}assert(hidden==tile);s2_session_destroy(h);cases++;}
 auto*p=create(0);p->mini.reset(create(26));std::vector<uint32_t>a(38400),b(38400);auto before=encoded(*p);assert(!s2_session_pause_frame(p,1,a.data(),a.size()));assert(encoded(*p)==before);assert(!s2_session_pause_frame(p,0,b.data(),b.size()));assert(a!=b);s2_session_destroy(p);std::cout<<"PASS Stage96 tile-only pause/resume: "<<cases<<" scene/width cases + nested mini, state frozen, sprites and HUD removed\n";
}
