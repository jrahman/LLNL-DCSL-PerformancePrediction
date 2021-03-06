#include "papi_util.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
typedef char * caddr_t;
#include <papi.h>

/**
 * Create a given set of event counters
 */
int create_counters(struct papi_counters **counters, char **names, int *events, int len) {
    if (counters == NULL) {
        return -1;
    }

    if (names == NULL) {
        return -1;
    }

    if (events == NULL) {
        return -1;
    }

    *counters = (struct papi_counters*)malloc(sizeof(struct papi_counters));
    if (*counters == NULL) {
        return -1;
    }

    (*counters)->n_counters = len;
    (*counters)->events = NULL;
    (*counters)->accum = NULL;
    (*counters)->values = NULL;
    (*counters)->names = NULL;

    // Allocate and copy the names
    (*counters)->names = (char**)malloc(sizeof(char*)*(len+1));
    if ((*counters)->names == NULL) goto cleanup;
    for (int i = 0; i < len; i++) {
        (*counters)->names[i] = strdup(names[i]);
        if ((*counters)->names[i] == NULL) goto cleanup;
    }
    (*counters)->names[len] = NULL;

    // Allocate and copy the event codes
    (*counters)->events = (int*)malloc(sizeof(int) * len);
    if ((*counters)->events == NULL) goto cleanup;
    for (int i = 0; i < len; i++) {
        (*counters)->events[i] = events[i];
    }
    
    // Allocate the values array
    (*counters)->values = (long long int*)malloc(sizeof(long long int) * len);
    if ((*counters)->values == NULL) goto cleanup;


    // Allocate the accum array
    (*counters)->accum = (double*)malloc(sizeof(double) * len);
    if ((*counters)->accum == NULL) goto cleanup;
    
    for (int i = 0; i < len; i++) {
        (*counters)->accum[i] = 0.0;
    }

    (*counters)->elapsed_time = 0;
    (*counters)->temp_time = 0;
    (*counters)->state = INITIALIZED;
    return 0;

    cleanup:
    if ((*counters)->names) {
        for (int i = 0; i < len; i++) {
            free((*counters)->names[i]);
        }
        free((*counters)->names);
    }
    if ((*counters)->values) {
        free((*counters)->values);
    }
    if ((*counters)->accum) {
        free((*counters)->accum);
    }
    if ((*counters)->events) {
        free((*counters)->events);
    }
    if ((*counters)) {
        free(*counters);
        *counters = NULL;
    }
    return -1;
}

/**
 * Destroy a given set of event counters when done
 */
int destroy_counters(papi_counters_t *counters) {
    if (counters == NULL) {
        return -1;
    }

    int ret;
    if (counters->state == RUNNING) {
        ret = stop_counters(counters);
        if (ret != PAPI_OK) {
            return ret;
        }
        counters->state = STOPPED;
    }

    char **tmp = counters->names;
    while (*tmp) {
        free(*tmp);
        tmp++;
    }
    free(counters->names);
    free(counters->events);
    free(counters->values);
    free(counters->accum);
    free(counters);
    return 0;
}

/**
 * Start a given set of event counters
 */
int start_counters(papi_counters_t *counters) {
    if (counters == NULL) {
        return -1;
    }

    for (int i = 0; i < counters->n_counters; i++) {
        counters->values[i] = 0;
    }
    
    counters->temp_time = PAPI_get_virt_usec();

    int ret = PAPI_start_counters(counters->events, counters->n_counters);
    if (ret != PAPI_OK) {
        fprintf(stderr, "Failed to start PAPI counters, %d", ret);
        return ret;
    }

    counters->state = RUNNING;

    return 0;
}

/**
 * Accumulate the current counters
 * stopping the counters in the background
 * in the process
 */
int accum_counters(papi_counters_t *counters) {
    if (counters == NULL) {
        return -1;
    }

    if (counters->state != RUNNING) {
        return -1;
    }

    // Update the elapsed time
    long long int temp = PAPI_get_virt_usec();
    counters->elapsed_time += temp - counters->temp_time;
    counters->temp_time = temp;

    int ret;
    ret = PAPI_read_counters(counters->values, counters->n_counters);
    if (ret != PAPI_OK) goto end;

    for (int i = 0; i < counters->n_counters; i++) {
        counters->accum[i] += (double)counters->values[i];
        // Note, possible precision loss
    }

    ret = PAPI_stop_counters(counters->values, counters->n_counters);
    if (ret != PAPI_OK) goto end;

    counters->state = STOPPED;
end:
    return ret;
}

/**
 * Stop running the event counters
 */
int stop_counters(papi_counters_t *counters) {
    if (counters == NULL) {
        return -1;
    }

    if (counters->state != RUNNING) {
        return 0;
    }

    long long int temp = PAPI_get_virt_usec();
    counters->elapsed_time += temp - counters->temp_time;
    counters->temp_time = temp;

    int ret;
    ret = PAPI_stop_counters(counters->values, counters->n_counters);
    if (ret != PAPI_OK) {
        fprintf(stderr, "Failed to stop PAPI counters, %d", ret);
        return ret;
    }

    counters->state = STOPPED;

    return 0;
}

int print_counters(struct papi_counters *counters) {
    if (counters == NULL) {
        return -1;
    }

    if (counters->state == INITIALIZED) {
        return -1; // Not run yet, no meaningful data
    }

    for (int i = 0; i < counters->n_counters; i++) {
        fprintf(stdout, "%s: %f\n", counters->names[i], counters->accum[i]);
    }
    return 0;
}
