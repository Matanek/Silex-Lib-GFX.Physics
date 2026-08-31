// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <stdbool.h>
#include <stdio.h>

static float mixed_friction;
static float mixed_restitution;

static b2WorldId create_world(void)
{
    b2WorldDef definition = b2DefaultWorldDef();
    definition.gravity = (b2Vec2){0.0f, 0.0f};
    return b2CreateWorld(&definition);
}

static b2BodyId add_circle(
    b2WorldId world,
    bool fixed,
    b2Vec2 position,
    b2SurfaceMaterial material,
    bool pre_solve)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = fixed ? b2_staticBody : b2_dynamicBody;
    body_definition.position = position;
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    shape_definition.material = material;
    shape_definition.enablePreSolveEvents = pre_solve;
    b2Circle circle = {{0.0f, 0.0f}, 1.0f};
    b2CreateCircleShape(body, &shape_definition, &circle);
    return body;
}

static bool reject_tagged(b2ShapeId first, b2ShapeId second, void* context)
{
    (void)context;
    return b2Shape_GetSurfaceMaterial(first).userMaterialId != 42 &&
        b2Shape_GetSurfaceMaterial(second).userMaterialId != 42;
}

static bool disable_contact(
    b2ShapeId first,
    b2ShapeId second,
    b2Manifold* manifold,
    void* context)
{
    (void)first;
    (void)second;
    (void)manifold;
    (void)context;
    return false;
}

static bool sideways_normal(
    b2ShapeId first,
    b2ShapeId second,
    b2Manifold* manifold,
    void* context)
{
    (void)first;
    (void)second;
    (void)context;
    manifold->normal = (b2Vec2){1.0f, 0.0f};
    return true;
}

static float average_friction(float first, int first_id, float second, int second_id)
{
    (void)first_id;
    (void)second_id;
    mixed_friction = 0.5f * (first + second);
    return mixed_friction;
}

static float average_restitution(float first, int first_id, float second, int second_id)
{
    (void)first_id;
    (void)second_id;
    mixed_restitution = 0.5f * (first + second);
    return mixed_restitution;
}

static void print_filter_case(void)
{
    b2WorldId world = create_world();
    b2World_SetCustomFilterCallback(world, reject_tagged, NULL);
    b2SurfaceMaterial tagged = b2DefaultSurfaceMaterial();
    tagged.userMaterialId = 42;
    add_circle(world, true, (b2Vec2){0.0f, 0.0f}, tagged, false);
    b2BodyId body = add_circle(
        world,
        false,
        (b2Vec2){1.5f, 0.0f},
        b2DefaultSurfaceMaterial(),
        false);
    b2Body_SetLinearVelocity(body, (b2Vec2){-2.0f, 0.0f});
    b2World_Step(world, 0.25f, 4);
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf(
        "filter %d %.9f %.9f\n",
        b2World_GetCounters(world).contactCount,
        position.x,
        velocity.x);
    b2DestroyWorld(world);
}

static void print_disabled_case(void)
{
    b2WorldId world = create_world();
    b2World_SetPreSolveCallback(world, disable_contact, NULL);
    add_circle(
        world,
        true,
        (b2Vec2){0.0f, 0.0f},
        b2DefaultSurfaceMaterial(),
        true);
    b2BodyId body = add_circle(
        world,
        false,
        (b2Vec2){1.5f, 0.0f},
        b2DefaultSurfaceMaterial(),
        false);
    b2Body_SetLinearVelocity(body, (b2Vec2){-2.0f, 0.0f});
    b2World_Step(world, 0.25f, 4);
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf("disabled 0 %.9f %.9f\n", position.x, velocity.x);
    b2DestroyWorld(world);
}

static void print_material_case(void)
{
    b2WorldId world = create_world();
    mixed_friction = 0.0f;
    mixed_restitution = 0.0f;
    b2World_SetFrictionCallback(world, average_friction);
    b2World_SetRestitutionCallback(world, average_restitution);
    b2SurfaceMaterial first = b2DefaultSurfaceMaterial();
    first.friction = 0.2f;
    first.restitution = 0.2f;
    b2SurfaceMaterial second = b2DefaultSurfaceMaterial();
    second.friction = 0.8f;
    second.restitution = 0.8f;
    add_circle(world, true, (b2Vec2){0.0f, 0.0f}, first, false);
    add_circle(world, false, (b2Vec2){1.5f, 0.0f}, second, false);
    b2World_Step(world, 0.001f, 4);
    printf("materials %.9f %.9f\n", mixed_friction, mixed_restitution);
    b2DestroyWorld(world);
}

static void print_normal_case(void)
{
    b2WorldId world = create_world();
    b2World_SetPreSolveCallback(world, sideways_normal, NULL);
    add_circle(
        world,
        true,
        (b2Vec2){0.0f, 0.0f},
        b2DefaultSurfaceMaterial(),
        true);
    b2BodyId body = add_circle(
        world,
        false,
        (b2Vec2){0.0f, 1.5f},
        b2DefaultSurfaceMaterial(),
        false);
    b2Body_SetLinearVelocity(body, (b2Vec2){0.0f, -2.0f});
    b2World_Step(world, 0.1f, 4);
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf(
        "normal %.9f %.9f %.9f %.9f\n",
        position.x,
        position.y,
        velocity.x,
        velocity.y);
    b2DestroyWorld(world);
}

int main(void)
{
    print_filter_case();
    print_disabled_case();
    print_material_case();
    print_normal_case();
    return 0;
}
