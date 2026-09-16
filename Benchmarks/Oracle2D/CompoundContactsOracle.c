#include <box2d/box2d.h>
#include <assert.h>
#include <stdio.h>

static b2ShapeId surfaces[2];
static int surface(b2ShapeId a, b2ShapeId b) {
    for (int i=0;i<2;++i) if (B2_ID_EQUALS(a,surfaces[i]) || B2_ID_EQUALS(b,surfaces[i])) return 1<<i;
    assert(false); return 0;
}
static b2ShapeId add_surface(b2BodyId body, float x, bool events) {
    b2ShapeDef d=b2DefaultShapeDef(); d.enableContactEvents=events; d.enableHitEvents=true;
    b2Polygon shape=b2MakeOffsetBox(.5f,.5f,(b2Vec2){x,0},b2Rot_identity);
    return b2CreatePolygonShape(body,&d,&shape);
}
static void record(b2WorldId world, b2BodyId visitor, int stage) {
    b2ContactEvents e=b2World_GetContactEvents(world);
    int begins=0, ends=0, hits=0, contacts=0;
    for(int i=0;i<e.beginCount;++i) begins+=surface(e.beginEvents[i].shapeIdA,e.beginEvents[i].shapeIdB);
    for(int i=0;i<e.endCount;++i) ends+=surface(e.endEvents[i].shapeIdA,e.endEvents[i].shapeIdB);
    for(int i=0;i<e.hitCount;++i) hits+=surface(e.hitEvents[i].shapeIdA,e.hitEvents[i].shapeIdB);
    b2ContactData data[4]; int count=b2Body_GetContactData(visitor,data,4);
    for(int i=0;i<count;++i) contacts+=surface(data[i].shapeIdA,data[i].shapeIdB);
    printf("stage_%d %d %d %d %d %d %d %d %d\n",stage,e.beginCount,begins,e.endCount,ends,e.hitCount,hits,count,contacts);
}
static void scenario(bool reverse) {
    b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=b2Vec2_zero;
    b2WorldId world=b2CreateWorld(&wd);
    b2BodyDef bd=b2DefaultBodyDef(); b2BodyId fixed=b2CreateBody(world,&bd);
    for(int n=0;n<2;++n) { int i=reverse?1-n:n; surfaces[i]=add_surface(fixed,i==0?-2:2,true); }
    bd.type=b2_dynamicBody; bd.position=(b2Vec2){0,.9f}; bd.enableSleep=false; bd.fixedRotation=true;
    b2BodyId visitor=b2CreateBody(world,&bd);
    b2ShapeDef sd=b2DefaultShapeDef(); b2Polygon box=b2MakeBox(3,.5f); b2CreatePolygonShape(visitor,&sd,&box);
    for(int stage=0;stage<10;++stage) {
        if(stage==1) b2Body_EnableContactEvents(fixed,false);
        if(stage==2) b2Body_SetTransform(visitor,(b2Vec2){4,.9f},b2Rot_identity);
        if(stage==3) b2Shape_EnableContactEvents(surfaces[0],true);
        if(stage==4) b2Body_SetTransform(visitor,(b2Vec2){0,.9f},b2Rot_identity);
        if(stage==5) b2DestroyShape(surfaces[0],true);
        if(stage==6) surfaces[0]=add_surface(fixed,-2,false);
        if(stage==7) b2Body_EnableContactEvents(fixed,true);
        if(stage==8) b2Body_SetTransform(visitor,(b2Vec2){0,3},b2Rot_identity);
        if(stage==9) { b2Body_SetTransform(visitor,(b2Vec2){0,.9f},b2Rot_identity); b2Body_SetLinearVelocity(visitor,(b2Vec2){0,-5}); }
        b2World_Step(world,.001f,4);
        record(world,visitor,stage+(reverse?10:0));
    }
    b2DestroyWorld(world);
}
static void support(void) {
    b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=(b2Vec2){0,-10}; b2WorldId world=b2CreateWorld(&wd);
    b2BodyDef bd=b2DefaultBodyDef(); b2BodyId fixed=b2CreateBody(world,&bd);
    surfaces[0]=add_surface(fixed,-2,true); surfaces[1]=add_surface(fixed,2,true);
    bd.type=b2_dynamicBody; bd.position=(b2Vec2){0,1.02f}; bd.enableSleep=false;
    b2BodyId visitor=b2CreateBody(world,&bd);
    b2ShapeDef sd=b2DefaultShapeDef(); b2Polygon box=b2MakeBox(3,.5f); b2CreatePolygonShape(visitor,&sd,&box);
    for(int i=0;i<120;++i) b2World_Step(world,1.0f/60,4);
    b2ContactData data[4]; int count=b2Body_GetContactData(visitor,data,4); int supported=0;
    for(int i=0;i<count;++i) {
        float impulse=0; for(int j=0;j<data[i].manifold.pointCount;++j) impulse+=data[i].manifold.points[j].normalImpulse;
        assert(impulse>0); supported+=surface(data[i].shapeIdA,data[i].shapeIdB);
    }
    b2Vec2 p=b2Body_GetPosition(visitor),v=b2Body_GetLinearVelocity(visitor);
    printf("support %d %d %.9g %.9g %.9g %.9g %.9g\n",count,supported,p.x,p.y,b2Rot_GetAngle(b2Body_GetRotation(visitor)),v.x,v.y);
    b2DestroyWorld(world);
}
static void before_touch(void) {
 b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=b2Vec2_zero;
 b2WorldId w=b2CreateWorld(&wd);
 b2BodyDef bd=b2DefaultBodyDef(); b2BodyId fixed=b2CreateBody(w,&bd);
 b2ShapeDef sd=b2DefaultShapeDef(); sd.enableContactEvents=false;
 b2Polygon box=b2MakeBox(.5f,.5f); b2CreatePolygonShape(fixed,&sd,&box);
 bd.type=b2_dynamicBody; bd.position=(b2Vec2){0,1.05f}; bd.enableSleep=false;
 b2BodyId visitor=b2CreateBody(w,&bd); b2CreatePolygonShape(visitor,&sd,&box);
 for(int i=0;i<4;++i) {
  if(i==1) { b2Body_EnableContactEvents(fixed,true); b2Body_SetTransform(visitor,(b2Vec2){0,.9f},b2Rot_identity); }
  if(i==2) { b2Body_EnableContactEvents(fixed,false); b2Body_SetTransform(visitor,(b2Vec2){0,1.05f},b2Rot_identity); }
  if(i==3) b2Body_SetTransform(visitor,(b2Vec2){0,.9f},b2Rot_identity);
  b2Body_SetLinearVelocity(visitor,b2Vec2_zero); b2World_Step(w,.001f,4);
  b2ContactEvents e=b2World_GetContactEvents(w); printf("precontact_%d %d %d\n",i,e.beginCount,e.endCount);
 }
 b2DestroyWorld(w);
}

static void connected_joint_case(void) {
    b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=b2Vec2_zero;
    b2WorldId world=b2CreateWorld(&wd);
    b2BodyDef bd=b2DefaultBodyDef(); b2BodyId fixed=b2CreateBody(world,&bd);
    surfaces[0]=add_surface(fixed,-2,true); surfaces[1]=add_surface(fixed,2,true);
    bd.type=b2_dynamicBody; bd.position=(b2Vec2){0,.9f}; bd.enableSleep=false; bd.fixedRotation=true;
    b2BodyId visitor=b2CreateBody(world,&bd);
    b2ShapeDef sd=b2DefaultShapeDef(); b2Polygon box=b2MakeBox(3,.5f); b2CreatePolygonShape(visitor,&sd,&box);
    b2World_Step(world,.001f,4); record(world,visitor,20);
    b2DistanceJointDef jd=b2DefaultDistanceJointDef(); jd.bodyIdA=fixed; jd.bodyIdB=visitor; jd.length=.9f;
    b2JointId joint=b2CreateDistanceJoint(world,&jd);
    b2World_Step(world,.001f,4); record(world,visitor,21);
    b2DestroyJoint(joint);
    b2Body_SetTransform(visitor,(b2Vec2){0,3},b2Rot_identity);
    b2World_Step(world,.001f,4); record(world,visitor,22);
    b2Body_SetTransform(visitor,(b2Vec2){0,.9f},b2Rot_identity);
    b2World_Step(world,.001f,4); record(world,visitor,23);
    b2DestroyWorld(world);
}
int main(void) { scenario(false); scenario(true); support(); before_touch(); connected_joint_case(); }
