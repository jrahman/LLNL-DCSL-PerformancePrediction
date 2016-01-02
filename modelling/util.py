#!/bin/env python

import pandas as pd
import numpy as np
import pickle

# interpolate.interp1d(x, y, kind=1)

def load_sensitivity_curves(filename):
    curves = None
    def copy_curve(curve):
        return lambda x: curve.predict([x])[0]
    def copy_percent(curve, base_value):
        return lambda x:  100 *(curve.predict([x])[0] - base_value) / base_value
    with open(filename, 'r') as f:
        curves = pickle.load(f)
    for qos_app in curves:
        for metric in curves[qos_app]:
            curve, base_value = curves[qos_app][metric]
            res = (copy_curve(curve), copy_percent(curve, base_value))
            curves[qos_app][metric] = res
    return curves

def read_experiment_list():
    experiments = []
    with open('completed_experiments', 'r') as f:
        for line in f:
            values = line.strip().split()
            experiment = {'apps': [], 'rep': values[-1], 'output': values[-2]}
            for i in range(int((len(values) - 2)/3)):
                experiment['apps'].append({
                    'suite': values[3*i],
                    'bmark': values[3*i+1],
                    'cores': values[3*i+2]
                })
            experiments.append(experiment)
    return experiments

def read_manifest():
    apps = []
    suites = ['parsec', 'spec_fp', 'spec_int']
    for suite in suites:
        with open('manifest/%(suite)s' % locals(), 'r') as f:
            for line in f:
                apps.append({'suite': suite, 'bmark': line.strip()}) 
    return apps  

def read_single_app_bubbles(filename):
    """
    Read the list of procesed bubble sizes 
    The format of the file is
    'mean median mean+std mean-std readable_name suite name cores'
    single_app_contention/process.sh generates this file from raw_data
    """
    means = dict()
    medians = dict()
    with open(filename, 'r') as f:
        for line in f:
            values = line.strip().split()
            bmark_suite = values[5]
            bmark_name = values[6]
            key = '_'.join([bmark_suite, bmark_name])
            means[key] = float(values[0])
            medians[key] = float(values[1])
    return means, medians

def parse_row(row):
    parsed = dict()
    parsed['mean_ipc'] = float(row[-4])
    parsed['median_ipc'] = float(row[-2])
    parsed['mean_bubble'] = float(row[-3])
    parsed['median_bubble'] = float(row[-1])
    rep = row[-5]
    parsed['rep'] = int(rep)
    apps = row[0:-5]
    app_list = []
    for i in range(int(len(apps) / 3)):
        suite = apps[3*i]
        bmark = apps[3*i + 1]
        
        if suite not in parsed:
            parsed[suite] = 0
        parsed[suite] += 1
        
        app = '_'.join([suite, bmark])
        if app not in parsed:
            parsed[app] = 0
        parsed[app] += 1

        app_list.append(app)

    parsed['apps'] = '.'.join(sorted(app_list))
    parsed['app_count'] = len(apps) / 3
    return parsed

def read_contention_data(filename):
    """
        Read multi-batch application experiment data from the file

        Format is
        '(suite bmark cores)+ rep mean_ipc mean_bubble median_ipc median_bubble' 
    """

    data = dict()
   
    # Read the line count ahead of time...
    lines = 0
    with open(filename, 'r') as f:
        for line in f:
            lines += 1

    apps = read_manifest()

    # Build empty dict will all required keys...
    app_count = 0

    data['apps'] = ['' for i in range(lines)]
    data['app_count'] = np.zeros(lines)
    data['mean_ipc'] = np.zeros(lines)
    data['median_ipc'] = np.zeros(lines)
    data['mean_bubble'] = np.zeros(lines)
    data['median_bubble'] = np.zeros(lines)
    data['rep'] = ['' for i in range(lines)]

    # Populate application counts
    apps = read_manifest()
    for app in apps:
        data[app['suite'] + '_' + app['bmark']] = [0 for i in range(lines)]
    for suite in set([item['suite'] for item in apps]):
        data[suite] = [0 for i in range(lines)]

    with open(filename, 'r') as f:
        idx = 0
        for line in f:
            row = parse_row(line.strip().split())
            for key, value in row.items():
                data[key][idx] = value
            idx += 1

    dataframe = pd.DataFrame()
    for key, value in data.items():
        dataframe[key] = value
    return dataframe

def apps_to_experiment_name(apps, rep):
    output = '.'.join(["%s_%s_%s" % (app['suite'], app['bmark'], app['cores']) for app in apps])
    output = str(len(apps)) + '_' + output + '_' + str(rep)
    return output

if __name__ == '__main__':
    pass
