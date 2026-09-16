#include <box2d/box2d.h>
#include <float.h>
#include <math.h>
#include <stdio.h>

static void record(const char* family, const char* value, bool valid)
{
    printf("%s %s %d\n", family, value, valid);
}

int main(void)
{
    const char* names[] = {"zero", "negative", "near", "upper", "huge", "inf", "nan", "negative-inf"};
    float values[] = {0, -1, 99999, 100000, FLT_MAX, INFINITY, NAN, -INFINITY};
    for (int i = 0; i < 8; ++i) {
        float v = values[i];
        record("scalar", names[i], b2IsValidFloat(v));
        record("vector", names[i], b2IsValidVec2((b2Vec2){v, v}));
        record("rotation", names[i], b2IsValidRotation((b2Rot){cosf(v), sinf(v)}));
        record("aabb", names[i], b2IsValidAABB((b2AABB){{-v, -v}, {v, v}}));
        record("aabb-overflow", names[i], b2IsValidAABB((b2AABB){{v-v, v-v}, {v+v, v+v}}) && v >= 0);
        record("aabb-position", names[i], b2IsValidAABB((b2AABB){{v, v}, {v, v}}));
        b2RayCastInput ray = {{v, v}, {0, 0}, 1};
        record("ray-origin", names[i], b2IsValidRay(&ray));
        ray = (b2RayCastInput){{0, 0}, {v, v}, 1};
        record("ray-motion", names[i], b2IsValidRay(&ray));
        ray = (b2RayCastInput){{0, 0}, {0, 0}, v};
        record("ray-fraction", names[i], b2IsValidRay(&ray));
    }
    record("raw-rotation", "zero", b2IsValidRotation((b2Rot){0, 0}));
    record("raw-rotation", "unit", b2IsValidRotation((b2Rot){0, 1}));
    record("raw-rotation", "scaled", b2IsValidRotation((b2Rot){0, 2}));
    record("plane", "zero-normal", b2IsValidPlane((b2Plane){{0, 0}, 0}));
    record("plane", "unit", b2IsValidPlane((b2Plane){{0, 1}, -2}));
    record("plane", "scaled", b2IsValidPlane((b2Plane){{0, 2}, 0}));
    record("plane", "inf-normal", b2IsValidPlane((b2Plane){{INFINITY, 0}, 0}));
    record("plane", "nan-normal", b2IsValidPlane((b2Plane){{NAN, 0}, 0}));
    record("plane", "inf-offset", b2IsValidPlane((b2Plane){{0, 1}, INFINITY}));
    record("plane", "nan-offset", b2IsValidPlane((b2Plane){{0, 1}, NAN}));
}
