#include <box2d/box2d.h>
#include <stdio.h>

static const b2Circle circle = {{0,0}, .5f};
static const b2Capsule capsule = {{-.25f,0},{.25f,0},.5f};
static const b2Segment segment = {{-2,0},{2,0}};
static void shape(b2BodyId body, int family, bool fixed) {
    b2ShapeDef sd=b2DefaultShapeDef(); sd.material.friction=0;
    sd.enableContactEvents=true; sd.enableHitEvents=true;
    if(family==0) b2CreateCircleShape(body,&sd,&circle);
    else if(family==1) { b2Polygon box=b2MakeBox(.5f,.5f); b2CreatePolygonShape(body,&sd,&box); }
    else if(family==3 && fixed) b2CreateSegmentShape(body,&sd,&segment);
    else b2CreateCapsuleShape(body,&sd,&capsule);
}
static void run(int family,int gap_index,int speed_index,int substeps,int timing) {
    const float gaps[]={.004f,.01f,.019f,.021f};
    const float speeds[]={0,-.3f,-3,-1};
    float y=(family==3?.5f:1)+gaps[gap_index];
    b2Transform a=b2Transform_identity,b={{0,y},b2Rot_identity};
    b2Manifold m={0};
    if(family==0) m=b2CollideCircles(&circle,a,&circle,b);
    if(family==1) { b2Polygon p=b2MakeBox(.5f,.5f); m=b2CollidePolygons(&p,a,&p,b); }
    if(family==2) m=b2CollideCapsules(&capsule,a,&capsule,b);
    if(family==3) m=b2CollideSegmentAndCapsule(&segment,a,&capsule,b);
    b2WorldDef wd=b2DefaultWorldDef();wd.gravity=b2Vec2_zero;wd.enableContinuous=false;wd.contactHertz=40.0f;
    b2WorldId world=b2CreateWorld(&wd);
    b2BodyDef bd=b2DefaultBodyDef();b2BodyId ground=b2CreateBody(world,&bd);shape(ground,family,true);
    bd.type=b2_dynamicBody;bd.position=(b2Vec2){0,y};bd.linearVelocity=(b2Vec2){0,speeds[speed_index]};bd.fixedRotation=true;bd.enableSleep=false;
    b2BodyId body=b2CreateBody(world,&bd);shape(body,family,false);
    b2Body_SetMassData(body,(b2MassData){.mass=1,.center={0,0},.rotationalInertia=0});
    for(int step=0;step<6;++step) {
        b2World_Step(world,timing==0?1.f/60:1.f/600,substeps);
        b2ContactEvents e=b2World_GetContactEvents(world);
        b2ContactData data[4];int count=b2Body_GetContactData(body,data,4),points=0;float impulse=0,separation=0;
        for(int i=0;i<count;++i) { points+=data[i].manifold.pointCount;for(int j=0;j<data[i].manifold.pointCount;++j) { impulse+=data[i].manifold.points[j].normalImpulse; if(j==0) separation=data[i].manifold.points[j].separation; } }
        printf("spec_%d_%d_%d_%d_%d_%d %d %.9g %.9g %.9g %d %d %d %d %d %.9g %.9g\n",family,gap_index,speed_index,substeps,step,timing,m.pointCount,m.pointCount?m.points[0].separation:0,b2Body_GetPosition(body).y,b2Body_GetLinearVelocity(body).y,e.beginCount,e.endCount,e.hitCount,count,points,separation,impulse);
    }
    b2DestroyWorld(world);
}
int main(void) {for(int f=0;f<4;++f)for(int g=0;g<4;++g)for(int v=0;v<4;++v)for(int s=1;s<=4;s*=4)for(int t=0;t<2;++t)run(f,g,v,s,t);}
