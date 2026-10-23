// Request-side original 0x080163AC. Low-level mixing/sample playback is external.
#include <cstdint>
using Play=int32_t(*)(int32_t,int32_t,int32_t,int32_t,void*);
using Volume=void(*)(int32_t,uint32_t,void*);
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" uint32_t s2_audio_descriptor_gain(uint32_t master,int32_t volume,int32_t scale){return (master*uint32_t(volume)*uint32_t(scale))>>16;}
// Manager[8]: mode, alternating channel (0/1), master Q8,
// remembered sound IDs for channels 0/1, reserved[3].
extern "C" int s2_audio_sfx(int32_t* manager,const int32_t* descriptor,int32_t scale,Play play,Volume volume,void* ctx){
 if(!manager||!play||!volume||manager[1]<0||manager[1]>1)return -1;
 if(manager[0]!=1)return 0;if(!descriptor)return -1;int32_t id=descriptor[0];if(!id)return 0;
 int channel=manager[1];int32_t voice=play(id,channel,descriptor[1],-1,ctx);
 if(voice==-1){channel^=1;manager[1]=channel;voice=play(id,channel,descriptor[1],-1,ctx);if(voice==-1)return 0;}
 manager[3+channel]=id;uint32_t gain=s2_audio_descriptor_gain(uint32_t(manager[2]),descriptor[2],scale);
 volume(voice,gain,ctx);manager[1]=channel^1;return 1;
}
extern "C" int s2_audio_sfx_resource(int32_t* manager,uint32_t address,int32_t scale,Fetch fetch,Play play,Volume volume,void* ctx){
 if(!manager||!fetch||!play||!volume||manager[1]<0||manager[1]>1)return -1;
 if(manager[0]!=1)return 0;int32_t d[3];if(!fetch(address,d,3,ctx))return -2;return s2_audio_sfx(manager,d,scale,play,volume,ctx);
}
// Original 0x0801DA20: unsigned clamp, not signed saturation.
extern "C" uint32_t s2_audio_volume_byte(uint32_t gain){return gain>255?255:gain;}
// Actor audio routes 34..39 / 56 in 0x08013B8C.
extern "C" int s2_generic_audio_message(int32_t* actor,int cls,int id,int32_t payload,Sink sink,void* ctx){
 if(!actor)return -1;if(cls!=8)return -4;
 if(id>=34&&id<=36){actor[id==34?58:id==35?59:63]=payload;return 0;}
 if(id>=37&&id<=39){if(!(actor[56]&255))return 0;payload=actor[id==37?58:id==38?59:63];if(!payload)return 0;}
 else if(id==56){if(!(actor[56]&255))return 0;}else return -4;
 return sink?sink(11,uint32_t(payload),256,ctx):-4;
}
