// Differential world-query witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.

#include <box2d/box2d.h>
#include <stdbool.h>
#include <stdio.h>

typedef struct OverlapCount
{
    int count;
} OverlapCount;

typedef struct ClosestCast
{
    bool hit;
    b2Vec2 point;
    b2Vec2 normal;
    float fraction;
} ClosestCast;

static bool count_overlap(b2ShapeId shape, void* context)
{
    (void)shape;
    OverlapCount* count = context;
    count->count += 1;
    return true;
}

static float retain_closest(
    b2ShapeId shape,
    b2Vec2 point,
    b2Vec2 normal,
    float fraction,
    void* context)
{
    (void)shape;
    ClosestCast* closest = context;
    if (!closest->hit || fraction < closest->fraction)
    {
        closest->hit = true;
        closest->point = point;
        closest->normal = normal;
        closest->fraction = fraction;
    }
    return fraction;
}

int main(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.position = (b2Vec2){2.0f, 0.0f};
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    b2Polygon box = b2MakeBox(1.0f, 1.0f);
    b2ShapeId shape = b2CreatePolygonShape(body, &shape_definition, &box);
    b2QueryFilter filter = b2DefaultQueryFilter();

    OverlapCount aabb_count = {0};
    b2World_OverlapAABB(
        world,
        (b2AABB){{1.75f, -0.25f}, {2.25f, 0.25f}},
        filter,
        count_overlap,
        &aabb_count);
    printf("aabb %d\n", aabb_count.count);

    b2Vec2 circle_point = {2.0f, 0.0f};
    b2ShapeProxy circle = b2MakeProxy(&circle_point, 1, 0.25f);
    OverlapCount shape_count = {0};
    b2World_OverlapShape(world, &circle, filter, count_overlap, &shape_count);
    printf("overlap_shape %d\n", shape_count.count);

    b2RayResult ray = b2World_CastRayClosest(
        world,
        (b2Vec2){-2.0f, 0.0f},
        (b2Vec2){8.0f, 0.0f},
        filter);
    printf("ray %.9g %.9g %.9g\n", ray.fraction, ray.point.x, ray.normal.x);

    b2Vec2 moving_point = {-2.0f, 0.0f};
    b2ShapeProxy moving = b2MakeProxy(&moving_point, 1, 0.25f);
    ClosestCast cast = {0};
    b2World_CastShape(
        world,
        &moving,
        (b2Vec2){8.0f, 0.0f},
        filter,
        retain_closest,
        &cast);
    printf("shape_cast %.9g %.9g %.9g\n",
        cast.fraction, cast.point.x, cast.normal.x);

    b2AABB bounds = b2Shape_GetAABB(shape);
    b2Vec2 closest = b2Shape_GetClosestPoint(shape, (b2Vec2){4.0f, 0.0f});
    b2MassData mass = b2Shape_GetMassData(shape);
    printf("collider %d %.9g %.9g %.9g %.9g %.9g\n",
        b2Shape_TestPoint(shape, (b2Vec2){2.5f, 0.0f}) ? 1 : 0,
        closest.x,
        0.5f * (bounds.lowerBound.x + bounds.upperBound.x),
        0.5f * (bounds.upperBound.x - bounds.lowerBound.x),
        mass.mass,
        mass.rotationalInertia);

    b2DestroyWorld(world);
    return 0;
}
