// SPDX-License-Identifier: MIT
#pragma once
#include "TaskSystem.h"
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Shared by functional witnesses; numerical observations stay on stdout.
typedef struct OracleWorkers {
    OracleTaskSystem* tasks;
    int count;
} OracleWorkers;

static bool oracle_workers_open(OracleWorkers* workers, int argc, char** argv)
{
    workers->count = 1;
    if (argc > 2) return false;
    if (argc == 2)
    {
        if (strcmp(argv[1], "--workers-1") == 0) workers->count = 1;
        else if (strcmp(argv[1], "--workers-2") == 0) workers->count = 2;
        else if (strcmp(argv[1], "--workers-4") == 0) workers->count = 4;
        else return false;
    }
    workers->tasks = oracle_tasks_create(workers->count);
    return workers->tasks != NULL;
}

static int oracle_workers_close(OracleWorkers* workers)
{
    OracleTaskStats stats = oracle_tasks_stats(workers->tasks);
    fprintf(stderr, "ORACLE_TASKS workers=%d groups=%llu finished=%llu items=%llu completed=%llu mask=%u\n",
        workers->count, (unsigned long long)stats.enqueued_groups,
        (unsigned long long)stats.finished_groups, (unsigned long long)stats.submitted_items,
        (unsigned long long)stats.completed_items, stats.worker_mask);
    bool complete = stats.enqueued_groups > 0 && stats.submitted_items > 0 &&
        stats.enqueued_groups == stats.finished_groups && stats.submitted_items == stats.completed_items;
    oracle_tasks_destroy(workers->tasks);
    return complete ? 0 : 1;
}
