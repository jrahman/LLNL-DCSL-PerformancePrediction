#!/bin/env python

import itertools
import sys

def read_applications(cores):
    suites = ['spec_fp', 'spec_int', 'parsec']
    applications = []
    for suite in suites:
        path = 'manifest/%(suite)s' % locals()
        if suite == 'parsec':
            app_cores = cores
        else:
            app_cores = 1
        with open(path, 'r') as f:
            for line in f:
                applications.append([suite, line.strip(), str(app_cores)])
    return applications

def create_output_path(combination, rep):
    path = 'data/' + str(len(combination)) + '_' + '.'.join([ "_".join(app) for app in combination])
    path += '.%(rep)d.reporter.perf_counters' % locals()
    return path

def main(reps, cores, maxapps):
    applications = read_applications(cores)
    for app_count in range(2, maxapps + 1):
        for combination in itertools.combinations(applications, app_count):
            combo = " ".join([" ".join(app) for app in combination])
            for rep in range(reps):
                output = create_output_path(combination, rep)
                print('%(combo)s %(output)s %(rep)d' % locals())
#
# Parameters: create_experiments.py REPS CORES MAXAPPS
#

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Error: Invalid number of parameters")
        print("create_experiments.py REPS CORES MAXAPPS")
        sys.exit(1)
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
