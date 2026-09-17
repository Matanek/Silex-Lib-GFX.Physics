#include <box2d/box2d.h>
#include "WorkerOptions.h"
#include <stdio.h>
#include <math.h>
#include <assert.h>
static void run(OracleTaskSystem* tasks,int family,int tuning,int substeps,int geometry) {
    b2WorldDef wd=b2DefaultWorldDef(); wd.gravity=(b2Vec2){2,-3};
    oracle_tasks_configure(tasks,&wd);
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
    if(family==0) { b2PrismaticJointDef d=b2DefaultPrismaticJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; d.localAxisA=axis; joint=b2CreatePrismaticJoint(world,&d); }
    if(family==1) { b2RevoluteJointDef d=b2DefaultRevoluteJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; joint=b2CreateRevoluteJoint(world,&d); }
    if(family==2) { b2WeldJointDef d=b2DefaultWeldJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor; joint=b2CreateWeldJoint(world,&d); }
    if(family==3) { b2WheelJointDef d=b2DefaultWheelJointDef(); d.bodyIdA=fixed; d.bodyIdB=body; d.localAnchorA=anchor; d.localAnchorB=anchor;  d.enableSpring=false; d.localAxisA=axis; joint=b2CreateWheelJoint(world,&d); }
    const float frequencies[]={0,5,5,60,10000,5,60};
    const float damping[]={0,0,2,2,2,4,2};
    if(tuning!=3 && tuning!=6) b2Joint_SetConstraintTuning(joint,frequencies[tuning],damping[tuning]);
    float hertz=0,ratio=0; b2Joint_GetConstraintTuning(joint,&hertz,&ratio);
    assert(hertz==frequencies[tuning] && ratio==damping[tuning]);
    b2Body_SetTransform(body,(b2Vec2){.7f,.9f},(b2Rot){cosf(.25f),sinf(.25f)});
    for(int step=0;step<8;++step) {
        if(tuning==6 && step==3) b2Joint_SetConstraintTuning(joint,5,4);
        b2World_Step(world,1.0f/60,substeps);
        b2Vec2 p=b2Body_GetPosition(body),v=b2Body_GetLinearVelocity(body),f=b2Joint_GetConstraintForce(joint);
        printf("rigid_%d_%d_%d_%d_%d %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n",family,tuning,substeps,step,geometry,p.x,p.y,b2Rot_GetAngle(b2Body_GetRotation(body)),v.x,v.y,b2Body_GetAngularVelocity(body),f.x,f.y,b2Joint_GetConstraintTorque(joint));
    }
    b2DestroyWorld(world);
}
int main(int argc, char** argv)
{
    OracleWorkers workers;
    if (!oracle_workers_open(&workers, argc, argv)) return 2;
    for (int geometry = 0; geometry < 3; ++geometry)
        for (int family = 0; family < 4; ++family)
            for (int tuning = 0; tuning < 7; ++tuning)
                for (int steps = 1; steps <= 8; steps *= 2)
                    run(workers.tasks, family, tuning, steps, geometry);
    return oracle_workers_close(&workers);
}
