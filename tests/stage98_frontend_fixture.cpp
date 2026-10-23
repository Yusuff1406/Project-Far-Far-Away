#include "../native/frontend.cpp"
#include <cassert>
#include <iostream>
static uint32_t pixels98[38400];
int main(){
 auto*h=s2_frontend_create("android/app/src/main/assets/frontend/menu.s2ui","android/app/src/main/assets/session/sprites/bank_328294/bank.s2sp");assert(h);auto&m=*static_cast<Menu*>(h);m.used=1;m.book=0;s2_frontend_open(h,4,0);
 assert(m.chapterPalette(0)==0&&m.chapterPalette(1)==2);m.tick=16;assert(m.chapterPalette(0)==1);m.complete[0]=1;assert(m.chapterPalette(1)==1&&m.chapterPalette(2)==2);m.complete[0]=0;
 for(int key:{16,32,64,128}){m.tick=20;m.held=0;s2_frontend_step(h,key);assert(m.cursor==0&&m.chapterPalette(0)==0&&s2_frontend_sound(h)==63);s2_frontend_step(h,0);assert(!s2_frontend_render(h,pixels98,38400));}
 m.testBooks=true;
 for(int mode=0;mode<3;mode++)for(int panel=0;panel<4;panel++){
  s2_frontend_epilogue(h,16);for(int i=0;i<16;i++)s2_frontend_step(h,0);m.cursor=panel;m.storyOffset=0;m.storyRevealed=10000;
  if(mode==0){m.cursor=3;auto lines=storyLines(m);m.storyOffset=(int(lines.size())-1)/3*3;m.accept();}else if(mode==1){m.held=0;s2_frontend_step(h,8);}else m.back();
  // All fade-out frames still belong to the final story, including its music ID.
  for(int tick=0;tick<32;tick++){assert(!s2_frontend_render(h,pixels98,38400));if(m.page==14)assert(m.book==5);s2_frontend_step(h,0);}
  assert(m.page==3&&m.book==5&&m.cursor==5);
 }
 // Render every frame of normal and repeated completions in all six stories.
 for(int scene:{17,5,21,22,15,16})for(int repeat=0;repeat<2;repeat++){
  assert(s2_frontend_epilogue(h,scene)==1);for(int tick=0;tick<1800&&m.page==14;tick++){assert(!s2_frontend_render(h,pixels98,38400));s2_frontend_step(h,tick%2?0:1);}assert(m.page==(scene==16?3:4));assert(!s2_frontend_render(h,pixels98,38400));
 }
 s2_frontend_destroy(h);std::cout<<"PASS Stage98: white/grey available text, dark locks, blocked white feedback, 12 final A/Start/B exits, all six story transitions twice rendered every frame\n";
}
