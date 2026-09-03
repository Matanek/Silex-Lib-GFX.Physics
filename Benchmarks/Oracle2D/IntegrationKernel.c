// Adapted from Box2D 3.1.1 solver.c, pinned at
// 8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3.
// Copyright (c) 2023 Erin Catto. MIT: Box2D-LICENSE.txt.
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#ifdef SLOT8
#define F(name) float name; uint32_t padding_##name
#define B(name) uint64_t name
#define LAYOUT "slots8"
#else
#define F(name) float name
#define B(name) bool name
#define LAYOUT "packed4"
#endif
typedef struct { F(vx); F(vy); F(w); F(px); F(py); F(c); F(s); } Body;
typedef struct {
    F(x); F(y); F(torque); F(inverse_mass); F(inverse_inertia);
    F(gravity_scale); F(linear_damping); F(angular_damping);
    B(allow_fast_rotation); B(speed_capped);
} Forces;
#ifdef SLOT8
_Static_assert(sizeof(Body) == 56, "Silex Body stride");
_Static_assert(sizeof(Forces) == 80, "Silex Forces stride");
#endif

void integrate_velocity(Body* body, Forces* forces)
{
    const float h = 1.0f / 240.0f;
    const float max_angular = (0.25f * 3.14159265359f) * 60.0f;
    float linear_damping = 1.0f / (1.0f + h * forces->linear_damping);
    float angular_damping = 1.0f / (1.0f + h * forces->angular_damping);
    float gravity_scale = forces->inverse_mass > 0.0f ? forces->gravity_scale : 0.0f;
    float dx = (h * forces->inverse_mass) * forces->x + (h * gravity_scale) * 0.0f;
    float dy = (h * forces->inverse_mass) * forces->y + (h * gravity_scale) * -10.0f;
    float dw = h * forces->inverse_inertia * forces->torque;
    float vx = dx + linear_damping * body->vx;
    float vy = dy + linear_damping * body->vy;
    float w = dw + angular_damping * body->w;
    if (vx * vx + vy * vy > 16.0f) {
        float ratio = 4.0f / sqrtf(vx * vx + vy * vy);
        vx = ratio * vx;
        vy = ratio * vy;
        forces->speed_capped = true;
    }
    if (w * w > max_angular * max_angular && !forces->allow_fast_rotation) {
        float ratio = max_angular / fabsf(w);
        w *= ratio;
        forces->speed_capped = true;
    }
    body->vx = vx; body->vy = vy; body->w = w;
}

void integrate_position(Body* body)
{
    const float h = 1.0f / 240.0f;
    float angle = h * body->w;
    float c = body->c - angle * body->s;
    float s = body->s + angle * body->c;
    float magnitude = sqrtf(s * s + c * c);
    float inverse = magnitude > 0.0f ? 1.0f / magnitude : 0.0f;
    body->c = c * inverse; body->s = s * inverse;
    body->px += h * body->vx; body->py += h * body->vy;
}

void integrate(Body* bodies, Forces* forces, int64_t count, int64_t force_count)
{
    for (int64_t i = 0; i < count; ++i) {
        if (i >= force_count) abort();
        integrate_velocity(bodies + i, forces + i);
    }
    for (int64_t i = 0; i < count; ++i) integrate_position(bodies + i);
}

#ifdef BOX2D_CHECK
// Include the unmodified pinned translation unit to exercise its static tasks.
// This build is correctness-only. No oracle code enters either timed kernel.
#include "solver.c"
static void oracle_pass(Body* bodies, Forces* forces, int count)
{
    b2BodyState states[16] = {0};
    b2BodySim sims[16] = {0};
    if (count != 16) abort();
    for (int i = 0; i < count; ++i) {
        Body b = bodies[i]; Forces f = forces[i];
        states[i] = (b2BodyState){.linearVelocity = {b.vx, b.vy}, .angularVelocity = b.w,
            .deltaPosition = {b.px, b.py}, .deltaRotation = {b.c, b.s}};
        sims[i] = (b2BodySim){.force = {f.x, f.y}, .torque = f.torque,
            .invMass = f.inverse_mass, .invInertia = f.inverse_inertia,
            .gravityScale = f.gravity_scale, .linearDamping = f.linear_damping,
            .angularDamping = f.angular_damping, .allowFastRotation = f.allow_fast_rotation,
            .isSpeedCapped = f.speed_capped};
    }
    b2World world = {.gravity = {0.0f, -10.0f}};
    b2StepContext context = {.world = &world, .states = states, .sims = sims,
        .h = 1.0f / 240.0f, .inv_dt = 60.0f, .maxLinearVelocity = 4.0f};
    b2IntegrateVelocitiesTask(0, count, &context);
    b2IntegratePositionsTask(0, count, &context);
    for (int i = 0; i < count; ++i) {
        b2BodyState s = states[i];
        bodies[i] = (Body){.vx = s.linearVelocity.x, .vy = s.linearVelocity.y,
            .w = s.angularVelocity, .px = s.deltaPosition.x, .py = s.deltaPosition.y,
            .c = s.deltaRotation.c, .s = s.deltaRotation.s};
        forces[i].speed_capped = sims[i].isSpeedCapped;
    }
}
#endif

static double seconds(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t) != 0) abort();
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}

int main(int argc, char** argv)
{
    bool replay = argc > 1 && strcmp(argv[1], "--check-replay") == 0;
    bool full = replay || (argc > 1 && strcmp(argv[1], "--check-full") == 0);
    bool check = full || (argc > 1 && strcmp(argv[1], "--check") == 0);
#ifdef BOX2D_CHECK
    if (!check) abort();
#endif
    int64_t count = check ? 16 : 8192, passes = check && !full ? 8 : 2048;
    Body* bodies = calloc((size_t)count, sizeof(Body));
    Forces* forces = calloc((size_t)count, sizeof(Forces));
    if (!bodies || !forces) abort();
    for (int64_t i = 0; i < count; ++i) {
        float k = (float)(i % 16);
        bodies[i] = (Body){.vx = k - 8.0f, .vy = 0.5f, .w = (k - 8.0f) * 16.0f,
            .c = 0.6f, .s = 0.8f};
        forces[i] = (Forces){.x = k * 0.125f, .y = 0.25f, .torque = k - 8.0f,
            .inverse_mass = i % 4 == 0 ? 0.0f : 0.5f,
            .inverse_inertia = i % 4 == 0 ? 0.0f : 0.25f,
            .gravity_scale = 1.0f, .linear_damping = k * 0.25f,
            .angular_damping = k * 0.125f, .allow_fast_rotation = i % 4 == 1};
    }
    double start = seconds();
    for (int64_t pass = 0; pass < passes; ++pass) {
#ifdef BOX2D_CHECK
        oracle_pass(bodies, forces, (int)count);
#else
        integrate(bodies, forces, count, count);
#endif
        if (check) {
            for (int64_t i = 0; i < count; ++i) {
                Body b = bodies[i];
                printf("STATE %lld %lld %.9g %.9g %.9g %.9g %.9g %.9g %.9g %d\n",
                    (long long)pass, (long long)i, b.vx, b.vy, b.w,
                    b.px, b.py, b.c, b.s, forces[i].speed_capped ? 1 : 0);
            }
        }
        if (replay) {
            for (int64_t i = 0; i < count; ++i) {
                long long input_pass, input_index;
                int capped;
                Body b = {0};
                if (scanf(" STATE %lld %lld %f %f %f %f %f %f %f %d",
                    &input_pass, &input_index, &b.vx, &b.vy, &b.w, &b.px, &b.py,
                    &b.c, &b.s, &capped) != 10 || input_pass != pass || input_index != i ||
                    (capped != 0 && capped != 1)) abort();
                bodies[i] = b;
                forces[i].speed_capped = capped != 0;
            }
        }
    }
    if (!check) {
        double elapsed = (seconds() - start) * 1000.0, signature = 0.0;
        for (int64_t i = 0; i < count; ++i) {
            Body b = bodies[i]; float capped = forces[i].speed_capped ? 1.0f : 0.0f;
            signature += (double)(b.vx + b.vy * 2.0f + b.w * 3.0f + b.px * 5.0f +
                b.py * 7.0f + b.c * 11.0f + b.s * 13.0f + capped * 17.0f);
        }
        printf("KERNEL integration clang " LAYOUT " %lld %lld %.9f %.17g\n",
            (long long)count, (long long)passes, elapsed, signature);
    }
    free(forces); free(bodies);
    return 0;
}
