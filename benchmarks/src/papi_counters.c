#include "papi_counters.h"

papi_counters_t *get_miss_counters() {
    
    int events[] = {PAPI_L1_TCA, PAPI_L1_TCM, PAPI_L2_TCA, PAPI_L2_TCM, PAPI_L3_TCA, PAPI_L3_TCM};
    char *names[] = {"L1 Accesses", "L1 Misses", "L2 Accesses", "L2 Misses", "L3 Accesses", "L3 Misses"};
    
    papi_counters_t *counters;
    if (create_counters(&counters, names, events, sizeof(events)/sizeof(events[0])) != 0) {
        return NULL;
    }

    return counters;
}
