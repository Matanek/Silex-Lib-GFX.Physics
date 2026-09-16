// SPDX-License-Identifier: MIT
#include <box2d/box2d.h>
#include <stdio.h>

static void run_case(int tuning, int substeps)
{
    const float hertz[] = {0.0f, 5.0f, 5.0f, 60.0f, 10000.0f, 5.0f, 60.0f};
    const float damping[] = {0.0f, 0.0f, 2.0f, 2.0f, 2.0f, 4.0f, 2.0f};
    b2WorldDef world_def = b2DefaultWorldDef();
    world_def.gravity = (b2Vec2){2.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_def);
    b2BodyDef body_def = b2DefaultBodyDef();
    b2BodyId ground = b2CreateBody(world, &body_def);
    body_def.type = b2_dynamicBody;
    body_def.position = (b2Vec2){2.0f, 0.0f};
    body_def.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &body_def);
    b2Body_SetMassData(body, (b2MassData){1.0f, {0.0f, 0.0f}, 1.0f});
    b2DistanceJointDef joint_def = b2DefaultDistanceJointDef();
    joint_def.bodyIdA = ground;
    joint_def.bodyIdB = body;
    joint_def.length = 1.0f;
    b2JointId joint = b2CreateDistanceJoint(world, &joint_def);
    if (tuning != 3 && tuning != 6)
    {
        b2Joint_SetConstraintTuning(joint, hertz[tuning], damping[tuning]);
    }
    for (int step = 0; step < 8; ++step)
    {
        if (tuning == 6 && step == 3)
        {
            b2Joint_SetConstraintTuning(joint, 5.0f, 4.0f);
        }
        b2World_Step(world, 1.0f / 60.0f, substeps);
        printf("distance-%d-%d-%d %.9f %.9f %.9f %.9f\n",
            tuning, substeps, step, b2DistanceJoint_GetCurrentLength(joint),
            b2Body_GetPosition(body).x, b2Body_GetLinearVelocity(body).x,
            b2Joint_GetConstraintForce(joint).x);
    }
    b2DestroyWorld(world);
}

int main(void)
{
    for (int tuning = 0; tuning < 7; ++tuning)
    {
        for (int substeps = 1; substeps <= 8; substeps *= 2)
        {
            run_case(tuning, substeps);
        }
    }
    return 0;
}
