// SPDX-License-Identifier: MIT
#include "TaskSystem.h"
#include <stdatomic.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct Check {
    int workers, count, min_range;
    bool barrier;
    atomic_int arrived;
    atomic_int active[4];
    atomic_int seen[4097];
} Check;
static void require(bool ok) { if (!ok) abort(); }
static void callback(int start, int end, uint32_t worker, void* context) {
    Check* check = context;
    require(worker < (uint32_t)check->workers && start >= 0 && start < end && end <= check->count);
    require(end - start >= check->min_range || check->count < check->min_range);
    require(atomic_exchange(&check->active[worker], 1) == 0);
    if (check->barrier) {
        atomic_fetch_add(&check->arrived, 1);
        while (atomic_load(&check->arrived) < check->workers) {
            struct timespec pause = {.tv_nsec = 100000}; nanosleep(&pause, NULL);
        }
    }
    for (int i = start; i < end; ++i) require(atomic_fetch_add(&check->seen[i], 1) == 0);
    require(atomic_exchange(&check->active[worker], 0) == 1);
}
int main(void) {
    for (int workers = 1; workers <= 4; workers *= 2) {
        OracleTaskSystem* system = oracle_tasks_create(workers);
        require(oracle_tasks_enqueue(callback, 0, 1, NULL, system) == NULL);
        Check barrier = {.workers = workers, .count = workers, .min_range = 1, .barrier = true};
        void* task = oracle_tasks_enqueue(callback, workers, 1, &barrier, system);
        oracle_tasks_finish(task, system);
        require(oracle_tasks_stats(system).worker_mask == (uint32_t)((1 << workers) - 1));
        const int counts[] = {1, 3, 7, 32, 255, 4095, 4096, 4097};
        for (int round = 0; round < 10; ++round) {
            Check checks[8] = {0}; void* tasks[8];
            for (int i = 0; i < 8; ++i) {
                checks[i].workers = workers; checks[i].count = counts[i];
                checks[i].min_range = round + 1;
                tasks[i] = oracle_tasks_enqueue(callback, counts[i], round + 1, &checks[i], system);
            }
            // Finish in reverse order to exercise simultaneous contexts and helping.
            for (int i = 7; i >= 0; --i) {
                oracle_tasks_finish(tasks[i], system);
                for (int j = 0; j < counts[i]; ++j) require(atomic_load(&checks[i].seen[j]) == 1);
            }
        }
        OracleTaskStats stats = oracle_tasks_stats(system);
        require(stats.enqueued_groups == stats.finished_groups && stats.submitted_items == stats.completed_items);
        printf("workers=%d groups=%llu items=%llu mask=%u complete\n", workers,
               (unsigned long long)stats.finished_groups, (unsigned long long)stats.completed_items, stats.worker_mask);
        oracle_tasks_destroy(system);
    }
}
