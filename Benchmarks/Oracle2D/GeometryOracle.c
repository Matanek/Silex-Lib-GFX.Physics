// Differential geometry witness against Box2D v3.1.1, commit 8c661469.
// Box2D is Copyright (c) 2022 Erin Catto and distributed under the MIT License.

#include <box2d/box2d.h>
#include <stdio.h>

static b2ShapeProxy proxy_from_polygon(const b2Polygon* polygon)
{
    return b2MakeProxy(polygon->vertices, polygon->count, polygon->radius);
}

static float polygon_area_twice(const b2Hull* hull)
{
    float area = 0.0f;
    for (int index = 0; index < hull->count; ++index)
    {
        int next = (index + 1) % hull->count;
        area += b2Cross(hull->points[index], hull->points[next]);
    }
    return area;
}

int main(void)
{
    const b2Transform identity = b2Transform_identity;

    b2Vec2 circle_point = {0.0f, 0.0f};
    b2ShapeProxy circle = b2MakeProxy(&circle_point, 1, 1.0f);
    b2Polygon box_shape = b2MakeBox(1.0f, 1.0f);
    b2ShapeProxy box = proxy_from_polygon(&box_shape);
    b2DistanceInput distance_input = {
        .proxyA = circle,
        .proxyB = box,
        .transformA = identity,
        .transformB = {{4.0f, 0.0f}, b2Rot_identity},
        .useRadii = true,
    };
    b2SimplexCache cache = {0};
    b2DistanceOutput distance = b2ShapeDistance(&distance_input, &cache, NULL, 0);
    printf("distance %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n",
           distance.distance, distance.pointA.x, distance.pointA.y,
           distance.pointB.x, distance.pointB.y,
           distance.normal.x, distance.normal.y);

    b2Capsule capsule = {{-1.0f, 0.0f}, {1.0f, 0.0f}, 0.5f};
    b2Circle manifold_circle = {{0.0f, 0.0f}, 0.75f};
    b2Transform circle_transform = {{0.0f, 1.0f}, b2Rot_identity};
    b2Manifold manifold = b2CollideCapsuleAndCircle(
        &capsule, identity, &manifold_circle, circle_transform);
    printf("manifold %d %.9g %.9g %.9g %.9g %.9g\n",
           manifold.pointCount, manifold.normal.x, manifold.normal.y,
           manifold.points[0].point.x, manifold.points[0].point.y,
           manifold.points[0].separation);

    b2RayCastInput ray = {{-3.0f, 0.0f}, {6.0f, 0.0f}, 1.0f};
    b2CastOutput ray_output = b2RayCastPolygon(&ray, &box_shape);
    printf("ray %d %.9g %.9g %.9g %.9g %.9g\n",
           ray_output.hit ? 1 : 0, ray_output.fraction,
           ray_output.point.x, ray_output.point.y,
           ray_output.normal.x, ray_output.normal.y);

    b2Segment chain_segment = {{-2.0f, 0.0f}, {2.0f, 0.0f}};
    b2RayCastInput chain_front_ray = {{0.0f, -2.0f}, {0.0f, 4.0f}, 1.0f};
    b2CastOutput chain_front = b2RayCastSegment(
        &chain_front_ray, &chain_segment, true);
    printf("chain_front %d %.9g %.9g %.9g\n",
           chain_front.hit ? 1 : 0, chain_front.fraction,
           chain_front.normal.x, chain_front.normal.y);

    b2RayCastInput chain_back_ray = {{0.0f, 2.0f}, {0.0f, -4.0f}, 1.0f};
    b2CastOutput chain_back = b2RayCastSegment(
        &chain_back_ray, &chain_segment, true);
    printf("chain_back %d\n", chain_back.hit ? 1 : 0);

    b2ShapeProxy cast_circle = b2MakeProxy(&circle_point, 1, 0.5f);
    b2ShapeCastPairInput cast_input = {
        .proxyA = box,
        .proxyB = cast_circle,
        .transformA = identity,
        .transformB = {{-3.0f, 0.0f}, b2Rot_identity},
        .translationB = {6.0f, 0.0f},
        .maxFraction = 1.0f,
        .canEncroach = false,
    };
    b2CastOutput cast_output = b2ShapeCast(&cast_input);
    printf("shape_cast %d %.9g %.9g %.9g %.9g %.9g\n",
           cast_output.hit ? 1 : 0, cast_output.fraction,
           cast_output.point.x, cast_output.point.y,
           cast_output.normal.x, cast_output.normal.y);

    b2Vec2 hull_points[] = {
        {1.0f, 1.0f}, {-1.0f, -1.0f}, {-1.0f, 1.0f},
        {1.0f, -1.0f}, {0.0f, 0.0f},
    };
    b2Hull hull = b2ComputeHull(hull_points, 5);
    printf("hull %d %.9g\n", hull.count, polygon_area_twice(&hull));

    b2Vec2 degenerate_points[] = {
        {-1.0f, 0.0f}, {0.0f, 0.0f}, {1.0f, 0.0f},
    };
    b2Hull degenerate = b2ComputeHull(degenerate_points, 3);
    printf("degenerate_hull %d\n", degenerate.count);

    return 0;
}
