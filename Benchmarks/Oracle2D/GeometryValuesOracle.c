#include <box2d/box2d.h>
#include <stdio.h>

static void record(const char* kind, int shift, int test, int shape, b2CastOutput h)
{
    printf("%s_%d_%d_%d %d %.9g %.9g %.9g %.9g %.9g\n", kind, shift, test, shape,
           h.hit, h.fraction, h.point.x, h.point.y, h.normal.x, h.normal.y);
}

int main(void)
{
    const b2RayCastInput cases[] = {
        {{-3, 0.2f}, {0, 0}, 1}, // zero_outside
        {{0.2f, 0.1f}, {0, 0}, 1}, // zero_inside
        {{-1, 0}, {0, 0}, 1}, // zero_surface
        {{-3, 0.2f}, {4, 0}, 0}, // fraction_zero_outside
        {{0.2f, 0.1f}, {4, 0}, 0}, // fraction_zero_inside
        {{-1, 0}, {4, 0}, 0}, // fraction_zero_surface
        {{-1.01f, 0}, {1e-06f, 0}, 99999}, // small_translation
        {{-3, 0.2f}, {4, 0}, 99999}, // near_upper
        {{0.2f, 0.1f}, {4, 0}, 1}, // moving_inside
        {{-3, 1}, {6, 0}, 1}, // tangent
        {{-3, 3}, {6, 0}, 1}, // miss
        {{0, -3}, {0, 6}, 1}, // segment_front
        {{0, 3}, {0, -6}, 1}, // segment_back
        {{-1, -3}, {0, 3}, 1}, // endpoint
        {{-3, 0.2f}, {4, 0}, 0.1f}, // capped
        {{0, 3}, {0, -6}, 1}, // cap_upper
        {{-3, -3}, {6, 6}, 1}, // diagonal
        {{-1, 0}, {-4, 0}, 1}, // surface_away
    };
    for (int shift = 0; shift < 2; ++shift) {
        b2Vec2 offset = shift ? (b2Vec2){6, -2} : b2Vec2_zero;
        b2Circle circle = {offset, 1};
        b2Capsule capsule = {b2Add(offset, (b2Vec2){0, -.5f}), b2Add(offset, (b2Vec2){0, .5f}), 1};
        b2Polygon box = b2MakeOffsetBox(1, 1, offset, b2Rot_identity);
        b2Polygon rounded = b2MakeRoundedBox(.75f, .75f, .25f);
        for (int k = 0; k < rounded.count; ++k) rounded.vertices[k] = b2Add(rounded.vertices[k], offset);
        rounded.centroid = offset;
        b2Segment segment = {b2Add(offset, (b2Vec2){-1, 0}), b2Add(offset, (b2Vec2){1, 0})};
        for (int test = 0; test < 18; ++test) {
            b2RayCastInput ray = cases[test];
            ray.origin = b2Add(ray.origin, offset);
            b2CastOutput hits[] = {b2RayCastCircle(&ray, &circle), b2RayCastCapsule(&ray, &capsule),
                b2RayCastPolygon(&ray, &box), b2RayCastPolygon(&ray, &rounded), b2RayCastSegment(&ray, &segment, false)};
            b2ShapeCastInput moving = {0};
            moving.proxy = b2MakeProxy(&ray.origin, 1, .1f);
            moving.translation = ray.translation;
            moving.maxFraction = ray.maxFraction;
            b2CastOutput casts[] = {b2ShapeCastCircle(&moving, &circle), b2ShapeCastCapsule(&moving, &capsule),
                b2ShapeCastPolygon(&moving, &box), b2ShapeCastPolygon(&moving, &rounded), b2ShapeCastSegment(&moving, &segment)};
            for (int shape = 0; shape < 5; ++shape) {
                record("ray", shift, test, shape, hits[shape]);
                record("cast", shift, test, shape, casts[shape]);
            }
        }
    }
}
