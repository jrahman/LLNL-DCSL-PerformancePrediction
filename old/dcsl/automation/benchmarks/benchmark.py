
import sys
import os
import logging
import gevent.subprocess as subprocess

class Benchmark:

    def __init__(self, environ, cores=[0]):
        self._cores = cores
        self._benchmark_dir = environ['benchmark_dir']
        self._data_dir = environ['data_dir']

    def __hash__(self):
        return hash(str(self))
    
    def __str__(self):
        return self._name

    def run(self):
        self._setup()
        cores = ','.join(map(lambda x: str(x), self._cores))

        cmd = ['taskset', '-c', cores, self._cmd]
        cmd = cmd + self._params
        features = {}

        logging.info('Starting benchmark %s', str(self))
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)    
            logging.info('Finished running benchmark %s', str(self))
            features = self._process_output(output)
        except subprocess.CalledProcessError as e:
            logging.exception('Benchmark failed: %s', e.output)
            self._teardown()
            raise
        except Exception as e:
            # Teardown for cleanup, then rethrow for capture somewhere else
            self._teardown()
            raise
        return features

    def _setup(self):
        pass

    def _teardown(self):
        pass

    def _process_output(self, output):
        pass

