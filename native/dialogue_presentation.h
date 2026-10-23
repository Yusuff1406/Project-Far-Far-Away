#pragma once
#include <cstdint>
#include <string>
#include <vector>
using DialogueFetch=int(*)(uint32_t,int32_t*,int,void*);
int s2_dialogue_lines(uint32_t resource,DialogueFetch fetch,void* ctx,std::vector<std::string>& lines);
int s2_dialogue_draw_text(const std::vector<std::string>& lines,int page,int width,uint32_t* pixels,DialogueFetch fetch,void* ctx);

int s2_dialogue_draw_label(const std::string&,int,int,int,uint32_t*,DialogueFetch,void*);

int s2_dialogue_label_width(const std::string&,DialogueFetch,void*);
