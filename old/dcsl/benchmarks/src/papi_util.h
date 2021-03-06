#ifndef PAPI_UTIL_H
#define PAPI_UTIL_H

#ifndef __cplusplus
#include <stdlib.h>
#include <stdio.h>
#endif

#define RUNNING         1
#define STOPPED         2
#define INITIALIZED     4

#ifdef __cplusplus
extern "C" {
#endif

typedef struct papi_counters {
    
    int n_counters;

    char **names;
    int *events;

    // Temp holding space for valus
    long long int *values;

    // Accumulated counter values
    double *accum;
    
    // Total accumulated time
    long long int elapsed_time;

    // Starting time
    long long int temp_time;

    int state;
} papi_counters_t;

int create_counters(papi_counters_t **counters, char **names, int *codes, int len);
int destroy_counters(papi_counters_t *counters);
int start_counters(papi_counters_t *counters);
int stop_counters(papi_counters_t *counters);
int accum_counters(papi_counters_t *counters);
int print_counters(papi_counters_t *counters);

#ifdef __cplusplus
}
#endif

#endif
