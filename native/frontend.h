#pragma once
#include <cstdint>
#include <cstddef>
// 0 title,1 main,2 slots,3 books,4 chapters,5 pause,6 confirm,
// 7 unavailable,8 credits,9 erase slots,10 sleep. Actions are consumed once.
extern "C" {
void* s2_frontend_create(const char*,const char*);
void s2_frontend_destroy(void*);
int s2_frontend_epilogue(void*,int scene);
int s2_frontend_open(void*,int,int);
int s2_frontend_restore(void*,const int32_t*);
int s2_frontend_bonus_bests(void*,const int32_t*); // 5 independent bonus records
int s2_frontend_chapter_coins(void*,const int32_t*); // 3 slots x25 chapter counts
int s2_frontend_progress(void*,const int32_t*); // used mask,3 completion masks,3 coin bests
int s2_frontend_step(void*,int);
int s2_frontend_touch(void*,int,int);
int s2_frontend_action(void*);
int s2_frontend_sound(void*);
int s2_frontend_snapshot(void*,int32_t*); // page,cursor,book,slot,tick,scene,used,complete,coins
int s2_frontend_presentation(void*,int32_t*);
int s2_frontend_text_boxes(void*,int32_t*,int);
int s2_frontend_render(void*,uint32_t*,size_t);
}

extern "C" int s2_frontend_names(void*,const char*);
extern "C" int s2_frontend_initials(void*,int,char*);

extern "C" int s2_frontend_test_books(void*,int);

extern "C" int s2_frontend_startup_fade(void*);
