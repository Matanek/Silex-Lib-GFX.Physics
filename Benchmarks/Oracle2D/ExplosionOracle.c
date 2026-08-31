// Differential radial-explosion witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.

#include <box2d/box2d.h>
#include <stdint.h>
#include <stdio.h>

static b2BodyId make_circle(b2WorldId world, float x, float y, uint64_t category)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){x, y};
    b2BodyId body = b2CreateBody(world, &body_definition);
    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.density = 1.0f;
    shape_definition.filter.categoryBits = category;
    b2Circle circle = {{0.0f, 0.0f}, 0.25f};
    b2CreateCircleShape(body, &shape_definition, &circle);
    return body;
}

int main(void)
{
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyId near_body = make_circle(world, 1.0f, 0.0f, 2);
    b2BodyId far_body = make_circle(world, 3.0f, 0.0f, 2);
    b2BodyId rejected_body = make_circle(world, 0.0f, 2.0f, 1);

    b2ExplosionDef explosion = b2DefaultExplosionDef();
    explosion.maskBits = 2;
    explosion.position = (b2Vec2){0.0f, 0.0f};
    explosion.radius = 0.0f;
    explosion.falloff = 4.0f;
    explosion.impulsePerLength = 16.0f;
    b2World_Explode(world, &explosion);

    b2Vec2 near_velocity = b2Body_GetLinearVelocity(near_body);
    b2Vec2 far_velocity = b2Body_GetLinearVelocity(far_body);
    b2Vec2 rejected_velocity = b2Body_GetLinearVelocity(rejected_body);
    printf("count %d\n", 2);
    printf("near %.9g %.9g\n", near_velocity.x, near_velocity.y);
    printf("far %.9g %.9g\n", far_velocity.x, far_velocity.y);
    printf("rejected %.9g %.9g\n", rejected_velocity.x, rejected_velocity.y);

    b2DestroyWorld(world);
    return 0;
}
