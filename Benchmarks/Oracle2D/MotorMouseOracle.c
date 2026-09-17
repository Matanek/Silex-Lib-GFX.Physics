// Differential witness against Box2D 3.1.1, commit 8c661469.
#include <box2d/box2d.h>
#include "WorkerOptions.h"
#include <math.h>
#include <stdio.h>

static void record(b2BodyId first, b2BodyId second, b2JointId joint,
    int family, int geometry, int variant, int substeps, int step)
{
    b2Vec2 a = b2Body_GetPosition(first), b = b2Body_GetPosition(second);
    b2Vec2 va = b2Body_GetLinearVelocity(first), vb = b2Body_GetLinearVelocity(second);
    b2Vec2 force = b2Joint_GetConstraintForce(joint);
    printf("target_%d_%d_%d_%d_%d %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n",
        family, geometry, variant, substeps, step,
        a.x, a.y, b2Rot_GetAngle(b2Body_GetRotation(first)), va.x, va.y, b2Body_GetAngularVelocity(first),
        b.x, b.y, b2Rot_GetAngle(b2Body_GetRotation(second)), vb.x, vb.y, b2Body_GetAngularVelocity(second),
        force.x, force.y, b2Joint_GetConstraintTorque(joint));
}

static void scenario(OracleTaskSystem* tasks, int family, int geometry, int variant, int substeps)
{
    b2WorldDef wd = b2DefaultWorldDef();
    wd.gravity = (b2Vec2){2, -3};
    oracle_tasks_configure(tasks, &wd);
    b2WorldId world = b2CreateWorld(&wd);
    b2World_EnableWarmStarting(world, variant != 6);
    b2BodyDef bd = b2DefaultBodyDef();
    bd.enableSleep = false;
    bool mobile = family == 0 && geometry == 2;
    if (mobile) bd.type = b2_dynamicBody;
    b2BodyId first = b2CreateBody(world, &bd);
    if (mobile)
    {
        b2Body_SetMassData(first, (b2MassData){.mass = 1, .rotationalInertia = 1});
        b2Body_SetLinearVelocity(first, (b2Vec2){.1f, -.2f});
        b2Body_SetAngularVelocity(first, .3f);
    }
    bd.type = b2_dynamicBody;
    bd.fixedRotation = variant == 7;
    b2BodyId second = b2CreateBody(world, &bd);
    float inertia = variant == 7 ? 0 : 3;
    b2Vec2 center = family == 1 && geometry == 2 ? (b2Vec2){.15f, -.1f} : b2Vec2_zero;
    b2Body_SetMassData(second, (b2MassData){.mass = 2, .center = center,
        .rotationalInertia = inertia});
    b2Vec2 anchor = geometry > 0 ? (b2Vec2){.2f, .3f} : b2Vec2_zero;
    float max_force = 1000, max_torque = 1000, correction = .3f, hertz = 5, damping = .7f;
    if (variant == 0) { max_force = 1; max_torque = 1; }
    if (variant == 2) { max_force = 0; max_torque = 0; }
    if (variant == 3) { correction = 0; hertz = 0; }
    if (variant == 4) { correction = 1; hertz = 12; damping = 0; max_force = 20; max_torque = 5; }
    b2JointId joint;
    if (family == 0)
    {
        b2MotorJointDef jd = b2DefaultMotorJointDef();
        jd.bodyIdA = first; jd.bodyIdB = second;
        jd.linearOffset = (b2Vec2){.1f, -.2f}; jd.angularOffset = -.1f;
        jd.maxForce = max_force; jd.maxTorque = max_torque; jd.correctionFactor = correction;
        joint = b2CreateMotorJoint(world, &jd);
        b2Joint_SetLocalAnchorA(joint, anchor);
        b2Joint_SetLocalAnchorB(joint, b2MulSV(-.5f, anchor));
    }
    else
    {
        b2MouseJointDef jd = b2DefaultMouseJointDef();
        jd.bodyIdA = first; jd.bodyIdB = second;
        jd.target = anchor; jd.hertz = hertz; jd.dampingRatio = damping; jd.maxForce = max_force;
        joint = b2CreateMouseJoint(world, &jd);
    }
    b2Body_SetTransform(second, (b2Vec2){.7f, .9f}, (b2Rot){cosf(.25f), sinf(.25f)});
    b2Body_SetLinearVelocity(second, (b2Vec2){-.2f, .4f});
    if (variant != 7) b2Body_SetAngularVelocity(second, .7f);
    for (int step = 0; step < 8; ++step)
    {
        if (variant == 5 && step == 3)
        {
            if (family == 0)
            {
                b2MotorJoint_SetLinearOffset(joint, (b2Vec2){-.3f, .4f});
                b2MotorJoint_SetAngularOffset(joint, .15f);
                b2MotorJoint_SetMaxForce(joint, 20);
                b2MotorJoint_SetMaxTorque(joint, 5);
                b2MotorJoint_SetCorrectionFactor(joint, .6f);
            }
            else
            {
                b2MouseJoint_SetTarget(joint, (b2Vec2){.8f, -.2f});
                b2MouseJoint_SetSpringHertz(joint, 8);
                b2MouseJoint_SetSpringDampingRatio(joint, 1.2f);
                b2MouseJoint_SetMaxForce(joint, 20);
            }
        }
        b2World_Step(world, 1.f / 60, substeps);
        record(first, second, joint, family, geometry, variant, substeps, step);
    }
    b2DestroyWorld(world);
}

int main(int argc, char** argv)
{
    OracleWorkers workers;
    if (!oracle_workers_open(&workers, argc, argv)) return 2;
    for (int family = 0; family < 2; ++family)
        for (int geometry = 0; geometry < 3; ++geometry)
            for (int variant = 0; variant < 8; ++variant)
                for (int substeps = 1; substeps <= 8; substeps *= 2)
                    scenario(workers.tasks, family, geometry, variant, substeps);
    return oracle_workers_close(&workers);
}
