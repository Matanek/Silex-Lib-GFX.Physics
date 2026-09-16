// SPDX-License-Identifier: MIT
#include <box2d/box2d.h>
#include <stdbool.h>
#include <stdio.h>

static void snapshot(const char *name, const char *phase, b2WorldId world,
                     b2BodyId body, b2ShapeId sensor)
{
    b2ContactData contacts[8];
    b2ShapeId overlaps[8];
    b2ContactEvents contact_events = b2World_GetContactEvents(world);
    b2SensorEvents sensor_events = b2World_GetSensorEvents(world);
    int count = b2Body_GetContactData(body, contacts, 8);
    int overlap_count = B2_IS_NON_NULL(sensor) ? b2Shape_GetSensorOverlaps(sensor, overlaps, 8) : 0;
    printf("%s-%s %d %d %d %d %d %d %d\n", name, phase, count, overlap_count,
        contact_events.beginCount, contact_events.endCount, contact_events.hitCount,
        sensor_events.beginCount, sensor_events.endCount);
}

static void collision_case(bool sensor)
{
    const char *name = sensor ? "sensor" : "contact";
    b2WorldDef world_def = b2DefaultWorldDef();
    world_def.gravity = b2Vec2_zero;
    b2WorldId world = b2CreateWorld(&world_def);
    b2BodyDef body_def = b2DefaultBodyDef();
    b2BodyId ground = b2CreateBody(world, &body_def);
    body_def.type = b2_dynamicBody;
    body_def.position = (b2Vec2){0.9f, 0.0f};
    body_def.linearVelocity = (b2Vec2){-5.0f, 0.0f};
    body_def.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &body_def);
    b2ShapeDef shape_def = b2DefaultShapeDef();
    shape_def.enableContactEvents = true;
    shape_def.enableHitEvents = true;
    shape_def.enableSensorEvents = true;
    shape_def.isSensor = sensor;
    b2Circle circle = {{0.0f, 0.0f}, 0.5f};
    b2ShapeId first = b2CreateCircleShape(ground, &shape_def, &circle);
    shape_def.isSensor = false;
    b2CreateCircleShape(body, &shape_def, &circle);
    b2ShapeId sensor_id = sensor ? first : b2_nullShapeId;
    snapshot(name, "created", world, body, sensor_id);
    b2World_Step(world, 0.0f, 1);
    snapshot(name, "zero", world, body, sensor_id);
    b2World_Step(world, 1.0f / 60.0f, 1);
    snapshot(name, "positive", world, body, sensor_id);
    b2World_Step(world, 0.0f, 1);
    snapshot(name, "paused", world, body, sensor_id);
    b2Body_SetTransform(body, (b2Vec2){4.0f, 0.0f}, b2Rot_identity);
    b2World_Step(world, 0.0f, 1);
    snapshot(name, "moved-zero", world, body, sensor_id);
    b2World_Step(world, 1.0f / 60.0f, 1);
    snapshot(name, "moved-positive", world, body, sensor_id);
    b2Body_SetTransform(body, (b2Vec2){0.9f, 0.0f}, b2Rot_identity);
    b2World_Step(world, 1.0f / 60.0f, 1);
    b2DestroyBody(body);
    b2World_Step(world, 0.0f, 1);
    b2ContactEvents contact_events = b2World_GetContactEvents(world);
    b2SensorEvents sensor_events = b2World_GetSensorEvents(world);
    printf("%s-destroyed-zero %d %d\n", name, contact_events.endCount, sensor_events.endCount);
    b2World_Step(world, 0.0f, 1);
    contact_events = b2World_GetContactEvents(world);
    sensor_events = b2World_GetSensorEvents(world);
    printf("%s-destroyed-twice %d %d\n", name, contact_events.endCount, sensor_events.endCount);
    b2DestroyWorld(world);
}

static void force_case(void)
{
    b2WorldDef world_def = b2DefaultWorldDef();
    world_def.gravity = b2Vec2_zero;
    b2WorldId world = b2CreateWorld(&world_def);
    b2BodyDef body_def = b2DefaultBodyDef();
    body_def.type = b2_dynamicBody;
    body_def.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &body_def);
    b2Body_SetMassData(body, (b2MassData){1.0f, {0.0f, 0.0f}, 1.0f});
    b2Body_ApplyForceToCenter(body, (b2Vec2){60.0f, 0.0f}, true);
    b2World_Step(world, 0.0f, 1);
    printf("force-zero %.9f %.9f\n", b2Body_GetPosition(body).x, b2Body_GetLinearVelocity(body).x);
    b2World_Step(world, 1.0f / 60.0f, 1);
    printf("force-positive %.9f %.9f\n", b2Body_GetPosition(body).x, b2Body_GetLinearVelocity(body).x);
    b2World_Step(world, 1.0f / 60.0f, 1);
    printf("force-next %.9f %.9f\n", b2Body_GetPosition(body).x, b2Body_GetLinearVelocity(body).x);
    b2DestroyWorld(world);
}

int main(void)
{
    collision_case(false);
    collision_case(true);
    force_case();
    return 0;
}
