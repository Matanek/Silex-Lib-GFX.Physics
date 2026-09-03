// One-point adaptation of Box2D 3.1.1 src/contact_solver.c,
// b2SolveOverflowContacts, revision 8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3.
// Copyright (c) 2022-2023 Erin Catto. MIT license: Box2D-LICENSE.txt.
// Keep arithmetic and fixtures aligned with ../ContactKernel2D.sx.
#include <stdbool.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Same field offsets and strides as the current Silex slot representation.
// A second build without SLOT8 diagnoses layout cost, not compiler equality.
#ifdef SLOT8
#define F(name) float name; uint32_t padding_##name
#define LAYOUT "slots8"
#else
#define F(name) float name
#define LAYOUT "packed4"
#endif

typedef struct { F(vx); F(vy); F(w); F(px); F(py); F(c); F(s); } State;
typedef struct {
    int64_t first, second;
    F(nx); F(ny); F(ma); F(mb); F(ia); F(ib);
    F(ax); F(ay); F(bx); F(by); F(separation);
    F(normal_mass); F(tangent_mass); F(bias_rate); F(mass_scale); F(impulse_scale);
    F(friction); F(tangent_speed); F(rolling_mass); F(rolling_resistance);
} Constraint;
typedef struct { F(normal); F(tangent); F(total); F(rolling); } Impulses;
#ifdef SLOT8
_Static_assert(sizeof(State) == 56, "Silex State stride");
_Static_assert(sizeof(Constraint) == 176, "Silex Constraint stride");
_Static_assert(sizeof(Impulses) == 32, "Silex Impulses stride");
#endif

// Match STD.Math, including NaN and signed-zero decisions. Box2D's simpler
// comparison helpers are not a fair compiler comparator for that contract.
static float maximum(float a, float b)
{
    if (a != a) return b;
    if (b != b) return a;
    if (a > b) return a;
    if (b > a) return b;
    if (!(copysignf(1.0f, a) < 0.0f)) return a;
    return b;
}
static float minimum(float a, float b)
{
    if (a != a) return b;
    if (b != b) return a;
    if (a < b) return a;
    if (b < a) return b;
    if (copysignf(1.0f, a) < 0.0f) return a;
    return b;
}

// Views accept negative indexing in Silex. Retain the same bounds contract;
// no restrict, fast-math, forced inlining or vectorization switches are used.
static int64_t checked_index(int64_t index, int64_t count)
{
    if (index < 0) index += count;
    if (index < 0 || index >= count) abort();
    return index;
}

void solve_contact(State* states, int64_t state_count, const Constraint* c,
                   Impulses* p, bool use_bias)
{
    int64_t first = checked_index(c->first, state_count);
    int64_t second = checked_index(c->second, state_count);
    State a = states[first], b = states[second];
    float vx_a = a.vx, vy_a = a.vy, w_a = a.w;
    float vx_b = b.vx, vy_b = b.vy, w_b = b.w;
    float dx = (b.px - a.px) +
        ((b.c * c->bx - b.s * c->by) - (a.c * c->ax - a.s * c->ay));
    float dy = (b.py - a.py) +
        ((b.s * c->bx + b.c * c->by) - (a.s * c->ax + a.c * c->ay));
    float separation = c->separation + (dx * c->nx + dy * c->ny);
    float bias = 0.0f, mass_scale = 1.0f, impulse_scale = 0.0f;
    if (separation > 0.0f) bias = separation * 240.0f;
    else if (use_bias) {
        bias = maximum(c->bias_rate * separation, -3.0f);
        mass_scale = c->mass_scale;
        impulse_scale = c->impulse_scale;
    }
    float vrx = (vx_b - w_b * c->by) - (vx_a - w_a * c->ay);
    float vry = (vy_b + w_b * c->bx) - (vy_a + w_a * c->ax);
    float vn = vrx * c->nx + vry * c->ny;
    float impulse = -c->normal_mass * mass_scale * (vn + bias) - impulse_scale * p->normal;
    float next_normal = maximum(p->normal + impulse, 0.0f);
    impulse = next_normal - p->normal;
    p->normal = next_normal;
    p->total += next_normal;
    float impulse_x = impulse * c->nx, impulse_y = impulse * c->ny;
    vx_a -= c->ma * impulse_x;
    vy_a -= c->ma * impulse_y;
    w_a -= c->ia * (c->ax * impulse_y - c->ay * impulse_x);
    vx_b += c->mb * impulse_x;
    vy_b += c->mb * impulse_y;
    w_b += c->ib * (c->bx * impulse_y - c->by * impulse_x);

    float tx = c->ny, ty = -c->nx;
    float vtx = (vx_b - w_b * c->by) - (vx_a - w_a * c->ay);
    float vty = (vy_b + w_b * c->bx) - (vy_a + w_a * c->ax);
    float vt = (vtx * tx + vty * ty) - c->tangent_speed;
    impulse = c->tangent_mass * (-vt);
    float limit = c->friction * p->normal;
    float next_tangent = minimum(maximum(p->tangent + impulse, -limit), limit);
    impulse = next_tangent - p->tangent;
    p->tangent = next_tangent;
    impulse_x = impulse * tx;
    impulse_y = impulse * ty;
    vx_a -= c->ma * impulse_x;
    vy_a -= c->ma * impulse_y;
    w_a -= c->ia * (c->ax * impulse_y - c->ay * impulse_x);
    vx_b += c->mb * impulse_x;
    vy_b += c->mb * impulse_y;
    w_b += c->ib * (c->bx * impulse_y - c->by * impulse_x);

    float rolling_delta = -c->rolling_mass * (w_b - w_a);
    float rolling_limit = c->rolling_resistance * next_normal;
    float next_rolling = minimum(maximum(p->rolling + rolling_delta, -rolling_limit), rolling_limit);
    rolling_delta = next_rolling - p->rolling;
    p->rolling = next_rolling;
    w_a -= c->ia * rolling_delta;
    w_b += c->ib * rolling_delta;
    states[first].vx = vx_a;
    states[first].vy = vy_a;
    states[first].w = w_a;
    states[second].vx = vx_b;
    states[second].vy = vy_b;
    states[second].w = w_b;
}

void run_kernel(State* states, int64_t state_count, const Constraint* constraints,
                Impulses* impulses, int64_t count, int64_t passes)
{
    for (int64_t pass = 0; pass < passes; ++pass)
        for (int64_t i = 0; i < count; ++i)
            solve_contact(states, state_count, constraints + i, impulses + i, pass % 2 == 0);
}

#ifdef BOX2D_CHECK
#include "body.h"
#include "contact_solver.h"
#include "constraint_graph.h"
#include "solver_set.h"
#include "world.h"

// Call the actual, unmodified pinned oracle; never time this adapter.
static void oracle_pass(State* states, Constraint* constraints, Impulses* impulses,
                        int count, bool use_bias)
{
    b2BodyState bodies[32] = {0};
    b2ContactConstraint contacts[16] = {0};
    if (count > 16) abort();
    for (int i = 0; i < count * 2; ++i) {
        State s = states[i];
        bodies[i] = (b2BodyState){{s.vx, s.vy}, s.w, 0, {s.px, s.py}, {s.c, s.s}};
    }
    for (int i = 0; i < count; ++i) {
        Constraint c = constraints[i];
        Impulses p = impulses[i];
        contacts[i] = (b2ContactConstraint){
            .indexA = (int)c.first, .indexB = (int)c.second,
            .points = {{.anchorA = {c.ax, c.ay}, .anchorB = {c.bx, c.by},
                .baseSeparation = c.separation, .normalMass = c.normal_mass,
                .tangentMass = c.tangent_mass, .normalImpulse = p.normal,
                .tangentImpulse = p.tangent, .totalNormalImpulse = p.total}},
            .normal = {c.nx, c.ny}, .invMassA = c.ma, .invMassB = c.mb,
            .invIA = c.ia, .invIB = c.ib, .friction = c.friction,
            .tangentSpeed = c.tangent_speed, .rollingMass = c.rolling_mass,
            .rollingResistance = c.rolling_resistance, .rollingImpulse = p.rolling,
            .softness = {c.bias_rate, c.mass_scale, c.impulse_scale}, .pointCount = 1,
        };
    }
    b2SolverSet sets[3] = {0};
    sets[b2_awakeSet].bodyStates.data = bodies;
    sets[b2_awakeSet].bodyStates.count = count * 2;
    sets[b2_awakeSet].bodyStates.capacity = count * 2;
    b2World world = {0};
    world.solverSets.data = sets;
    world.solverSets.count = 3;
    world.solverSets.capacity = 3;
    world.maxContactPushSpeed = 3.0f;
    b2ConstraintGraph graph = {0};
    graph.colors[B2_OVERFLOW_INDEX].overflowConstraints = contacts;
    graph.colors[B2_OVERFLOW_INDEX].contactSims.count = count;
    b2StepContext context = {.world = &world, .graph = &graph, .inv_h = 240.0f};
    b2SolveOverflowContacts(&context, use_bias);
    for (int i = 0; i < count * 2; ++i) {
        states[i].vx = bodies[i].linearVelocity.x;
        states[i].vy = bodies[i].linearVelocity.y;
        states[i].w = bodies[i].angularVelocity;
    }
    for (int i = 0; i < count; ++i) {
        impulses[i].normal = contacts[i].points[0].normalImpulse;
        impulses[i].tangent = contacts[i].points[0].tangentImpulse;
        impulses[i].total = contacts[i].points[0].totalNormalImpulse;
        impulses[i].rolling = contacts[i].rollingImpulse;
    }
}
#endif

static double seconds(void)
{
    struct timespec value;
    if (clock_gettime(CLOCK_MONOTONIC, &value) != 0) abort();
    return (double)value.tv_sec + (double)value.tv_nsec * 1e-9;
}

int main(int argc, char** argv)
{
    bool check = argc > 1 && strcmp(argv[1], "--check") == 0;
    int64_t count = check ? 16 : 2048, passes = check ? 8 : 2048;
    State* states = calloc((size_t)count * 2, sizeof(State));
    Constraint* constraints = calloc((size_t)count, sizeof(Constraint));
    Impulses* impulses = calloc((size_t)count, sizeof(Impulses));
    if (!states || !constraints || !impulses) abort();
    for (int64_t i = 0; i < count; ++i) {
        float k = (float)(i % 16);
        states[i * 2] = (State){.vx = k * 0.125f, .vy = -0.5f, .w = 0.25f, .c = 1.0f};
        states[i * 2 + 1] = (State){.vx = -0.25f, .vy = k * 0.0625f - 1.0f, .w = -0.5f,
            .px = 0.00390625f, .py = -0.0078125f, .c = 0.6f, .s = 0.8f};
        constraints[i] = (Constraint){.first = i * 2, .second = i * 2 + 1,
            .nx = 0.6f, .ny = 0.8f, .ma = i % 4 == 0 ? 0.0f : 1.0f, .mb = 0.5f,
            .ia = i % 4 == 0 ? 0.0f : 0.25f, .ib = 0.5f,
            .ax = 0.125f, .ay = -0.0625f, .bx = -0.125f, .by = 0.0625f,
            .separation = (k - 8.0f) * 0.03125f,
            .normal_mass = 0.5f, .tangent_mass = 0.375f,
            .bias_rate = 12.0f, .mass_scale = 0.75f, .impulse_scale = 0.25f,
            .friction = (float)(i % 4) * 0.25f, .tangent_speed = (k - 8.0f) * 0.125f,
            .rolling_mass = 0.5f, .rolling_resistance = 0.125f};
        impulses[i] = (Impulses){.normal = 0.125f, .tangent = 0.03125f, .rolling = -0.015625f};
    }
    double start = seconds();
    if (check) {
        for (int64_t pass = 0; pass < passes; ++pass) {
#ifdef BOX2D_CHECK
            oracle_pass(states, constraints, impulses, (int)count, pass % 2 == 0);
#else
            for (int64_t i = 0; i < count; ++i)
                solve_contact(states, count * 2, constraints + i, impulses + i, pass % 2 == 0);
#endif
            for (int64_t i = 0; i < count; ++i) {
                State a = states[i * 2], b = states[i * 2 + 1];
                Impulses p = impulses[i];
                printf("STATE %lld %lld %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n",
                    (long long)pass, (long long)i, a.vx, a.vy, a.w, b.vx, b.vy, b.w,
                    p.normal, p.tangent, p.total, p.rolling);
            }
        }
    } else {
        run_kernel(states, count * 2, constraints, impulses, count, passes);
        double elapsed_ms = (seconds() - start) * 1000.0;
        double signature = 0.0;
        for (int64_t i = 0; i < count; ++i) {
            State a = states[i * 2], b = states[i * 2 + 1];
            Impulses p = impulses[i];
            signature += (double)(a.vx + a.vy * 2.0f + a.w * 3.0f +
                b.vx * 5.0f + b.vy * 7.0f + b.w * 11.0f + p.normal * 13.0f +
                p.tangent * 17.0f + p.total * 19.0f + p.rolling * 23.0f);
        }
        printf("KERNEL clang " LAYOUT " %lld %lld %.9f %.17g\n",
            (long long)count, (long long)passes, elapsed_ms, signature);
    }
    free(impulses);
    free(constraints);
    free(states);
    return 0;
}
