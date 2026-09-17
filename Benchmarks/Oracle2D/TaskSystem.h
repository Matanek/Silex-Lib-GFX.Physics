// SPDX-License-Identifier: MIT
#pragma once
#include <box2d/box2d.h>
#include <stdint.h>

typedef struct OracleTaskSystem OracleTaskSystem;
typedef struct OracleTaskStats {
    uint64_t enqueued_groups;
    uint64_t finished_groups;
    uint64_t submitted_items;
    uint64_t completed_items;
    uint32_t worker_mask;
} OracleTaskStats;

// Benchmark-only persistent POSIX pool. The caller is worker zero.
OracleTaskSystem* oracle_tasks_create(int worker_count);
void oracle_tasks_destroy(OracleTaskSystem* system);
void oracle_tasks_configure(OracleTaskSystem* system, b2WorldDef* definition);
OracleTaskStats oracle_tasks_stats(OracleTaskSystem* system);
void* oracle_tasks_enqueue(b2TaskCallback* callback, int count, int min_range,
                          void* context, void* user_context);
void oracle_tasks_finish(void* task, void* user_context);
