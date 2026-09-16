// Differential units witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.
#include <box2d/box2d.h>
#include <assert.h>
#include <stdio.h>

static b2WorldId world(float gravity)
{
    b2WorldDef definition = b2DefaultWorldDef();
    definition.gravity = (b2Vec2){0.0f, gravity};
    definition.contactHertz = 30.0f;
    return b2CreateWorld(&definition);
}

static b2BodyId circle(b2WorldId world_id, float u, b2BodyType type,
                       b2Vec2 position, b2Vec2 velocity, float radius, bool sleep,
                       float restitution, bool hits)
{
    b2BodyDef definition = b2DefaultBodyDef();
    definition.type = type;
    definition.position = position;
    definition.linearVelocity = velocity;
    definition.enableSleep = sleep;
    b2BodyId body = b2CreateBody(world_id, &definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f / (u * u);
    shape_definition.material.restitution = restitution;
    shape_definition.enableHitEvents = hits;
    b2Circle shape = {{0.0f, 0.0f}, radius};
    b2CreateCircleShape(body, &shape_definition, &shape);
    return body;
}

static void fixed_box(b2WorldId world_id, b2Vec2 position, float half_x, float half_y)
{
    b2BodyDef definition = b2DefaultBodyDef();
    definition.position = position;
    b2BodyId body = b2CreateBody(world_id, &definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon box = b2MakeBox(half_x, half_y);
    b2CreatePolygonShape(body, &shape_definition, &box);
}

static void rest_case(const char* name, float u)
{
    b2WorldId world_id = world(-10.0f * u);
    fixed_box(world_id, (b2Vec2){0.0f, -0.5f * u}, 5.0f * u, 0.5f * u);
    b2BodyId body = circle(world_id, u, b2_dynamicBody, (b2Vec2){0.0f, 3.0f * u},
        b2Vec2_zero, 0.5f * u, true, 0.0f, false);
    for (int step = 0; step < 240; ++step) { b2World_Step(world_id, 1.0f / 60.0f, 4); }
    printf("%s_rest %.9g %.9g %d\n", name, b2Body_GetPosition(body).y / u,
        b2Body_GetLinearVelocity(body).y / u, b2Body_IsAwake(body));
    b2DestroyWorld(world_id);
}

static void casts_case(const char* name, float u)
{
    b2WorldId world_id = world(0.0f);
    fixed_box(world_id, b2Vec2_zero, 0.05f * u, u);
    b2RayResult ray = b2World_CastRayClosest(world_id, (b2Vec2){-2.0f * u, 0.0f},
        (b2Vec2){4.0f * u, 0.0f}, b2DefaultQueryFilter());
    assert(ray.hit);
    printf("%s_ray %.9g %.9g\n", name, ray.fraction, ray.point.x / u);
    b2Polygon box = b2MakeBox(0.05f * u, u);
    b2Vec2 center = b2Vec2_zero;
    b2ShapeCastPairInput input = {
        .proxyA = b2MakeProxy(box.vertices, box.count, box.radius),
        .proxyB = b2MakeProxy(&center, 1, 0.1f * u),
        .transformA = b2Transform_identity,
        .transformB = {{-2.0f * u, 0.0f}, b2Rot_identity},
        .translationB = {4.0f * u, 0.0f}, .maxFraction = 1.0f,
    };
    b2CastOutput cast = b2ShapeCast(&input);
    assert(cast.hit);
    printf("%s_cast %.9g %.9g\n", name, cast.fraction, cast.point.x / u);
    b2BodyId body = circle(world_id, u, b2_dynamicBody, (b2Vec2){-2.0f * u, 0.0f},
        (b2Vec2){300.0f * u, 0.0f}, 0.1f * u, false, 0.0f, false);
    b2World_Step(world_id, 1.0f / 60.0f, 4);
    printf("%s_ccd %.9g %.9g\n", name, b2Body_GetPosition(body).x / u,
        b2Body_GetLinearVelocity(body).x / u);
    b2DestroyWorld(world_id);
}

static void threshold_case(const char* name, const char* label, float u, float speed)
{
    b2WorldId world_id = world(0.0f);
    circle(world_id, u, b2_staticBody, b2Vec2_zero, b2Vec2_zero, 0.5f * u, true, 1.0f, false);
    b2BodyId body = circle(world_id, u, b2_dynamicBody, (b2Vec2){u, 0.0f},
        (b2Vec2){-speed * u, 0.0f}, 0.5f * u, false, 1.0f, true);
    b2World_Step(world_id, 1.0f / 60.0f, 4);
    printf("%s_%s %.9g %d\n", name, label, b2Body_GetLinearVelocity(body).x / u,
        b2World_GetContactEvents(world_id).hitCount);
    b2DestroyWorld(world_id);
}

static void sleep_case(const char* name, const char* label, float u, float speed)
{
    b2WorldId world_id = world(0.0f);
    b2BodyId body = circle(world_id, u, b2_dynamicBody, b2Vec2_zero,
        (b2Vec2){speed * u, 0.0f}, 0.5f * u, true, 0.0f, false);
    for (int step = 0; step < 90; ++step) { b2World_Step(world_id, 1.0f / 60.0f, 4); }
    printf("%s_sleep_%s %d\n", name, label, b2Body_IsAwake(body));
    b2DestroyWorld(world_id);
}

static void scale_case(const char* name, float u)
{
    b2SetLengthUnitsPerMeter(u);
    rest_case(name, u);
    casts_case(name, u);
    threshold_case(name, "low", u, 0.5f);
    threshold_case(name, "high", u, 2.0f);
    sleep_case(name, "low", u, 0.04f);
    sleep_case(name, "high", u, 0.06f);
    b2WorldId world_id = world(0.0f);
    b2BodyId body = circle(world_id, u, b2_dynamicBody, b2Vec2_zero,
        (b2Vec2){500.0f * u, 0.0f}, 0.5f * u, true, 0.0f, false);
    b2World_Step(world_id, 1.0f / 60.0f, 4);
    b2WorldDef defaults = b2DefaultWorldDef();
    b2BodyDef body_defaults = b2DefaultBodyDef();
    printf("%s_limits %.9g %.9g %.9g %.9g %.9g\n", name,
        b2Body_GetLinearVelocity(body).x / u, defaults.restitutionThreshold / u,
        defaults.hitEventThreshold / u, defaults.maxContactPushSpeed / u, body_defaults.sleepThreshold / u);
    b2DestroyWorld(world_id);
}

int main(void)
{
    scale_case("meter", 1.0f);
    scale_case("centimeter", 100.0f);
    b2SetLengthUnitsPerMeter(1.0f);
    return 0;
}
