// Box2D 3.1.1 public observations; no private solver state is read.
#include <box2d/box2d.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
// Match the public Silex radian input with the same unit rotation.
static b2Rot rotation(float angle) { return (b2Rot){cosf(angle),sinf(angle)}; }
static int fail_assert(const char* condition, const char* file, int line) {
    fprintf(stderr,"Box2D assertion: %s (%s:%d)\n",condition,file,line); exit(2);
}

static void configure(int f, int variant, b2JointId j, int stage) {
    bool spring = variant % 2 == 1, limit = variant >= 2;
    float lower = -.25f, upper = .4f;
    if (stage == 6) { spring = !spring; lower = -2.8f; upper = 2.8f; }
    if (f == 0) {
        b2DistanceJoint_SetLength(j, 1.2f);
        b2DistanceJoint_EnableSpring(j, spring);
        b2DistanceJoint_SetSpringHertz(j, 3);
        b2DistanceJoint_SetSpringDampingRatio(j, .7f);
        b2DistanceJoint_EnableLimit(j, limit);
        b2DistanceJoint_SetLengthRange(j, stage == 6 ? .01f : .5f, stage == 6 ? 10 : .9f);
    }
    if (f == 2) { b2MotorJoint_SetLinearOffset(j, (b2Vec2){.3f,-.1f}); b2MotorJoint_SetAngularOffset(j,.2f); }
    if (f == 3) { b2MouseJoint_SetTarget(j,(b2Vec2){.8f,-.4f}); }
    if (f == 4) {
        b2PrismaticJoint_EnableSpring(j,spring); b2PrismaticJoint_SetSpringHertz(j,3);
        b2PrismaticJoint_SetSpringDampingRatio(j,.7f); b2PrismaticJoint_EnableLimit(j,limit);
        b2PrismaticJoint_SetLimits(j,lower,upper); b2PrismaticJoint_SetTargetTranslation(j,.2f);
    }
    if (f == 5) { b2RevoluteJoint_EnableLimit(j,limit); b2RevoluteJoint_SetLimits(j,lower,upper); }
    if (f == 6) { b2WeldJoint_SetLinearDampingRatio(j,1); b2WeldJoint_SetAngularDampingRatio(j,1); b2WeldJoint_SetLinearHertz(j,spring ? 3 : 0); b2WeldJoint_SetAngularHertz(j,limit ? 3 : 0); }
    if (f == 7) {
        b2WheelJoint_EnableSpring(j,spring); b2WheelJoint_SetSpringHertz(j,3);
        b2WheelJoint_SetSpringDampingRatio(j,.7f); b2WheelJoint_EnableLimit(j,limit);
        b2WheelJoint_SetLimits(j,lower,upper);
    }
}

static void record(int f,int g,int v,int s,b2JointId j,b2BodyId a,b2BodyId b) {
    b2Vec2 pa=b2Body_GetWorldPoint(a,b2Joint_GetLocalAnchorA(j));
    b2Vec2 pb=b2Body_GetWorldPoint(b,b2Joint_GetLocalAnchorB(j));
    b2Vec2 dp=b2Sub(pb,pa);
    if (f==3) dp=b2Sub(b2MouseJoint_GetTarget(j),pb);
    float measure=0,speed=0;
    if (f==0) measure=b2DistanceJoint_GetCurrentLength(j);
    if (f==4) { measure=b2PrismaticJoint_GetTranslation(j); speed=b2PrismaticJoint_GetSpeed(j); }
    if (f==5) measure=b2RevoluteJoint_GetAngle(j);
    if (f==7) {
        // Box2D 3.1.1 has no wheel translation/speed getters. Use public body kinematics.
        b2Vec2 axis=b2Body_GetWorldVector(a,b2Joint_GetLocalAxisA(j));
        measure=b2Dot(dp,axis);
        b2Vec2 va=b2Body_GetWorldPointVelocity(a,pa),vb=b2Body_GetWorldPointVelocity(b,pb);
        speed=b2Dot(dp,b2CrossSV(b2Body_GetAngularVelocity(a),axis))+b2Dot(axis,b2Sub(vb,va));
    }
    printf("observe_%d_%d_%d_%d %.9g %.9g %.9g %.9g %.9g %.9g\n",f,g,v,s,
        measure,speed,b2Joint_GetLinearSeparation(j),b2Joint_GetAngularSeparation(j),dp.x,dp.y);
}
static void run(int f,int g,int v) {
    b2WorldDef wd=b2DefaultWorldDef();wd.gravity=b2Vec2_zero;
    b2WorldId world=b2CreateWorld(&wd);
    b2BodyDef bd=b2DefaultBodyDef();bd.type=g ? b2_dynamicBody : b2_staticBody;
    b2BodyId a=b2CreateBody(world,&bd);bd.type=b2_dynamicBody;b2BodyId b=b2CreateBody(world,&bd);
    b2MassData mass={.mass=2,.rotationalInertia=3,.center={.1f,-.2f}};
    if(g)b2Body_SetMassData(a,mass);b2Body_SetMassData(b,mass);
    if(g){b2Body_SetLinearVelocity(a,(b2Vec2){.3f,-.2f});b2Body_SetAngularVelocity(a,.2f);}
    b2Body_SetLinearVelocity(b,(b2Vec2){-.4f,.7f});b2Body_SetAngularVelocity(b,-.3f);
    b2JointId j;
    if(f==0) { b2DistanceJointDef d=b2DefaultDistanceJointDef();d.bodyIdA=a;d.bodyIdB=b;d.localAnchorA=(b2Vec2){-.2f,.1f};d.localAnchorB=(b2Vec2){.3f,-.4f};d.length=1.2f;j=b2CreateDistanceJoint(world,&d); }
    if(f==1) { b2FilterJointDef d=b2DefaultFilterJointDef();d.bodyIdA=a;d.bodyIdB=b;j=b2CreateFilterJoint(world,&d); }
    if(f==2) { b2MotorJointDef d=b2DefaultMotorJointDef();d.bodyIdA=a;d.bodyIdB=b;j=b2CreateMotorJoint(world,&d); }
    if(f==3) { b2MouseJointDef d=b2DefaultMouseJointDef();d.bodyIdA=a;d.bodyIdB=b;d.target=(b2Vec2){.2f,.3f};j=b2CreateMouseJoint(world,&d); }
    if(f==4) { b2PrismaticJointDef d=b2DefaultPrismaticJointDef();d.bodyIdA=a;d.bodyIdB=b;d.localAnchorA=(b2Vec2){.2f,.3f};d.localAnchorB=(b2Vec2){.2f,.3f};d.localAxisA=(b2Vec2){.6f,.8f};j=b2CreatePrismaticJoint(world,&d); }
    if(f==5) { b2RevoluteJointDef d=b2DefaultRevoluteJointDef();d.bodyIdA=a;d.bodyIdB=b;d.localAnchorA=(b2Vec2){.2f,.3f};d.localAnchorB=(b2Vec2){.2f,.3f};j=b2CreateRevoluteJoint(world,&d); }
    if(f==6) { b2WeldJointDef d=b2DefaultWeldJointDef();d.bodyIdA=a;d.bodyIdB=b;d.localAnchorA=(b2Vec2){.2f,.3f};d.localAnchorB=(b2Vec2){.2f,.3f};j=b2CreateWeldJoint(world,&d); }
    if(f==7) { b2WheelJointDef d=b2DefaultWheelJointDef();d.bodyIdA=a;d.bodyIdB=b;d.localAnchorA=(b2Vec2){.2f,.3f};d.localAnchorB=(b2Vec2){.2f,.3f};d.localAxisA=(b2Vec2){.6f,.8f};j=b2CreateWheelJoint(world,&d); }
    configure(f,v,j,0);
    for(int s=0;s<8;s++) {
        if(s==1){b2Body_SetTransform(a,(b2Vec2){.2f,.1f},rotation(.4f));b2Body_SetTransform(b,(b2Vec2){1.3f,-.8f},rotation(-.7f));}
        if(s==2){
            if(f!=1){
                if(f!=3)b2Joint_SetLocalAnchorA(j,(b2Vec2){.4f,.1f});
                b2Joint_SetLocalAnchorB(j,(b2Vec2){-.2f,.3f});
            }
            if(f==4||f==7)b2Joint_SetLocalAxisA(j,(b2Vec2){-.8f,.6f});
            if(f==4||f==5||f==6)b2Joint_SetReferenceAngle(j,.25f);
            configure(f,v,j,2);
        }
        if(s==3)b2World_Step(world,0,4);
        if(s==4)b2World_Step(world,1.0f/60,4);
        if(s==5){b2Body_SetTransform(a,(b2Vec2){-.4f,.2f},rotation(-2.8f));b2Body_SetTransform(b,(b2Vec2){-1.5f,.9f},rotation(3));}
        if(s==6)configure(f,v,j,6);
        if(s==7){if(g){b2Body_SetLinearVelocity(a,b2Vec2_zero);b2Body_SetAngularVelocity(a,0);}b2Body_SetLinearVelocity(b,b2Vec2_zero);b2Body_SetAngularVelocity(b,0);}
        record(f,g,v,s,j,a,b);
    }
    b2DestroyWorld(world);
}
int main(void){b2SetAssertFcn(fail_assert);for(int f=0;f<8;f++)for(int g=0;g<2;g++)for(int v=0;v<4;v++)run(f,g,v);}
