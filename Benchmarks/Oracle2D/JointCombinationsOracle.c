#include <box2d/box2d.h>
#include <stdio.h>
#include <math.h>
static void run(int family,int variant,int substeps,int geometry) {
    b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=(b2Vec2){2,-3};
    b2WorldId world=b2CreateWorld(&wd);
    b2Vec2 anchor=geometry>0?(b2Vec2){.2f,.3f}:(b2Vec2){0,0};
    b2Vec2 axis=geometry==2?(b2Vec2){.6f,.8f}:(b2Vec2){1,0};
    b2BodyDef bd=b2DefaultBodyDef(); bd.enableSleep=false;
    if(geometry==2) bd.type=b2_dynamicBody;
    b2BodyId fixed=b2CreateBody(world,&bd);
    if(geometry==2) b2Body_SetMassData(fixed,(b2MassData){.mass=1,.center={0,0},.rotationalInertia=1});
    bd.type=b2_dynamicBody; bd.enableSleep=false;
    b2BodyId body=b2CreateBody(world,&bd);
    b2Body_SetMassData(body,(b2MassData){.mass=1,.center={0,0},.rotationalInertia=1});
    b2JointId joint=b2_nullJointId;
    bool spring=variant==0 || variant==2 || variant==4 || variant==6 || variant==7;
    bool limit=variant!=0 && variant!=3;
    bool motor=variant==3 || variant==4 || variant==5;
    float hertz=variant==6?0:5, lower=variant==7?.15f:.1f, upper=variant==7?.15f:.2f;
    if(family==0) { b2PrismaticJointDef d=b2DefaultPrismaticJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.enableSpring=spring; d.enableLimit=limit; d.enableMotor=motor; d.hertz=hertz; d.dampingRatio=.7f; d.motorSpeed=1.5f;  d.lowerTranslation=lower; d.upperTranslation=upper; d.targetTranslation=.05f; d.maxMotorForce=3; d.localAxisA=axis; joint=b2CreatePrismaticJoint(world,&d); }
    if(family==1) { b2RevoluteJointDef d=b2DefaultRevoluteJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.enableSpring=spring; d.enableLimit=limit; d.enableMotor=motor; d.hertz=hertz; d.dampingRatio=.7f; d.motorSpeed=1.5f; d.lowerAngle=lower; d.upperAngle=upper; d.targetAngle=.05f; d.maxMotorTorque=3; joint=b2CreateRevoluteJoint(world,&d); }
    if(family==2) { b2WeldJointDef d=b2DefaultWeldJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.linearHertz=variant%2==1?5:0; d.angularHertz=variant%4>=2?5:0; d.linearDampingRatio=.7f; d.angularDampingRatio=.7f; joint=b2CreateWeldJoint(world,&d); }
    if(family==3) { b2WheelJointDef d=b2DefaultWheelJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.enableSpring=spring; d.enableLimit=limit; d.enableMotor=motor; d.hertz=hertz; d.dampingRatio=.7f; d.motorSpeed=1.5f;  d.lowerTranslation=lower; d.upperTranslation=upper; d.maxMotorTorque=3; d.localAxisA=axis; joint=b2CreateWheelJoint(world,&d); }
    if(family==4) { b2DistanceJointDef d=b2DefaultDistanceJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.enableSpring=spring; d.enableLimit=limit; d.enableMotor=motor; d.hertz=hertz; d.dampingRatio=.7f; d.motorSpeed=1.5f; d.maxMotorForce=3; d.length=.8f; d.minLength=lower+.5f; d.maxLength=upper+.5f; joint=b2CreateDistanceJoint(world,&d); }
    b2Body_SetTransform(body,(b2Vec2){.7f,.9f},(b2Rot){cosf(.25f),sinf(.25f)});
    for(int step=0;step<8;++step) {
        b2World_Step(world,1.0f/60,substeps);
        b2Vec2 p=b2Body_GetPosition(body),v=b2Body_GetLinearVelocity(body),f=b2Joint_GetConstraintForce(joint);
        printf("combination_%d_%d_%d_%d_%d %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n",family,variant,substeps,step,geometry,p.x,p.y,b2Rot_GetAngle(b2Body_GetRotation(body)),v.x,v.y,b2Body_GetAngularVelocity(body),f.x,f.y,b2Joint_GetConstraintTorque(joint));
    }
    b2DestroyWorld(world);
}
int main(void) { for(int geometry=0;geometry<3;++geometry) for(int family=0;family<5;++family) for(int variant=0;variant<8;++variant) for(int steps=1;steps<=8;steps*=2) run(family,variant,steps,geometry); }
