// Native wrapping in the original142x43 text area, using extracted ROM glyphs.
#include "dialogue_presentation.h"
#include <algorithm>
static int byte(uint32_t address,DialogueFetch fetch,void* ctx){int32_t word;if(!fetch(address,&word,1,ctx))return -2;return uint32_t(word)&255;}
static int advance(unsigned char ch,DialogueFetch fetch,void* ctx){return byte(0x0830fbac+264+ch,fetch,ctx);}
int s2_dialogue_lines(uint32_t resource,DialogueFetch fetch,void* ctx,std::vector<std::string>& lines){
 int32_t p;if(!fetch(resource,&p,1,ctx)||!fetch(uint32_t(p),&p,1,ctx))return -2;
 std::string text;for(int i=0;i<2048;i++){int ch=byte(uint32_t(p)+uint32_t(i),fetch,ctx);if(ch<0)return ch;if(!ch)break;text.push_back(char(ch));if(i==2047)return -3;}
 lines.clear();std::string line,word;int lineWidth=0,wordWidth=0;
 auto putWord=[&]()->int{if(word.empty())return 0;int space=line.empty()?0:advance(' ',fetch,ctx);if(space<0)return space;if(!line.empty()&&lineWidth+space+wordWidth>142){lines.push_back(line);line.clear();lineWidth=0;space=0;}
  if(wordWidth>142){for(unsigned char ch:word){int w=advance(ch,fetch,ctx);if(w<0)return w;if(lineWidth+w>142){lines.push_back(line);line.clear();lineWidth=0;}line.push_back(char(ch));lineWidth+=w;}}
  else{if(space){line.push_back(' ');lineWidth+=space;}line+=word;lineWidth+=wordWidth;}word.clear();wordWidth=0;return 0;};
 for(unsigned char ch:text){if(ch==' '||ch=='\n'){int e=putWord();if(e)return e;if(ch=='\n'){lines.push_back(line);line.clear();lineWidth=0;}}else{int w=advance(ch,fetch,ctx);if(w<0)return w;word.push_back(char(ch));wordWidth+=w;}}
 int e=putWord();if(e)return e;if(!line.empty()||lines.empty())lines.push_back(line);return 0;
}
static int drawLabel(const std::string& text,int x,int y,int width,uint32_t* pixels,DialogueFetch fetch,void* ctx,int left,int top,int right,int bottom){
 if(!pixels||width<240)return -1;int32_t palette[8];if(!fetch(0x0830f9ac,palette,8,ctx))return -2;
 for(unsigned char ch:text){int w=advance(ch,fetch,ctx);if(w<0)return -2;if(ch==' '){x+=w;continue;}int glyph=byte(0x0830fbac+8+ch,fetch,ctx);if(glyph<0)return -2;int32_t raw[32];if(!fetch(0x0830fbac+520+uint32_t(glyph)*128,raw,32,ctx))return -2;
  for(int py=0;py<16;py++)for(int px=0;px<16;px++){int at=(py/8*2+px/8)*32+(py%8)*4+px%8/2;int value=(uint32_t(raw[at/4])>>((at%4)*8+(px&1)*4))&15;if(!value)continue;uint32_t color=(uint32_t(palette[value/2])>>((value&1)*16))&65535;int xx=x+px,yy=y+py;if(xx>=left&&xx<right&&yy>=top&&yy<bottom)pixels[size_t(yy)*width+xx]=0xff000000u|((color&31)*255/31<<16)|(((color>>5)&31)*255/31<<8)|(((color>>10)&31)*255/31);}
  x+=w;
 }return 0;
}
int s2_dialogue_draw_label(const std::string& text,int x,int y,int width,uint32_t* pixels,DialogueFetch fetch,void* ctx){return drawLabel(text,x,y,width,pixels,fetch,ctx,0,0,width,160);}
int s2_dialogue_draw_text(const std::vector<std::string>& lines,int page,int width,uint32_t* pixels,DialogueFetch fetch,void* ctx){
 if(!pixels||page<0||width<240)return -1;
 // Clip glyph writes directly to the original 142x43 window. No full-screen
 // temporary layer is needed, including on interpolated high-refresh frames.
 int left=(width-240)/2+65,right=(width-240)/2+207;
 for(int row=0;row<3;row++){size_t index=size_t(page)*3+row;if(index>=lines.size())break;int e=drawLabel(lines[index],left,18+row*12,width,pixels,fetch,ctx,left,18,right,61);if(e)return e;}
 return 0;
}

int s2_dialogue_label_width(const std::string& text,DialogueFetch f,void* ctx){int width=0;for(unsigned char ch:text){int n=advance(ch,f,ctx);if(n<0)return n;width+=n;}return width;}
