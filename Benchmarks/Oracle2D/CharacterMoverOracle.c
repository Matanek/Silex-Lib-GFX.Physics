// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

enum { plane_capacity = 16 };

typedef struct PlaneCollector
{
    b2CollisionPlane planes[plane_capacity];
    int count;
} PlaneCollector;

static bool collect_plane(
    b2ShapeId shape,
    const b2PlaneResult* result,
    void* context)
{
    (void)shape;
    PlaneCollector* collector = context;
    if (result->hit && collector->count < plane_capacity)
    {
        collector->planes[collector->count] = (b2CollisionPlane){
            result->plane,
            FLT_MAX,
            0.0f,
            true,
        };
        collector->count += 1;
    }
    return true;
}

static b2WorldId create_floor_world(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.position = (b2Vec2){0.0f, -0.25f};
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon box = b2MakeBox(4.0f, 0.25f);
    b2CreatePolygonShape(body, &shape_definition, &box);
    return world;
}

static b2Capsule capsule_at(b2Vec2 position)
{
    return (b2Capsule){
        {position.x, position.y - 0.4f},
        {position.x, position.y + 0.4f},
        0.3f,
    };
}

static void print_plane_case(b2Vec2 position, const char* name)
{
    b2WorldId world = create_floor_world();
    b2Capsule capsule = capsule_at(position);
    PlaneCollector collector = {0};
    b2QueryFilter filter = b2DefaultQueryFilter();
    b2World_CollideMover(world, &capsule, filter, collect_plane, &collector);
    b2PlaneSolverResult solved = b2SolvePlanes(
        (b2Vec2){2.0f, -1.0f},
        collector.planes,
        collector.count);
    printf(
        "%s %d %.9f %.9f %.9f %.9f %.9f\n",
        name,
        collector.count,
        collector.planes[0].plane.normal.x,
        collector.planes[0].plane.normal.y,
        solved.translation.x,
        solved.translation.y,
        collector.planes[0].push);
    b2DestroyWorld(world);
}

static void print_move_case(void)
{
    b2WorldId world = create_floor_world();
    b2BodyDef wall_definition = b2DefaultBodyDef();
    wall_definition.position = (b2Vec2){2.25f, 1.0f};
    b2BodyId wall = b2CreateBody(world, &wall_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon wall_box = b2MakeBox(0.25f, 1.25f);
    b2CreatePolygonShape(wall, &shape_definition, &wall_box);

    b2Vec2 start = {0.0f, 0.7f};
    b2Vec2 position = start;
    b2Vec2 target = {4.0f, -0.3f};
    int iteration = 0;
    for (; iteration < 8; ++iteration)
    {
        b2Capsule capsule = capsule_at(position);
        PlaneCollector collector = {0};
        b2QueryFilter filter = b2DefaultQueryFilter();
        b2World_CollideMover(world, &capsule, filter, collect_plane, &collector);
        b2PlaneSolverResult solved = b2SolvePlanes(
            b2Sub(target, position),
            collector.planes,
            collector.count);
        float fraction = b2World_CastMover(
            world, &capsule, solved.translation, filter);
        b2Vec2 delta = b2MulSV(fraction, solved.translation);
        position = b2Add(position, delta);
        if (b2LengthSquared(delta) < 0.005f * 0.005f)
        {
            iteration += 1;
            break;
        }
    }
    b2Vec2 applied = b2Sub(position, start);
    printf("move %.9f %.9f 2 %d\n", applied.x, applied.y, iteration);
    b2DestroyWorld(world);
}

int main(void)
{
    print_plane_case((b2Vec2){0.0f, 0.7f}, "floor");
    print_plane_case((b2Vec2){0.0f, 0.5f}, "penetration");
    print_move_case();
    return 0;
}
