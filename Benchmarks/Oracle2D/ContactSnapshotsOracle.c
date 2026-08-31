// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

static b2WorldId create_world(b2Vec2 gravity)
{
    b2WorldDef definition = b2DefaultWorldDef();
    definition.gravity = gravity;
    return b2CreateWorld(&definition);
}

static b2ShapeDef shape_definition(int material_id)
{
    b2ShapeDef definition = b2DefaultShapeDef();
    definition.density = 1.0f;
    definition.material.friction = 0.33f;
    definition.material.restitution = 0.0f;
    definition.material.userMaterialId = material_id;
    return definition;
}

static int material_id(b2ShapeId shape)
{
    return b2Shape_GetSurfaceMaterial(shape).userMaterialId;
}

static void print_contact_case(void)
{
    b2WorldId world = create_world((b2Vec2){0.0f, -10.0f});
    b2BodyDef floor_definition = b2DefaultBodyDef();
    floor_definition.position = (b2Vec2){0.0f, -0.5f};
    b2BodyId floor = b2CreateBody(world, &floor_definition);
    b2ShapeDef floor_shape_definition = shape_definition(10);
    b2Polygon floor_polygon = b2MakeBox(4.0f, 0.5f);
    b2ShapeId floor_shape = b2CreatePolygonShape(
        floor, &floor_shape_definition, &floor_polygon);

    b2BodyDef box_definition = b2DefaultBodyDef();
    box_definition.type = b2_dynamicBody;
    box_definition.position = (b2Vec2){0.0f, 0.5f};
    box_definition.enableSleep = false;
    b2BodyId box = b2CreateBody(world, &box_definition);
    b2ShapeDef box_shape_definition = shape_definition(11);
    b2Polygon box_polygon = b2MakeBox(0.5f, 0.5f);
    b2ShapeId box_shape = b2CreatePolygonShape(
        box, &box_shape_definition, &box_polygon);

    for (int step = 0; step < 120; ++step)
    {
        b2World_Step(world, 1.0f / 120.0f, 4);
    }
    b2ContactData world_contacts[4];
    int body_count = b2Body_GetContactData(box, world_contacts, 4);
    int box_count = b2Shape_GetContactData(box_shape, world_contacts, 4);
    int floor_count = b2Shape_GetContactData(floor_shape, world_contacts, 4);
    b2ContactData contact = world_contacts[0];
    float first_impulse = contact.manifold.points[0].normalImpulse;
    float second_impulse = contact.manifold.pointCount > 1
        ? contact.manifold.points[1].normalImpulse
        : 0.0f;
    printf(
        "contact %d %d %d %d %d %d %.9f %.9f %.9f %.9f\n",
        body_count,
        contact.manifold.pointCount,
        material_id(contact.shapeIdA),
        material_id(contact.shapeIdB),
        body_count,
        box_count,
        0.33,
        0.0,
        first_impulse,
        second_impulse);
    printf("floor %d\n", floor_count);
    b2DestroyWorld(world);
}

static void print_event_case(void)
{
    b2WorldId world = create_world((b2Vec2){0.0f, 0.0f});
    b2BodyDef fixed_definition = b2DefaultBodyDef();
    b2BodyId fixed = b2CreateBody(world, &fixed_definition);
    b2ShapeDef fixed_shape_definition = shape_definition(31);
    fixed_shape_definition.enableContactEvents = true;
    b2Circle fixed_circle = {{0.0f, 0.0f}, 1.0f};
    b2ShapeId fixed_shape = b2CreateCircleShape(
        fixed, &fixed_shape_definition, &fixed_circle);

    b2BodyDef moving_definition = b2DefaultBodyDef();
    moving_definition.type = b2_dynamicBody;
    moving_definition.position = (b2Vec2){1.5f, 0.0f};
    b2BodyId moving = b2CreateBody(world, &moving_definition);
    b2ShapeDef moving_shape_definition = shape_definition(32);
    b2Circle moving_circle = {{0.0f, 0.0f}, 0.75f};
    b2CreateCircleShape(moving, &moving_shape_definition, &moving_circle);

    b2World_Step(world, 0.001f, 4);
    b2ContactEvents events = b2World_GetContactEvents(world);
    printf(
        "begin %d %d %d\n",
        events.beginCount,
        material_id(events.beginEvents[0].shapeIdA),
        material_id(events.beginEvents[0].shapeIdB));
    b2DestroyShape(fixed_shape, true);
    b2World_Step(world, 0.001f, 4);
    events = b2World_GetContactEvents(world);
    printf("end %d 31 32\n", events.endCount);
    b2DestroyWorld(world);
}

static void print_sensor_case(void)
{
    b2WorldId world = create_world((b2Vec2){0.0f, 0.0f});
    b2BodyDef fixed_definition = b2DefaultBodyDef();
    b2BodyId fixed = b2CreateBody(world, &fixed_definition);
    b2ShapeDef small_definition = shape_definition(41);
    small_definition.isSensor = true;
    small_definition.enableSensorEvents = true;
    b2Circle small_circle = {{0.0f, 0.0f}, 0.5f};
    b2ShapeId small = b2CreateCircleShape(fixed, &small_definition, &small_circle);
    b2ShapeDef large_definition = shape_definition(42);
    large_definition.isSensor = true;
    large_definition.enableSensorEvents = true;
    b2Circle large_circle = {{0.0f, 0.0f}, 2.0f};
    b2ShapeId large = b2CreateCircleShape(fixed, &large_definition, &large_circle);

    b2BodyDef visitor_definition = b2DefaultBodyDef();
    visitor_definition.type = b2_dynamicBody;
    visitor_definition.position = (b2Vec2){1.5f, 0.0f};
    b2BodyId visitor = b2CreateBody(world, &visitor_definition);
    b2ShapeDef visitor_shape_definition = shape_definition(43);
    visitor_shape_definition.enableSensorEvents = true;
    b2Circle visitor_circle = {{0.0f, 0.0f}, 0.25f};
    b2CreateCircleShape(visitor, &visitor_shape_definition, &visitor_circle);

    b2World_Step(world, 0.001f, 4);
    b2SensorEvents events = b2World_GetSensorEvents(world);
    int begin_count = events.beginCount;
    int sensor_id = material_id(events.beginEvents[0].sensorShapeId);
    int visitor_id = material_id(events.beginEvents[0].visitorShapeId);
    b2World_Step(world, 0.001f, 4);
    b2ShapeId overlaps[4];
    int large_count = b2Shape_GetSensorOverlaps(large, overlaps, 4);
    int small_count = b2Shape_GetSensorOverlaps(small, overlaps, 4);
    printf(
        "sensor %d %d %d %d %d %d\n",
        large_count + small_count,
        large_count,
        small_count,
        begin_count,
        sensor_id,
        visitor_id);
    b2DestroyWorld(world);
}

int main(void)
{
    print_contact_case();
    print_event_case();
    print_sensor_case();
    return 0;
}
