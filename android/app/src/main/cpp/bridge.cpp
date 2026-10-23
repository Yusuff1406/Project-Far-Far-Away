#include <jni.h>
#include <cstdint>
#include <algorithm>
#include <cstddef>
#include <vector>
extern "C" int s2_render_file(const char*,int,int,int,int,int,uint8_t*,size_t);
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_MainActivity_renderScene(JNIEnv* env,jclass,jstring path,jint x,jint y){
    const char* p=env->GetStringUTFChars(path,nullptr);if(!p)return nullptr;
    std::vector<uint8_t> rgba(240*160*4);int code=s2_render_file(p,x,y,240,160,-1,rgba.data(),rgba.size());env->ReleaseStringUTFChars(path,p);
    if(code){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Failed to load or render scene");return nullptr;}
    std::vector<jint> pixels(240*160);
    for(size_t i=0;i<pixels.size();i++){size_t j=i*4;uint32_t c=rgba[j+3]?0xff000000u|(uint32_t(rgba[j])<<16)|(uint32_t(rgba[j+1])<<8)|rgba[j+2]:0xff181818u;pixels[i]=static_cast<jint>(c);}
    jintArray out=env->NewIntArray(static_cast<jsize>(pixels.size()));if(out)env->SetIntArrayRegion(out,0,static_cast<jsize>(pixels.size()),pixels.data());return out;
}

extern "C" int s2_sprite_info(const char*,int,int32_t*);
extern "C" int s2_sprite_render_file(const char*,int,int,int,int,int,int,int,uint8_t*,size_t);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_MainActivity_spriteInfo(JNIEnv* env,jclass,jstring path,jint animation){
 const char* p=env->GetStringUTFChars(path,nullptr);if(!p)return nullptr;int32_t data[4];int code=s2_sprite_info(p,animation,data);env->ReleaseStringUTFChars(path,p);
 if(code){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Invalid sprite animation");return nullptr;}
 jintArray result=env->NewIntArray(4);if(result)env->SetIntArrayRegion(result,0,4,reinterpret_cast<const jint*>(data));return result;
}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_MainActivity_renderSprite(JNIEnv* env,jclass,jstring path,jint animation,jint frame,jint flip){
 const char* p=env->GetStringUTFChars(path,nullptr);if(!p)return nullptr;std::vector<uint8_t> rgba(160*160*4);int code=s2_sprite_render_file(p,animation,frame,flip,160,160,80,100,rgba.data(),rgba.size());env->ReleaseStringUTFChars(path,p);
 if(code){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Sprite render failed");return nullptr;}
 std::vector<jint> pixels(160*160);for(size_t i=0;i<pixels.size();i++){size_t j=i*4;pixels[i]=static_cast<jint>((uint32_t(rgba[j+3])<<24)|(uint32_t(rgba[j])<<16)|(uint32_t(rgba[j+1])<<8)|rgba[j+2]);}
 jintArray result=env->NewIntArray(static_cast<jsize>(pixels.size()));if(result)env->SetIntArrayRegion(result,0,static_cast<jsize>(pixels.size()),pixels.data());return result;
}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_MainActivity_advanceAnimation(JNIEnv* env,jclass,jint rate,jint count,jint flags,jint tick,jintArray state){
 if(!state||env->GetArrayLength(state)!=4){env->ThrowNew(env->FindClass("java/lang/IllegalArgumentException"),"Animation state must have four entries");return;}
 jint values[4];env->GetIntArrayRegion(state,0,4,values);if(env->ExceptionCheck())return;s2_animation_step(rate,count,flags,tick,reinterpret_cast<int32_t*>(values));env->SetIntArrayRegion(state,0,4,values);
}

extern "C" int s2_collision_overlay_file(const char*,int32_t,int32_t,int,int,uint8_t*,size_t);
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_MainActivity_renderCollision(JNIEnv* env,jclass,jstring path,jint cameraX,jint cameraY){
 const char* p=env->GetStringUTFChars(path,nullptr);if(!p)return nullptr;std::vector<uint8_t> rgba(240*160*4);int code=s2_collision_overlay_file(p,cameraX,cameraY,240,160,rgba.data(),rgba.size());env->ReleaseStringUTFChars(path,p);
 if(code){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Collision geometry unavailable");return nullptr;}
 std::vector<jint> pixels(240*160);for(size_t i=0;i<pixels.size();i++){size_t j=i*4;pixels[i]=static_cast<jint>((uint32_t(rgba[j+3])<<24)|(uint32_t(rgba[j])<<16)|(uint32_t(rgba[j+1])<<8)|rgba[j+2]);}
 jintArray result=env->NewIntArray(static_cast<jsize>(pixels.size()));if(result)env->SetIntArrayRegion(result,0,static_cast<jsize>(pixels.size()),pixels.data());return result;
}

extern "C" void s2_prototype_init(int32_t*);
extern "C" int s2_prototype_step(const char*,const char*,int,int32_t*);
extern "C" int s2_prototype_anchor(const char*,const int32_t*,int32_t*);
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_PrototypeActivity_resetPrototype(JNIEnv* env,jclass,jintArray state){
 if(!state||env->GetArrayLength(state)!=40){env->ThrowNew(env->FindClass("java/lang/IllegalArgumentException"),"Invalid prototype state");return;}
 int32_t s[40];s2_prototype_init(s);env->SetIntArrayRegion(state,0,40,reinterpret_cast<jint*>(s));
}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_PrototypeActivity_stepAndRender(JNIEnv* env,jclass,jstring scene,jstring collision,jstring sprite,jint buttons,jintArray state){
 if(!state||env->GetArrayLength(state)!=40){env->ThrowNew(env->FindClass("java/lang/IllegalArgumentException"),"Invalid prototype state");return nullptr;}
 jint s[40];env->GetIntArrayRegion(state,0,40,s);if(env->ExceptionCheck())return nullptr;
 const char* sc=env->GetStringUTFChars(scene,nullptr);if(!sc)return nullptr;
 const char* cp=env->GetStringUTFChars(collision,nullptr);if(!cp){env->ReleaseStringUTFChars(scene,sc);return nullptr;}
 const char* sp=env->GetStringUTFChars(sprite,nullptr);if(!sp){env->ReleaseStringUTFChars(scene,sc);env->ReleaseStringUTFChars(collision,cp);return nullptr;}
 int code=s2_prototype_step(cp,sp,buttons,reinterpret_cast<int32_t*>(s));int cx=std::max(0,std::min(3200-240,int(s[0]>>8)-120));int cy=std::max(0,std::min(400-160,int(s[1]>>8)-95));
 std::vector<uint8_t> rgba(240*160*4),actor(240*160*4);
 if(!code)code=s2_render_file(sc,cx,cy,240,160,-1,rgba.data(),rgba.size());
 int32_t anchor[2];if(!code)code=s2_prototype_anchor(sp,reinterpret_cast<int32_t*>(s),anchor);
 if(!code)code=s2_sprite_render_file(sp,s[19],s[22],s[18],240,160,anchor[0]-cx,anchor[1]-cy,actor.data(),actor.size());
 env->ReleaseStringUTFChars(scene,sc);env->ReleaseStringUTFChars(collision,cp);env->ReleaseStringUTFChars(sprite,sp);
 if(code){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Native prototype update failed");return nullptr;}
 std::vector<jint> pixels(240*160);for(size_t i=0;i<pixels.size();i++){size_t j=i*4;const auto& source=actor[j+3]?actor:rgba;uint32_t color=source[j+3]?0xff000000u|(uint32_t(source[j])<<16)|(uint32_t(source[j+1])<<8)|source[j+2]:0xff181818u;pixels[i]=static_cast<jint>(color);}
 s[28]=cx;s[29]=cy;env->SetIntArrayRegion(state,0,40,s);jintArray out=env->NewIntArray(static_cast<jsize>(pixels.size()));if(out)env->SetIntArrayRegion(out,0,static_cast<jsize>(pixels.size()),pixels.data());return out;
}
