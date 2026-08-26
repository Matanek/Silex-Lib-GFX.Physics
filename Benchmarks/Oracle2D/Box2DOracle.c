// SPDX-License-Identifier: MIT

#include <box2d/box2d.h>

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const float pi = 3.14159265358979323846f;

#if defined(NDEBUG)
static const char* build_mode = "release";
#else
static const char* build_mode = "debug";
#endif

typedef struct Metrics
{
    double elapsed_ms;
    double centroid_x;
    double centroid_y;
    double maximum_speed;
    double minimum_y;
    double maximum_overlap_mm;
    double state_signature;
    int awake_count;
    int contact_count;
    int memory_bytes;
} Metrics;

static double now_ms(void)
{
    struct timespec value;
    timespec_get(&value, TIME_UTC);
    return (double)value.tv_sec * 1000.0 + (double)value.tv_nsec / 1000000.0;
}

static b2BodyId create_box(
    b2WorldId world,
    bool dynamic,
    float width,
    float height,
    float x,
    float y,
    float rotation,
    float friction,
    float angular_damping,
    bool allow_sleep,
    float velocity_x,
    float velocity_y)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = dynamic ? b2_dynamicBody : b2_staticBody;
    body_definition.position = (b2Vec2){x, y};
    body_definition.rotation = b2MakeRot(rotation);
    body_definition.linearVelocity = (b2Vec2){velocity_x, velocity_y};
    body_definition.angularDamping = angular_damping;
    body_definition.enableSleep = allow_sleep;
    b2BodyId body = b2CreateBody(world, &body_definition);

    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.material.friction = friction;
    if (dynamic)
    {
        shape_definition.density = 1.0f / (width * height);
    }
    b2Polygon polygon = b2MakeBox(width * 0.5f, height * 0.5f);
    b2CreatePolygonShape(body, &shape_definition, &polygon);
    return body;
}

static b2BodyId create_circle(
    b2WorldId world,
    float radius,
    float x,
    float y,
    float friction,
    float angular_damping,
    bool allow_sleep)
{
    b2BodyDef body_definition = b2DefaultBodyDef();
    body_definition.type = b2_dynamicBody;
    body_definition.position = (b2Vec2){x, y};
    body_definition.angularDamping = angular_damping;
    body_definition.enableSleep = allow_sleep;
    b2BodyId body = b2CreateBody(world, &body_definition);

    b2ShapeDef shape_definition = b2DefaultShapeDef();
    shape_definition.material.friction = friction;
    shape_definition.density = 1.0f / (pi * radius * radius);
    b2Circle circle = {{0.0f, 0.0f}, radius};
    b2CreateCircleShape(body, &shape_definition, &circle);
    return body;
}

static Metrics collect_metrics(
    b2WorldId world,
    const b2BodyId* bodies,
    int body_count,
    double elapsed_ms,
    float circle_radius)
{
    Metrics metrics = {0};
    metrics.elapsed_ms = elapsed_ms;
    metrics.minimum_y = INFINITY;
    metrics.maximum_overlap_mm = -1.0;

    for (int index = 0; index < body_count; ++index)
    {
        b2Vec2 position = b2Body_GetPosition(bodies[index]);
        b2Vec2 velocity = b2Body_GetLinearVelocity(bodies[index]);
        float angular_velocity = b2Body_GetAngularVelocity(bodies[index]);
        double speed = sqrt((double)velocity.x * velocity.x + (double)velocity.y * velocity.y);
        metrics.centroid_x += position.x;
        metrics.centroid_y += position.y;
        metrics.maximum_speed = fmax(metrics.maximum_speed, speed);
        metrics.minimum_y = fmin(metrics.minimum_y, position.y);
        metrics.state_signature +=
            (double)(index + 1) * (position.x + position.y * 3.0 + velocity.x * 5.0 + velocity.y * 7.0 + angular_velocity * 11.0);
    }

    if (body_count > 0)
    {
        metrics.centroid_x /= body_count;
        metrics.centroid_y /= body_count;
    }

    if (circle_radius > 0.0f)
    {
        const double diameter = circle_radius * 2.0;
        metrics.maximum_overlap_mm = 0.0;
        for (int first = 0; first < body_count; ++first)
        {
            b2Vec2 first_position = b2Body_GetPosition(bodies[first]);
            for (int second = first + 1; second < body_count; ++second)
            {
                b2Vec2 second_position = b2Body_GetPosition(bodies[second]);
                double x = second_position.x - first_position.x;
                double y = second_position.y - first_position.y;
                double overlap = diameter - sqrt(x * x + y * y);
                metrics.maximum_overlap_mm = fmax(metrics.maximum_overlap_mm, overlap * 1000.0);
            }
        }
    }

    b2Counters counters = b2World_GetCounters(world);
    metrics.awake_count = b2World_GetAwakeBodyCount(world);
    metrics.contact_count = counters.contactCount;
    metrics.memory_bytes = counters.byteCount;
    return metrics;
}

static void print_metrics(
    const char* scenario,
    int body_count,
    int step_count,
    double time_step,
    Metrics metrics)
{
    printf(
        "SILEX_PHYSICS_CORPUS schema=2 engine=box2d-3.1.1 engine_version=3.1.1 "
        "oracle_version=3.1.1 oracle_revision=8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3 "
        "solver=box2d-soft-step substeps=4 scenario=%s mode=%s workers=1 bodies=%d steps=%d dt=%.9f "
        "elapsed_ms=%.6f step_ms=%.6f centroid_x=%.9f centroid_y=%.9f max_speed=%.9f min_y=%.9f "
        "max_overlap_mm=%.9f awake=%d contacts=%d state_signature=%.9f memory_bytes=%d\n",
        scenario,
        build_mode,
        body_count,
        step_count,
        time_step,
        metrics.elapsed_ms,
        metrics.elapsed_ms / step_count,
        metrics.centroid_x,
        metrics.centroid_y,
        metrics.maximum_speed,
        metrics.minimum_y,
        metrics.maximum_overlap_mm,
        metrics.awake_count,
        metrics.contact_count,
        metrics.state_signature,
        metrics.memory_bytes);
}

static void step_world(b2WorldId world, int step_count, float time_step)
{
    for (int step = 0; step < step_count; ++step)
    {
        b2World_Step(world, time_step, 4);
    }
}

static void run_release_parity(void)
{
    const int step_count = 120;
    const float time_step = 1.0f / 120.0f;
    b2WorldDef world_definition = b2DefaultWorldDef();
    b2WorldId world = b2CreateWorld(&world_definition);
    create_box(world, false, 8.0f, 1.0f, 0.0f, -0.5f, 0.0f, 0.6f, 0.0f, true, 0.0f, 0.0f);
    b2BodyId body = create_box(world, true, 1.0f, 1.0f, 0.0f, 2.0f, 0.0f, 0.6f, 0.0f, true, 0.0f, 0.0f);

    double started = now_ms();
    step_world(world, step_count, time_step);
    Metrics metrics = collect_metrics(world, &body, 1, now_ms() - started, 0.0f);
    print_metrics("release-parity", 1, step_count, time_step, metrics);
    b2DestroyWorld(world);
}

static void run_sparse(int body_count)
{
    const int step_count = 120;
    const float time_step = 1.0f / 60.0f;
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.gravity = (b2Vec2){0.0f, 0.0f};
    world_definition.enableSleep = false;
    b2WorldId world = b2CreateWorld(&world_definition);
    b2BodyId* bodies = malloc((size_t)body_count * sizeof(*bodies));
    if (bodies == NULL)
    {
        fprintf(stderr, "cannot allocate sparse body handles\n");
        exit(2);
    }

    for (int index = 0; index < body_count; ++index)
    {
        int column = index % 100;
        int row = index / 100;
        bodies[index] = create_box(
            world,
            true,
            0.5f,
            0.5f,
            column * 1.25f,
            row * 1.25f,
            0.0f,
            0.6f,
            0.0f,
            false,
            2.0f,
            0.25f);
    }

    double started = now_ms();
    step_world(world, step_count, time_step);
    Metrics metrics = collect_metrics(world, bodies, body_count, now_ms() - started, 0.0f);
    char scenario[32];
    snprintf(scenario, sizeof(scenario), "sparse-%d", body_count);
    print_metrics(scenario, body_count, step_count, time_step, metrics);
    free(bodies);
    b2DestroyWorld(world);
}

static void run_pile(void)
{
    const int body_count = 1000;
    const int step_count = 240;
    const int columns = 50;
    const float time_step = 1.0f / 60.0f;
    b2WorldDef world_definition = b2DefaultWorldDef();
    b2WorldId world = b2CreateWorld(&world_definition);
    create_box(world, false, 24.0f, 1.0f, 0.0f, -0.5f, 0.0f, 0.8f, 0.0f, true, 0.0f, 0.0f);
    b2BodyId* bodies = malloc((size_t)body_count * sizeof(*bodies));
    if (bodies == NULL)
    {
        fprintf(stderr, "cannot allocate pile body handles\n");
        exit(2);
    }

    for (int index = 0; index < body_count; ++index)
    {
        int column = index % columns;
        int row = index / columns;
        bodies[index] = create_box(
            world,
            true,
            0.4f,
            0.4f,
            (column - 24.5f) * 0.405f,
            0.2f + row * 0.405f,
            ((index % 3) - 1.0f) * 0.002f,
            0.75f,
            0.12f,
            true,
            0.0f,
            0.0f);
    }

    double started = now_ms();
    step_world(world, step_count, time_step);
    Metrics metrics = collect_metrics(world, bodies, body_count, now_ms() - started, 0.0f);
    print_metrics("pile-1000", body_count, step_count, time_step, metrics);
    free(bodies);
    b2DestroyWorld(world);
}

static void create_container(b2WorldId world, float width, float height)
{
    const float depth = 4.0f;
    const float half_width = width * 0.5f;
    const float half_height = height * 0.5f;
    const float half_depth = depth * 0.5f;
    create_box(world, false, depth, height, -half_width - half_depth, 0.0f, 0.0f, 0.9f, 0.0f, true, 0.0f, 0.0f);
    create_box(world, false, depth, height, half_width + half_depth, 0.0f, 0.0f, 0.9f, 0.0f, true, 0.0f, 0.0f);
    create_box(world, false, width + depth * 2.0f, depth, 0.0f, -half_height - half_depth, 0.0f, 0.9f, 0.0f, true, 0.0f, 0.0f);
    create_box(world, false, width + depth * 2.0f, depth, 0.0f, half_height + half_depth, 0.0f, 0.9f, 0.0f, true, 0.0f, 0.0f);
}

static void run_circle(int body_count)
{
    const int step_count = 300;
    const float time_step = 1.0f / 60.0f;
    const float radius = body_count > 2000 ? 0.025f : 0.05f;
    const int columns = body_count > 2000 ? 170 : 87;
    const float spacing = radius * 2.0f * 1.04f;
    const float width = 9.2f;
    const float height = 6.0f;
    const float half_height = height * 0.5f;
    b2WorldDef world_definition = b2DefaultWorldDef();
    world_definition.enableSleep = false;
    b2WorldId world = b2CreateWorld(&world_definition);
    create_container(world, width, height);
    b2BodyId* bodies = malloc((size_t)body_count * sizeof(*bodies));
    if (bodies == NULL)
    {
        fprintf(stderr, "cannot allocate circle body handles\n");
        exit(2);
    }

    for (int index = 0; index < body_count; ++index)
    {
        int column = index % columns;
        int row = index / columns;
        bodies[index] = create_circle(
            world,
            radius,
            (column - (columns - 1) * 0.5f) * spacing,
            -half_height + radius * 1.05f + row * spacing,
            0.75f,
            0.12f,
            false);
    }

    double started = now_ms();
    step_world(world, step_count, time_step);
    Metrics metrics = collect_metrics(world, bodies, body_count, now_ms() - started, radius);
    char scenario[32];
    snprintf(scenario, sizeof(scenario), "circle-%d", body_count);
    print_metrics(scenario, body_count, step_count, time_step, metrics);
    free(bodies);
    b2DestroyWorld(world);
}

static void print_usage(const char* executable)
{
    fprintf(
        stderr,
        "usage: %s --release-parity|--sparse-1000|--sparse-5000|--sparse-10000|--pile-1000|--circle-1800|--circle-5000|--all\n",
        executable);
}

int main(int argument_count, char** arguments)
{
    if (argument_count != 2)
    {
        print_usage(arguments[0]);
        return 2;
    }
    const char* scenario = arguments[1];
    if (strcmp(scenario, "--release-parity") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_release_parity();
    }
    if (strcmp(scenario, "--sparse-1000") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_sparse(1000);
    }
    if (strcmp(scenario, "--sparse-5000") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_sparse(5000);
    }
    if (strcmp(scenario, "--sparse-10000") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_sparse(10000);
    }
    if (strcmp(scenario, "--pile-1000") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_pile();
    }
    if (strcmp(scenario, "--circle-1800") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_circle(1800);
    }
    if (strcmp(scenario, "--circle-5000") == 0 || strcmp(scenario, "--all") == 0)
    {
        run_circle(5000);
    }

    if (
        strcmp(scenario, "--release-parity") != 0 && strcmp(scenario, "--sparse-1000") != 0 &&
        strcmp(scenario, "--sparse-5000") != 0 && strcmp(scenario, "--sparse-10000") != 0 &&
        strcmp(scenario, "--pile-1000") != 0 && strcmp(scenario, "--circle-1800") != 0 &&
        strcmp(scenario, "--circle-5000") != 0 && strcmp(scenario, "--all") != 0)
    {
        print_usage(arguments[0]);
        return 2;
    }
    return 0;
}
