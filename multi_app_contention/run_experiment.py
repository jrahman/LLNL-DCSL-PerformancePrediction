#!/bin/env python

import os
import sys
import subprocess
import logging
import threading
import functools

import json
import requests

def ensure_data_dir():
    # Ensure that the data directory is created
    subprocess.check_call(['mkdir', '-p', 'data'])

def self_pin(core):
    # Pin the python process to another socket to ensure
    # that this process doesn't interfere with the measurement
    cmd = ['taskset', '-p', '-c', str(core), str(os.getpid())]
    subprocess.check_call(cmd)

def base_command(cores, numa_node):
    return ['setsid', 'taskset', '-c', ','.join(map(lambda s: str(s), cores)), 'numactl', '-m', str(numa_node)]

def kill_process_group(proc):
    if proc.poll() is None:
        pid = proc.pid
        pgroup = int(subprocess.check_output('ps -o pgid= %(pid)s' % locals(), shell=True).decode('utf-8').strip())
        logging.info('Killing process group: %(pgroup)s' % locals())
        subprocess.check_call('kill -9 -%(pgroup)s' % locals(), shell=True)

procs = dict()
lock = threading.Lock()

def run_thread(func):
    """
    Decorator to run a function inside it's own thread
    Its assumed the function will return a Process object back
    """
    def wrapper(slot, bmark, cores):
        with lock:
            procs[slot] = None
        def run():
            global procs
            while True:
                proc = None
                with lock:
                    procs[slot] = func(bmark, cores)
                    proc = procs[slot]
                retcode = proc.wait()
                logging.info('%(bmark)s finished' % locals())
                with lock:
                    procs[slot] = None
                # retcode == 0 indicates normal termination of the batch process
                # while retcode==9 indicates that it was killed intentionally
                if retcode != 0 and retcode != -9:
                    raise Exception('Non-zero return code: %(retcode)d' % locals())
                if update_count(slot) == False:
                    # Finished running, kill all other running procs since
                    # update_count() has indicated that each process has
                    # fully run at least one time
                    with lock:
                        logging.info('Killing extra procs')
                        for key in procs:
                            if procs[key] is not None:
                                try:
                                    kill_process_group(procs[key])
                                except Exception as e:
                                    logging.exception("Failed to kill proc")
                    break
        thread = threading.Thread(target=run)
        logging.info('Starting thread for %(bmark)s' % locals())
        thread.start()
        return thread
    return wrapper

@run_thread
def run_spec(bmark, cores):
    cmd = base_command(cores, 0)
    cmd += ['runspec', '--nobuild', '--config', 'research_config', '--action', 'onlyrun', '--size', 'ref', bmark]
    logging.info('Starting %(bmark)s' % locals())
    return subprocess.Popen(cmd)

@run_thread
def run_parsec(bmark, cores):
    core_count = len(cores)
    cmd = base_command(cores, 0)
    cmd += ['parsecmgmt', '-a', 'run', '-i', 'native', '-n', str(core_count), '-p', bmark]
    logging.info('Starting %(bmark)s' % locals())
    return subprocess.Popen(cmd)

def run_reporter(output_path, pid_file, cores):
    logging.info('Starting reporter...')
    cores = ",".join(map(lambda s: str(s), cores))
    cmd = '../bin/time 2> "%(output_path)s" ' % locals()
    cmd += '| 3>>"%(output_path)s" taskset -c %(cores)s numactl -m 0 ' % locals()  # subrata cores => comma seperated list of cores
    cmd += '/usr/bin/perf stat -I 1000 -D 15000 -e cycles,instructions --append --log-fd=3 -x " " '
    cmd += '../bin/reporter 1> %(pid_file)s' % locals() #subrata : call the script that would run the interactive application. Before running "run_reporter" prepare mongoDB by loading it and shutdown . and call script shoud start it
    return subprocess.Popen(cmd, shell=True)

# List containing completion counts for the ith process
run_counts = []

def update_count(slot):
    """
    Update the counts for a given process and determine if all processes
    finished at least once, in which case we actually return false
    """
    global run_counts
    global lock
    with lock:
        run_counts[slot] += 1
        return functools.reduce(lambda x, y: x*y, run_counts, 1) == 0

def add_slot():
    """
    Add a new slot for another batch application
    """
    global run_counts
    run_counts.append(0)
    return len(run_counts) - 1

# Application format is '(suite bmark cores)+ output_path rep'
def run_experiment(params, output_path, rep):
    "(suite bmark #cores)+"
    applications = []                            # subrata need to save the benchmark results in a file. and pass the name of that file here
    for i in range(int((len(params) - 2) / 3)):  # subrata : parsing of the already created experiment list generated by "create_experiment.py"
        suite = params[3 * i]
        bmark = params[1 + 3 * i]
        cores = int(params[2 + 3 * i])
        applications.append([suite, bmark, cores])
    
    logging.info('Starting experiment with %d applications' % (len(applications)))

    # Cab contains 8 cores per SMP
    reporter_core = 0    #subrata : reporter will be replaced by mongodB (interactive) => use two cores. YCSB will be in the other socket 2 cores anything between (8-15)
    starting_core = 1
    ending_core = 7
    current_core = 1
    core_allocations = []
    for application in applications:
        cores = int(application[2])
        if current_core + cores - 1 <= ending_core:
            core_allocations.append(list(range(current_core, current_core + cores)))
            current_core += cores # This is appearently important...
        else:
            # TODO, error
            pass

    # Pin ourself to the other socket
    self_pin(ending_core+1)   # subrata : self pining of "this" python driver. similarly pin the benchmark driver YCSB/ apache bench etc. Pin tghem on the other socket to reduce intf
    ensure_data_dir()

    experiment = ".".join(['%(suite)s_%(bmark)s_%(cores)d' % locals() for suite, bmark, cores in applications])
    pid_file = './logs/%(experiment)s.%(rep)d.reporter.pid' % locals()    

    reporter = None
    try:
        reporter = run_reporter(output_path, pid_file, [reporter_core]) 
    except Exception as e:
        logging.exception("Error: Failed to start reporter")
        sys.exit(1)

    threads = []

    # Launch applications...
    for i in range(len(applications)):
        application = applications[i]
        cores = core_allocations[i]
        suite = application[0]
        bmark = application[1]
        if suite == 'parsec':
            # Notice that the parameters here reflect the def wrapper() function in the decorator
            threads.append(run_parsec(add_slot(), bmark, cores))
        elif suite == 'spec_fp' or suite == 'spec_int':
            threads.append(run_spec(add_slot(), bmark, cores))
        else:
            raise Exception('Bad suite: %(suite)s' % locals())

    # Wait for all worker threads to finish
    for thread in threads:
        thread.join()

    subprocess.check_call('/bin/kill `/bin/cat %(pid_file)s`' % locals(), shell=True)

def send_request(host, port, endpoint, method='GET', body=None):
    url = 'http://%(host)s:%(port)d/%(endpoint)s' % locals()
    logging.info('Sending to url "%(url)s"' % locals())
    if method == 'GET':
        return requests.get(url).text
    else:
        return requests.post(url, data=body).text

def get_experiment(host, port):
    return send_request(host, port, 'get_experiment')    

def send_success(host, port, experiment):
    body = {'experiment': experiment, 'success': True}
    send_request(host, port, 'return_experiment', 'POST', json.dumps(body))

def send_failure(host, port, experiment, message):
    body = {'experiment': experiment, 'success': False, 'message': message}
    send_request(host, port, 'return_experiment', 'POST', json.dumps(body))

def run_slave(host, port):
    # Run as a slave worker on a node
    keep_running = True
    while keep_running:
        keep_running = False
        logging.info('Getting experiment...')
        experiment = get_experiment(host, port)
        try:
            parsed_experiment = experiment.split()
            size = len(parsed_experiment)
            logging.info('Retrieved experiment: %(experiment)s with %(size)d entries' % locals())
            run_experiment(parsed_experiment, parsed_experiment[-2], int(parsed_experiment[-1]))
            send_success(host, port, experiment)
            keep_running = True
        except Exception as e:
            logging.info('Failed experiment: %(experiment)s' % locals())
            logging.exception('Error: %s' % str(e))
            send_failure(host, port, experiment, str(e))

if __name__ == '__main__':
   
    logging.basicConfig(level=logging.DEBUG)
     
    # Two parameters for the rep and the name of the program
    # All others are 3*i where i is the number of batch applications
    if len(sys.argv) == 3:
        # Host and port of the master...
       run_slave(sys.argv[1], int(sys.argv[2]))
    elif (len(sys.argv) - 3) % 3 == 0:
        # Parameters given on the command line
        run_experiment(sys.argv[1:], sys.argv[-2], int(sys.argv[-1]))
    else:
        print('Error: Invalid parameters')
        sys.exit(1)
