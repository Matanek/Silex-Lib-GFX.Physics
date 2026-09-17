// Pinned Box2D 3.1.1 filter-joint lifecycle witness.
#include <box2d/box2d.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int mask(b2ShapeId shape)
{
    uintptr_t id = (uintptr_t)b2Shape_GetUserData(shape);
    return id == 10 ? 1 : id == 20 ? 2 : 0;
}

static void record(b2WorldId world, b2BodyId body, int scene, int stage)
{
    b2ContactEvents events = b2World_GetContactEvents(world);
    b2ContactData contacts[4];
    int count = b2Body_GetContactData(body, contacts, 4);
    int begin_mask = 0, end_mask = 0, contact_mask = 0;
    float impulse = 0;
    for (int i = 0; i < events.beginCount; ++i)
        begin_mask += mask(events.beginEvents[i].shapeIdA) + mask(events.beginEvents[i].shapeIdB);
    for (int i = 0; i < events.endCount; ++i)
        end_mask += mask(events.endEvents[i].shapeIdA) + mask(events.endEvents[i].shapeIdB);
    for (int i = 0; i < count; ++i)
    {
        contact_mask += mask(contacts[i].shapeIdA) + mask(contacts[i].shapeIdB);
        for (int j = 0; j < contacts[i].manifold.pointCount; ++j)
            impulse += contacts[i].manifold.points[j].normalImpulse;
    }
    printf("filter_%d_%d %d %d %d %d %d %d %.9g %.9g %.9g\n", scene, stage,
        events.beginCount, begin_mask, events.endCount, end_mask, count, contact_mask,
        b2Body_GetPosition(body).y, b2Body_GetLinearVelocity(body).y, impulse);
}

static void scenario(int scene, bool immediate)
{
    b2WorldDef wd = b2DefaultWorldDef();
    wd.gravity = b2Vec2_zero;
    wd.contactHertz = 40.0f;
    wd.enableContinuous = false;
    b2WorldId world = b2CreateWorld(&wd);
    b2BodyDef bd = b2DefaultBodyDef();
    b2BodyId ground = b2CreateBody(world, &bd);
    b2ShapeDef sd = b2DefaultShapeDef();
    sd.material.friction = 0.6f;
    sd.enableContactEvents = true;
    for (int i = 0; i < 2; ++i)
    {
        b2Polygon shape = b2MakeOffsetBox(.5f, .5f, (b2Vec2){-2.f + 4.f * i, 0}, b2Rot_identity);
        sd.userData = (void*)(uintptr_t)((i + 1) * 10);
        b2CreatePolygonShape(ground, &sd, &shape);
    }
    bd.type = b2_dynamicBody;
    bd.position = (b2Vec2){0, .99f};
    bd.linearVelocity = (b2Vec2){0, -2};
    bd.fixedRotation = true;
    bd.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &bd);
    b2Polygon shape = b2MakeBox(3, .5f);
    sd.userData = NULL;
    b2CreatePolygonShape(body, &sd, &shape);
    b2Body_SetMassData(body, (b2MassData){.mass = 1});
    b2FilterJointDef fd = b2DefaultFilterJointDef();
    fd.bodyIdA = ground;
    fd.bodyIdB = body;
    b2JointId joint = b2_nullJointId;
    if (scene == 0) joint = b2CreateFilterJoint(world, &fd);
    for (int stage = 0; stage < 8; ++stage)
    {
        if (stage == 1)
        {
            if (scene == 1)
            {
                joint = b2CreateFilterJoint(world, &fd);
                if (immediate)
                {
                    b2Joint_SetCollideConnected(joint, true);
                    b2Joint_SetCollideConnected(joint, false);
                }
            }
            if (scene == 2)
            {
                b2MotorJointDef md = b2DefaultMotorJointDef();
                md.bodyIdA = ground;
                md.bodyIdB = body;
                md.maxForce = 0;
                md.maxTorque = 0;
                md.collideConnected = false;
                joint = b2CreateMotorJoint(world, &md);
            }
            b2Body_SetLinearVelocity(body, (b2Vec2){0, -2});
        }
        if (stage == 2)
        {
            if (scene == 2) b2Joint_SetCollideConnected(joint, true);
            b2Body_SetLinearVelocity(body, (b2Vec2){0, -2});
        }
        if (stage == 3)
        {
            if (scene == 2) b2Joint_SetCollideConnected(joint, false);
            b2Body_SetTransform(body, (b2Vec2){0, 3}, b2Rot_identity);
            b2Body_SetLinearVelocity(body, b2Vec2_zero);
        }
        if (stage == 4)
        {
            if (scene == 2) b2Joint_SetCollideConnected(joint, false);
            b2Body_SetTransform(body, (b2Vec2){0, .99f}, b2Rot_identity);
            b2Body_SetLinearVelocity(body, (b2Vec2){0, -2});
        }
        if (stage == 5)
        {
            if (immediate) b2Joint_SetCollideConnected(joint, true);
            b2DestroyJoint(joint);
            b2Body_SetLinearVelocity(body, b2Vec2_zero);
        }
        if (stage == 6)
        {
            b2Body_SetTransform(body, (b2Vec2){0, 3}, b2Rot_identity);
            b2Body_SetLinearVelocity(body, b2Vec2_zero);
        }
        if (stage == 7)
        {
            b2Body_SetTransform(body, (b2Vec2){0, .99f}, b2Rot_identity);
            b2Body_SetLinearVelocity(body, (b2Vec2){0, -2});
        }
        b2World_Step(world, .001f, 4);
        record(world, body, scene, stage);
    }
    b2DestroyWorld(world);
}

int main(int argc, char** argv)
{
    bool immediate = argc == 2 && strcmp(argv[1], "--immediate") == 0;
    for (int scene = 0; scene < 3; ++scene) scenario(scene, immediate);
}
