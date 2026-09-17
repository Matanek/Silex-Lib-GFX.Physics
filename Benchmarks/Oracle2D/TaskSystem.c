// SPDX-License-Identifier: MIT
#include "TaskSystem.h"
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

enum { max_workers = 4, max_groups = 256, queue_capacity = max_groups * max_workers };
typedef struct Group {
    bool used;
    int remaining;
    b2TaskCallback* callback;
    void* context;
} Group;
typedef struct Work { Group* group; int start; int end; } Work;
typedef struct Worker { OracleTaskSystem* system; uint32_t index; pthread_t thread; } Worker;
struct OracleTaskSystem {
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t changed;
    bool stopping;
    Group groups[max_groups];
    Work queue[queue_capacity];
    int head;
    int size;
    Worker workers[max_workers - 1];
    OracleTaskStats stats;
};
static void require(bool condition) {
    if (!condition) { fputs("oracle task-system invariant failed\n", stderr); abort(); }
}
static void lock(OracleTaskSystem* s) { require(pthread_mutex_lock(&s->mutex) == 0); }
static void unlock(OracleTaskSystem* s) { require(pthread_mutex_unlock(&s->mutex) == 0); }
static Work pop(OracleTaskSystem* s) {
    require(s->size > 0);
    Work w = s->queue[s->head];
    s->head = (s->head + 1) % queue_capacity;
    --s->size;
    return w;
}
// Enter and return with the mutex held. Context lives until the last callback returns.
static void execute(OracleTaskSystem* s, Work w, uint32_t index) {
    unlock(s);
    w.group->callback(w.start, w.end, index, w.group->context);
    lock(s);
    require(w.group->used && w.group->remaining > 0);
    --w.group->remaining;
    s->stats.completed_items += (uint64_t)(w.end - w.start);
    s->stats.worker_mask |= 1u << index;
    require(pthread_cond_broadcast(&s->changed) == 0);
}
static void* worker_main(void* value) {
    Worker* worker = value;
    OracleTaskSystem* s = worker->system;
    lock(s);
    for (;;) {
        while (s->size == 0 && !s->stopping)
            require(pthread_cond_wait(&s->changed, &s->mutex) == 0);
        if (s->stopping) { require(s->size == 0); break; }
        execute(s, pop(s), worker->index);
    }
    unlock(s);
    return NULL;
}
OracleTaskSystem* oracle_tasks_create(int count) {
    require(count >= 1 && count <= max_workers);
    OracleTaskSystem* s = calloc(1, sizeof(*s));
    require(s != NULL);
    s->count = count;
    require(pthread_mutex_init(&s->mutex, NULL) == 0);
    require(pthread_cond_init(&s->changed, NULL) == 0);
    for (int i = 1; i < count; ++i) {
        Worker* worker = &s->workers[i - 1];
        worker->system = s; worker->index = (uint32_t)i;
        require(pthread_create(&worker->thread, NULL, worker_main, worker) == 0);
    }
    return s;
}
void oracle_tasks_destroy(OracleTaskSystem* s) {
    lock(s);
    require(s->size == 0);
    for (int i = 0; i < max_groups; ++i) require(!s->groups[i].used);
    require(s->stats.enqueued_groups == s->stats.finished_groups);
    require(s->stats.submitted_items == s->stats.completed_items);
    s->stopping = true;
    require(pthread_cond_broadcast(&s->changed) == 0);
    unlock(s);
    for (int i = 1; i < s->count; ++i) require(pthread_join(s->workers[i - 1].thread, NULL) == 0);
    require(pthread_cond_destroy(&s->changed) == 0);
    require(pthread_mutex_destroy(&s->mutex) == 0);
    free(s);
}
void* oracle_tasks_enqueue(b2TaskCallback* callback, int count, int min_range,
                          void* context, void* user_context) {
    OracleTaskSystem* s = user_context;
    require(callback != NULL && count >= 0 && min_range > 0);
    if (count == 0) return NULL;
    int chunks = count / min_range;
    if (chunks < 1) chunks = 1;
    if (chunks > s->count) chunks = s->count;
    lock(s);
    Group* group = NULL;
    for (int i = 0; i < max_groups; ++i) {
        if (!s->groups[i].used) { group = &s->groups[i]; break; }
    }
    require(group != NULL && s->size + chunks <= queue_capacity);
    *group = (Group){.used = true, .remaining = chunks, .callback = callback, .context = context};
    for (int i = 0; i < chunks; ++i) {
        int start = (int)((int64_t)count * i / chunks);
        int end = (int)((int64_t)count * (i + 1) / chunks);
        s->queue[(s->head + s->size) % queue_capacity] = (Work){group, start, end};
        ++s->size;
    }
    ++s->stats.enqueued_groups;
    s->stats.submitted_items += (uint64_t)count;
    require(pthread_cond_broadcast(&s->changed) == 0);
    unlock(s);
    return group;
}
void oracle_tasks_finish(void* task, void* user_context) {
    OracleTaskSystem* s = user_context;
    Group* group = task;
    lock(s);
    require(group != NULL && group->used);
    while (group->remaining != 0) {
        if (s->size > 0) execute(s, pop(s), 0);
        else require(pthread_cond_wait(&s->changed, &s->mutex) == 0);
    }
    group->used = false;
    ++s->stats.finished_groups;
    unlock(s);
}
OracleTaskStats oracle_tasks_stats(OracleTaskSystem* s) {
    lock(s);
    OracleTaskStats stats = s->stats;
    unlock(s);
    return stats;
}
void oracle_tasks_configure(OracleTaskSystem* s, b2WorldDef* definition) {
    definition->workerCount = s->count;
    definition->enqueueTask = oracle_tasks_enqueue;
    definition->finishTask = oracle_tasks_finish;
    definition->userTaskContext = s;
}
