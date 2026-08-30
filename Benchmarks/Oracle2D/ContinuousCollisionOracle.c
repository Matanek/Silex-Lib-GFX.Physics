// Differential continuous-collision witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.

#include <box2d/box2d.h>
#include <stdio.h>

typedef enum ShapeKind
{
    shape_circle,
    shape_capsule,
    shape_segment,
    shape_polygon,
} ShapeKind;

static void create_shape(b2BodyId body, ShapeKind kind)
{
    b2ShapeDef definition = b2DefaultShapeDef();
    definition.density = 1.0f;
    switch (kind)
    {
        case shape_circle:
        {
            b2Circle shape = {{0.0f, 0.0f}, 0.1f};
            b2CreateCircleShape(body, &definition, &shape);
            break;
        }
        case shape_capsule:
        {
            b2Capsule shape = {{-0.2f, 0.0f}, {0.2f, 0.0f}, 0.1f};
            b2CreateCapsuleShape(body, &definition, &shape);
            break;
        }
        case shape_segment:
        {
            b2Segment shape = {{0.0f, -0.2f}, {0.0f, 0.2f}};
            b2CreateSegmentShape(body, &definition, &shape);
            b2MassData mass = {
                .mass = 1.0f,
                .center = {0.0f, 0.0f},
                .rotationalInertia = 1.0f / 75.0f,
            };
            b2Body_SetMassData(body, mass);
            break;
        }
        case shape_polygon:
        {
            b2Polygon shape = b2MakeRoundedBox(0.15f, 0.15f, 0.03f);
            b2CreatePolygonShape(body, &definition, &shape);
            break;
        }
    }
}

static b2BodyId create_wall(
    b2WorldId world, b2BodyType type, float position, float velocity)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = type;
    body_definition.position = (b2Vec2){position, 0.0f};
    body_definition.linearVelocity = (b2Vec2){velocity, 0.0f};
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    b2Polygon wall = b2MakeBox(0.05f, 1.0f);
    b2CreatePolygonShape(body, &shape_definition, &wall);
    return body;
}

static b2BodyId create_circle(
    b2WorldId world, float position, float velocity, bool bullet)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){position, 0.0f};
    body_definition.linearVelocity = (b2Vec2){velocity, 0.0f};
    body_definition.enableSleep = false;
    body_definition.isBullet = bullet;
    b2BodyId body = b2CreateBody(world, &body_definition);
    create_shape(body, shape_circle);
    return body;
}

static void fixed_target_case(const char* name, ShapeKind kind)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    create_wall(world, b2_staticBody, 0.0f, 0.0f);

    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){-2.0f, 0.0f};
    body_definition.linearVelocity = (b2Vec2){300.0f, 0.0f};
    body_definition.enableSleep = false;
    b2BodyId mover = b2CreateBody(world, &body_definition);
    create_shape(mover, kind);

    b2World_Step(world, 1.0f / 60.0f, 4);
    printf("%s %.9g %.9g 0 0\n", name,
        b2Body_GetPosition(mover).x, b2Body_GetLinearVelocity(mover).x);
    b2DestroyWorld(world);
}

static void kinematic_target_case(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyId target = create_wall(world, b2_kinematicBody, -2.0f, 300.0f);
    b2BodyId mover = create_circle(world, 0.0f, 0.0f, false);

    b2World_Step(world, 1.0f / 60.0f, 4);
    printf("kinematic_target %.9g %.9g %.9g %.9g\n",
        b2Body_GetPosition(mover).x, b2Body_GetLinearVelocity(mover).x,
        b2Body_GetPosition(target).x, b2Body_GetLinearVelocity(target).x);
    b2DestroyWorld(world);
}

static void dynamic_bullet_case(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyId bullet = create_circle(world, -2.0f, 300.0f, true);
    b2BodyId target = create_circle(world, 0.0f, 0.0f, false);

    b2World_Step(world, 1.0f / 60.0f, 4);
    printf("dynamic_bullet %.9g %.9g %.9g %.9g\n",
        b2Body_GetPosition(bullet).x, b2Body_GetLinearVelocity(bullet).x,
        b2Body_GetPosition(target).x, b2Body_GetLinearVelocity(target).x);
    b2DestroyWorld(world);
}

int main(void)
{
    fixed_target_case("fixed_circle", shape_circle);
    fixed_target_case("fixed_capsule", shape_capsule);
    fixed_target_case("fixed_segment", shape_segment);
    fixed_target_case("fixed_polygon", shape_polygon);
    kinematic_target_case();
    dynamic_bullet_case();
    return 0;
}
