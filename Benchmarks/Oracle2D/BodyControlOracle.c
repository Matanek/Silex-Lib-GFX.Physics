// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <stdio.h>

static b2WorldId create_world(void)
{
    b2WorldDef definition = b2DefaultWorldDef();
    definition.gravity = (b2Vec2){0.0f, 0.0f};
    return b2CreateWorld(&definition);
}

static b2BodyId create_unit_box(b2WorldId world, bool fixed_rotation)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.fixedRotation = fixed_rotation;
    b2BodyId body = b2CreateBody(world, &body_definition);

    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    b2Polygon polygon = b2MakeBox(0.5f, 0.5f);
    b2CreatePolygonShape(body, &shape_definition, &polygon);
    return body;
}

static void print_mass_case(void)
{
    b2WorldId world = create_world();
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    b2Polygon first = b2MakeOffsetBox(
        1.0f,
        0.5f,
        (b2Vec2){-1.0f, 0.0f},
        b2MakeRot(0.0f));
    b2Polygon second = b2MakeOffsetBox(
        1.0f,
        0.5f,
        (b2Vec2){3.0f, 0.0f},
        b2MakeRot(0.0f));
    b2CreatePolygonShape(body, &shape_definition, &first);
    b2CreatePolygonShape(body, &shape_definition, &second);
    b2Vec2 center = b2Body_GetLocalCenterOfMass(body);
    printf(
        "mass %.9f %.9f %.9f %.9f\n",
        b2Body_GetMass(body),
        center.x,
        center.y,
        b2Body_GetRotationalInertia(body));
    b2DestroyWorld(world);
}

static void print_force_and_torque_cases(void)
{
    b2WorldId world = create_world();
    b2BodyId body = create_unit_box(world, false);
    b2Body_ApplyForceToCenter(body, (b2Vec2){4.0f, 0.0f}, true);
    b2Body_ApplyTorque(body, 1.0f, true);
    b2World_Step(world, 0.25f, 4);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf("force_torque %.9f %.9f\n", velocity.x, b2Body_GetAngularVelocity(body));
    b2DestroyWorld(world);
}

static void print_rounded_mass_case(void)
{
    b2WorldId world = create_world();
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 2.0f;
    b2Polygon polygon = b2MakeRoundedBox(1.0f, 0.5f, 0.2f);
    b2CreatePolygonShape(body, &shape_definition, &polygon);
    printf(
        "rounded_mass %.9f %.9f\n",
        b2Body_GetMass(body),
        b2Body_GetRotationalInertia(body));
    b2DestroyWorld(world);
}

static void print_impulse_case(void)
{
    b2WorldId world = create_world();
    b2BodyId body = create_unit_box(world, false);
    b2Body_ApplyLinearImpulse(
        body,
        (b2Vec2){1.0f, 0.0f},
        (b2Vec2){0.0f, 1.0f},
        true);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf("impulse %.9f %.9f\n", velocity.x, b2Body_GetAngularVelocity(body));
    b2DestroyWorld(world);
}

static void print_fixed_rotation_case(void)
{
    b2WorldId world = create_world();
    b2BodyId body = create_unit_box(world, true);
    b2Body_ApplyLinearImpulse(
        body,
        (b2Vec2){1.0f, 0.0f},
        (b2Vec2){0.0f, 1.0f},
        true);
    printf("fixed_rotation %.9f\n", b2Body_GetAngularVelocity(body));
    b2DestroyWorld(world);
}

static void print_target_case(void)
{
    b2WorldId world = create_world();
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_kinematicBody;
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon polygon = b2MakeBox(0.5f, 0.5f);
    b2CreatePolygonShape(body, &shape_definition, &polygon);

    b2Transform target = {{4.0f, -2.0f}, b2MakeRot(0.5f)};
    b2Body_SetTargetTransform(body, target, 2.0f);
    for (int step = 0; step < 8; ++step)
    {
        b2World_Step(world, 0.25f, 4);
    }
    b2Vec2 position = b2Body_GetPosition(body);
    float rotation = b2Rot_GetAngle(b2Body_GetRotation(body));
    printf("target %.9f %.9f %.9f\n", position.x, position.y, rotation);
    b2DestroyWorld(world);
}

static void print_activation_case(void)
{
    b2WorldId world = create_world();
    b2BodyDef floor_definition = b2DefaultBodyDef();
    b2BodyId floor = b2CreateBody(world, &floor_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon floor_polygon = b2MakeBox(2.0f, 0.5f);
    b2CreatePolygonShape(floor, &shape_definition, &floor_polygon);

    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){0.0f, 0.75f};
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2Polygon body_polygon = b2MakeBox(0.5f, 0.5f);
    shape_definition.density = 1.0f;
    b2CreatePolygonShape(body, &shape_definition, &body_polygon);

    b2World_Step(world, 0.0001f, 4);
    int initial_contacts = b2World_GetCounters(world).contactCount;
    b2Body_Disable(body);
    int disabled_contacts = b2World_GetCounters(world).contactCount;
    bool disabled = b2Body_IsEnabled(body);
    b2World_Step(world, 0.0001f, 4);
    b2Body_Enable(body);
    b2World_Step(world, 0.0001f, 4);
    int enabled_contacts = b2World_GetCounters(world).contactCount;
    bool enabled = b2Body_IsEnabled(body);
    printf(
        "activation %d %d %s %d %s\n",
        initial_contacts,
        disabled_contacts,
        disabled ? "true" : "false",
        enabled_contacts,
        enabled ? "true" : "false");
    b2DestroyWorld(world);
}

int main(void)
{
    print_mass_case();
    print_rounded_mass_case();
    print_force_and_torque_cases();
    print_impulse_case();
    print_fixed_rotation_case();
    print_target_case();
    print_activation_case();
    return 0;
}
