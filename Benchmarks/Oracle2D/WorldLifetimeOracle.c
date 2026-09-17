#include <box2d/box2d.h>
#include <stdio.h>
typedef struct Handles { b2BodyId body; b2ShapeId shape; b2ChainId chain; b2JointId joints[8]; } Handles;
static Handles create(b2WorldId world) {
    Handles h={0};b2BodyDef bd=b2DefaultBodyDef();b2BodyId ground=b2CreateBody(world,&bd);
    bd.type=b2_dynamicBody;h.body=b2CreateBody(world,&bd);
    b2ShapeDef sd=b2DefaultShapeDef();b2Polygon box=b2MakeBox(.5f,.5f);h.shape=b2CreatePolygonShape(h.body,&sd,&box);
    const b2Vec2 points[]={{-2,0},{-1,0},{1,0},{2,0}};b2ChainDef cd=b2DefaultChainDef();cd.points=points;cd.count=4;h.chain=b2CreateChain(ground,&cd);
    b2DistanceJointDef d0=b2DefaultDistanceJointDef();d0.bodyIdA=ground;d0.bodyIdB=h.body;h.joints[0]=b2CreateDistanceJoint(world,&d0);
    b2FilterJointDef d1=b2DefaultFilterJointDef();d1.bodyIdA=ground;d1.bodyIdB=h.body;h.joints[1]=b2CreateFilterJoint(world,&d1);
    b2MotorJointDef d2=b2DefaultMotorJointDef();d2.bodyIdA=ground;d2.bodyIdB=h.body;h.joints[2]=b2CreateMotorJoint(world,&d2);
    b2MouseJointDef d3=b2DefaultMouseJointDef();d3.bodyIdA=ground;d3.bodyIdB=h.body;h.joints[3]=b2CreateMouseJoint(world,&d3);
    b2PrismaticJointDef d4=b2DefaultPrismaticJointDef();d4.bodyIdA=ground;d4.bodyIdB=h.body;h.joints[4]=b2CreatePrismaticJoint(world,&d4);
    b2RevoluteJointDef d5=b2DefaultRevoluteJointDef();d5.bodyIdA=ground;d5.bodyIdB=h.body;h.joints[5]=b2CreateRevoluteJoint(world,&d5);
    b2WeldJointDef d6=b2DefaultWeldJointDef();d6.bodyIdA=ground;d6.bodyIdB=h.body;h.joints[6]=b2CreateWeldJoint(world,&d6);
    b2WheelJointDef d7=b2DefaultWheelJointDef();d7.bodyIdA=ground;d7.bodyIdB=h.body;h.joints[7]=b2CreateWheelJoint(world,&d7);
    return h;
}
static void record(int stage,Handles h) {
    printf("lifetime_%d %d %d %d",stage,b2Body_IsValid(h.body),b2Shape_IsValid(h.shape),b2Chain_IsValid(h.chain));
    for(int i=0;i<8;i++)printf(" %d",b2Joint_IsValid(h.joints[i]));printf("\n");
}
int main(void){
    b2WorldDef wd=b2DefaultWorldDef();b2WorldId world=b2CreateWorld(&wd);Handles old=create(world);
    record(0,old);b2DestroyWorld(world);record(1,old);
    world=b2CreateWorld(&wd);Handles fresh=create(world);record(2,old);record(3,fresh);b2DestroyWorld(world);
}
