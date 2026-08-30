// Differential dynamic-shape witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.

#include <box2d/box2d.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum ShapeKind
{
    shape_circle,
    shape_capsule,
    shape_segment,
    shape_polygon,
} ShapeKind;

static void create_dynamic_shape(b2BodyId body, ShapeKind kind)
{
    b2ShapeDef definition = b2DefaultShapeDef();
    definition.density = 1.0f;
    switch (kind)
    {
        case shape_circle:
        {
            b2Circle shape = {{0.0f, 0.0f}, 0.5f};
            b2CreateCircleShape(body, &definition, &shape);
            break;
        }
        case shape_capsule:
        {
            b2Capsule shape = {{-0.5f, 0.0f}, {0.5f, 0.0f}, 0.25f};
            b2CreateCapsuleShape(body, &definition, &shape);
            break;
        }
        case shape_segment:
        {
            b2Segment shape = {{-0.5f, 0.0f}, {0.5f, 0.0f}};
            b2CreateSegmentShape(body, &definition, &shape);
            // Segments are massless in Box2D. Assign the same finite fallback
            // mass used by World2D so their supported polygon contact can be
            // compared dynamically.
            b2MassData mass = {
                .mass = 1.0f,
                .center = {0.0f, 0.0f},
                .rotationalInertia = 1.0f / 12.0f,
            };
            b2Body_SetMassData(body, mass);
            break;
        }
        case shape_polygon:
        {
            b2Polygon shape = b2MakeRoundedBox(0.5f, 0.5f, 0.1f);
            b2CreatePolygonShape(body, &definition, &shape);
            break;
        }
    }
}

static void create_support(b2WorldId world, bool chain)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    b2BodyId body = b2CreateBody(world, &body_definition);
    if (chain)
    {
        b2Vec2 points[] = {
            {5.0f, 0.0f}, {2.0f, 0.0f}, {-2.0f, 0.0f}, {-5.0f, 0.0f},
        };
        b2SurfaceMaterial material = b2DefaultSurfaceMaterial();
        b2ChainDef definition = b2DefaultChainDef();
        definition.points = points;
        definition.count = 4;
        definition.materials = &material;
        definition.materialCount = 1;
        b2CreateChain(body, &definition);
    }
    else
    {
        b2ShapeDef definition = b2DefaultShapeDef();
        b2Polygon floor = b2MakeOffsetBox(
            5.0f, 0.5f, (b2Vec2){0.0f, -0.5f}, b2Rot_identity);
        b2CreatePolygonShape(body, &definition, &floor);
    }
}

static void print_case(const char* name, ShapeKind kind, bool chain)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    b2WorldId world = b2CreateWorld(&world_definition);
    create_support(world, chain);

    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){0.0f, 3.0f};
    body_definition.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &body_definition);
    create_dynamic_shape(body, kind);

    for (int step = 0; step < 240; ++step)
    {
        b2World_Step(world, 1.0f / 60.0f, 4);
    }

    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf(
        "%s %.9g %.9g %.9g %.9g %.9g %.9g\n",
        name,
        position.x,
        position.y,
        velocity.x,
        velocity.y,
        b2Rot_GetAngle(b2Body_GetRotation(body)),
        b2Body_GetAngularVelocity(body));
    b2DestroyWorld(world);
}

static void print_chain_transition(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyDef support_definition = b2DefaultBodyDef();
    b2BodyId support = b2CreateBody(world, &support_definition);
    b2Vec2 points[] = {
        {5.0f, 0.0f}, {4.0f, 0.0f}, {2.0f, 0.0f}, {0.0f, 0.5f},
        {-2.0f, 0.5f}, {-4.0f, 0.0f}, {-5.0f, 0.0f},
    };
    b2SurfaceMaterial material = b2DefaultSurfaceMaterial();
    material.friction = 0.0f;
    b2ChainDef chain_definition = b2DefaultChainDef();
    chain_definition.points = points;
    chain_definition.count = 7;
    chain_definition.materials = &material;
    chain_definition.materialCount = 1;
    b2CreateChain(support, &chain_definition);

    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){3.5f, 0.3f};
    body_definition.linearVelocity = (b2Vec2){-5.0f, 0.0f};
    body_definition.enableSleep = false;
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    shape_definition.material.friction = 0.0f;
    b2Circle circle = {{0.0f, 0.0f}, 0.25f};
    b2CreateCircleShape(body, &shape_definition, &circle);
    for (int step = 0; step < 120; ++step)
    {
        b2World_Step(world, 1.0f / 120.0f, 4);
    }
    b2Vec2 position = b2Body_GetPosition(body);
    b2Vec2 velocity = b2Body_GetLinearVelocity(body);
    printf(
        "chain_transition %.9g %.9g %.9g %.9g %.9g %.9g\n",
        position.x,
        position.y,
        velocity.x,
        velocity.y,
        b2Rot_GetAngle(b2Body_GetRotation(body)),
        b2Body_GetAngularVelocity(body));
    b2DestroyWorld(world);
}

int main(void)
{
    print_case("floor_circle", shape_circle, false);
    print_case("floor_capsule", shape_capsule, false);
    print_case("floor_segment", shape_segment, false);
    print_case("floor_polygon", shape_polygon, false);
    print_case("chain_circle", shape_circle, true);
    print_case("chain_capsule", shape_capsule, true);
    print_case("chain_polygon", shape_polygon, true);
    print_chain_transition();
    return 0;
}
