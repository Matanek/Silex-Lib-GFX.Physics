#include <box2d/box2d.h>
#include <assert.h>
#include <stdio.h>

static b2ShapeId shapes[3];
static int mask(b2ShapeId a, b2ShapeId b)
{
    for (int i = 0; i < 3; ++i) {
        if (B2_ID_EQUALS(a, shapes[i]) || B2_ID_EQUALS(b, shapes[i])) return 1 << i;
    }
    assert(false);
    return 0;
}
static void record(b2WorldId world, int stage, int count)
{
    b2ContactEvents e = b2World_GetContactEvents(world);
    int began = 0, ended = 0, hit = 0;
    for (int i = 0; i < e.beginCount; ++i) began += mask(e.beginEvents[i].shapeIdA, e.beginEvents[i].shapeIdB);
    for (int i = 0; i < e.endCount; ++i) ended += mask(e.endEvents[i].shapeIdA, e.endEvents[i].shapeIdB);
    for (int i = 0; i < e.hitCount; ++i) {
        hit += mask(e.hitEvents[i].shapeIdA, e.hitEvents[i].shapeIdB);
        assert(e.hitEvents[i].approachSpeed > 4.9f);
    }
    int contacts = 0, hits = 0, sensors = 0;
    for (int i = 0; i < count; ++i) {
        if (b2Shape_AreContactEventsEnabled(shapes[i])) contacts += 1 << i;
        if (b2Shape_AreHitEventsEnabled(shapes[i])) hits += 1 << i;
        if (b2Shape_AreSensorEventsEnabled(shapes[i])) sensors += 1 << i;
    }
    printf("stage_%d %d %d %d %d %d %d %d %d %d\n", stage, e.beginCount, began,
        e.endCount, ended, e.hitCount, hit, contacts, hits, sensors);
}
static b2ShapeId collider(b2BodyId body, float x, bool events, bool sensors)
{
    b2ShapeDef def = b2DefaultShapeDef();
    def.enableContactEvents = events;
    def.enableHitEvents = false;
    def.enableSensorEvents = sensors;
    b2Polygon box = b2MakeOffsetBox(.5f, .5f, (b2Vec2){x, 0}, b2Rot_identity);
    return b2CreatePolygonShape(body, &def, &box);
}
int main(void)
{
    b2WorldDef w = b2DefaultWorldDef();
    w.gravity = b2Vec2_zero;
    w.hitEventThreshold = 1;
    b2WorldId world = b2CreateWorld(&w);
    b2BodyDef fixed_def = b2DefaultBodyDef();
    b2BodyId fixed = b2CreateBody(world, &fixed_def);
    shapes[0] = collider(fixed, -2, true, true);
    shapes[1] = collider(fixed, 2, false, false);
    b2BodyId visitors[2];
    for (int i = 0; i < 2; ++i) {
        b2BodyDef bd = b2DefaultBodyDef();
        bd.type = b2_dynamicBody;
        bd.enableSleep = false;
        bd.position = (b2Vec2){-2.0f + 4.0f*i, .9f};
        visitors[i] = b2CreateBody(world, &bd);
        b2ShapeDef sd = b2DefaultShapeDef();
        sd.enableContactEvents = false;
        sd.enableHitEvents = false;
        b2Circle circle = {b2Vec2_zero, .5f};
        b2CreateCircleShape(visitors[i], &sd, &circle);
    }
    for (int stage = 0; stage < 10; ++stage) {
        if (stage == 1 || stage == 4 || stage == 8) b2Body_EnableContactEvents(fixed, true);
        if (stage == 2) b2Body_EnableContactEvents(fixed, false);
        if (stage == 5) b2Shape_EnableContactEvents(shapes[0], false);
        if (stage == 6) b2Body_EnableHitEvents(fixed, true);
        if (stage == 7) b2Body_EnableHitEvents(fixed, false);
        if (stage == 3 || stage == 4 || stage == 6 || stage == 7 || stage == 9) {
            for (int i = 0; i < 2; ++i) {
                float y = stage == 3 || stage == 9 ? 3 : .9f;
                b2Body_SetTransform(visitors[i], (b2Vec2){-2.0f + 4.0f*i, y}, b2Rot_identity);
                b2Body_SetLinearVelocity(visitors[i], (b2Vec2){0, stage == 6 || stage == 7 ? -5 : 0});
            }
        }
        if (stage == 8) shapes[2] = collider(fixed, 6, false, false);
        b2World_Step(world, .001f, 4);
        record(world, stage, stage < 8 ? 2 : 3);
    }
    b2DestroyWorld(world);
}
