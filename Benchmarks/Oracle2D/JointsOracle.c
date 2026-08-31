// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <stdbool.h>
#include <stdio.h>

static b2WorldId create_world(float gravity_y)
{
    b2WorldDef definition = b2DefaultWorldDef();
    definition.gravity = (b2Vec2){0.0f, gravity_y};
    return b2CreateWorld(&definition);
}

static b2BodyId add_body(b2WorldId world, bool fixed, b2Vec2 position)
{
    b2BodyDef definition = b2DefaultBodyDef();
    definition.type = fixed ? b2_staticBody : b2_dynamicBody;
    definition.position = position;
    definition.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    b2Circle circle = {{0.0f, 0.0f}, 1.0f};
    b2CreateCircleShape(body, &shape_definition, &circle);
    return body;
}

static void run_steps(b2WorldId world, int count)
{
    for (int step = 0; step < count; ++step)
    {
        b2World_Step(world, 1.0f / 120.0f, 4);
    }
}

static void distance_case(void)
{
    b2WorldId world = create_world(0.0f);
    b2BodyId ground = add_body(world, true, (b2Vec2){0.0f, 0.0f});
    b2BodyId body = add_body(world, false, (b2Vec2){2.0f, 0.0f});
    b2DistanceJointDef definition = b2DefaultDistanceJointDef();
    definition.bodyIdA = ground;
    definition.bodyIdB = body;
    definition.length = 2.0f;
    b2JointId joint = b2CreateDistanceJoint(world, &definition);
    b2DistanceJoint_SetLength(joint, 1.2f);
    b2DistanceJoint_EnableSpring(joint, true);
    b2DistanceJoint_SetSpringHertz(joint, 6.0f);
    b2DistanceJoint_SetSpringDampingRatio(joint, 1.0f);
    b2DistanceJoint_EnableLimit(joint, true);
    b2DistanceJoint_SetLengthRange(joint, 0.8f, 2.0f);
    run_steps(world, 180);
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    b2Vec2 force = b2Joint_GetConstraintForce(joint);
    printf("distance %.9f %.9f %.9f %.9f\n",
        b2DistanceJoint_GetCurrentLength(joint), position.x, velocity.x, force.x);
    b2DestroyWorld(world);
}

static void prismatic_case(void)
{
    b2WorldId world = create_world(0.0f);
    b2BodyId ground = add_body(world, true, (b2Vec2){0.0f, 0.0f});
    b2BodyId body = add_body(world, false, (b2Vec2){0.0f, 0.0f});
    b2PrismaticJointDef definition = b2DefaultPrismaticJointDef();
    definition.bodyIdA = ground;
    definition.bodyIdB = body;
    definition.localAxisA = (b2Vec2){1.0f, 0.0f};
    b2JointId joint = b2CreatePrismaticJoint(world, &definition);
    b2PrismaticJoint_SetLimits(joint, -0.5f, 0.5f);
    b2PrismaticJoint_EnableLimit(joint, true);
    b2PrismaticJoint_EnableSpring(joint, false);
    b2PrismaticJoint_SetMotorSpeed(joint, 2.0f);
    b2PrismaticJoint_SetMaxMotorForce(joint, 40.0f);
    b2PrismaticJoint_EnableMotor(joint, true);
    run_steps(world, 120);
    b2Vec2 position = b2Body_GetPosition(body);
    printf("prismatic %.9f %.9f %.9f %.9f\n",
        b2PrismaticJoint_GetTranslation(joint),
        b2PrismaticJoint_GetSpeed(joint),
        b2PrismaticJoint_GetMotorForce(joint),
        position.x);
    b2DestroyWorld(world);
}

static void revolute_case(void)
{
    b2WorldId world = create_world(0.0f);
    b2BodyId ground = add_body(world, true, (b2Vec2){0.0f, 0.0f});
    b2BodyId body = add_body(world, false, (b2Vec2){1.0f, 0.0f});
    b2RevoluteJointDef definition = b2DefaultRevoluteJointDef();
    definition.bodyIdA = ground;
    definition.bodyIdB = body;
    definition.localAnchorB = (b2Vec2){-1.0f, 0.0f};
    b2JointId joint = b2CreateRevoluteJoint(world, &definition);
    b2RevoluteJoint_SetLimits(joint, -0.4f, 0.4f);
    b2RevoluteJoint_EnableLimit(joint, true);
    b2RevoluteJoint_SetMotorSpeed(joint, 1.0f);
    b2RevoluteJoint_SetMaxMotorTorque(joint, 20.0f);
    b2RevoluteJoint_EnableMotor(joint, true);
    run_steps(world, 120);
    b2Vec2 position = b2Body_GetPosition(body);
    printf("revolute %.9f %.9f %.9f %.9f\n",
        b2RevoluteJoint_GetAngle(joint),
        b2Body_GetAngularVelocity(body),
        b2RevoluteJoint_GetMotorTorque(joint),
        b2Length(position));
    b2DestroyWorld(world);
}

static void wheel_case(void)
{
    b2WorldId world = create_world(-10.0f);
    b2BodyId ground = add_body(world, true, (b2Vec2){0.0f, 0.0f});
    b2BodyId body = add_body(world, false, (b2Vec2){0.0f, 0.5f});
    b2WheelJointDef definition = b2DefaultWheelJointDef();
    definition.bodyIdA = ground;
    definition.bodyIdB = body;
    definition.localAnchorB = (b2Vec2){0.0f, 0.0f};
    definition.localAnchorA = (b2Vec2){0.0f, 0.5f};
    definition.localAxisA = (b2Vec2){0.0f, 1.0f};
    b2JointId joint = b2CreateWheelJoint(world, &definition);
    b2WheelJoint_SetLimits(joint, -0.5f, 0.5f);
    b2WheelJoint_EnableLimit(joint, true);
    b2WheelJoint_EnableSpring(joint, true);
    b2WheelJoint_SetSpringHertz(joint, 5.0f);
    b2WheelJoint_SetSpringDampingRatio(joint, 1.0f);
    b2WheelJoint_SetMotorSpeed(joint, 3.0f);
    b2WheelJoint_SetMaxMotorTorque(joint, 20.0f);
    b2WheelJoint_EnableMotor(joint, true);
    run_steps(world, 180);
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf("wheel %.9f %.9f %.9f %.9f\n",
        position.y - 0.5f,
        velocity.y,
        b2Body_GetAngularVelocity(body),
        b2WheelJoint_GetMotorTorque(joint));
    b2DestroyWorld(world);
}

int main(void)
{
    distance_case();
    prismatic_case();
    revolute_case();
    wheel_case();
    return 0;
}
