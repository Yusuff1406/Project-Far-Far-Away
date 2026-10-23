// Stable listener list broadcast at 0x0800BCF0. Callbacks' return values ignored.
#include <cstdint>
using EventCallback=int(*)(uint32_t,const int32_t*,void*);
using DeferredCallback=void(*)(uint32_t,void*);
extern "C" int s2_event_broadcast(const uint32_t* receivers,const int32_t* adjustments,int n,const int32_t* event,EventCallback callback,void* context){
 if(n<0||(!receivers&&n)||(!adjustments&&n)||!event||!callback)return -1;
 for(int i=0;i<n;i++)callback(receivers[i]+uint32_t(int16_t(adjustments[i])),event,context);return n;
}
// 0x0800BCCC / 0x0800BC94: eight pending virtual-slot-0x20 calls.
extern "C" int s2_deferred_add(uint32_t item,uint32_t* items,int32_t* count){
 if(!items||!count||*count<0||*count>8)return -1;if(*count==8)return 0;items[(*count)++]=item;return 1;
}
extern "C" int s2_deferred_run(uint32_t* items,int32_t* count,DeferredCallback callback,void* context){
 if(!items||!count||!callback||*count<0||*count>8)return -1;int i=0;
 while(i<*count){if(*count>8)return -1;callback(items[i++],context);}*count=0;return i;
}
