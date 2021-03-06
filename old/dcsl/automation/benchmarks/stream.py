
from benchmark import Benchmark
from interference import Interference
import logging
import re

class StreamBenchmark(Benchmark):

    def __init__(self, environ, operation=1, cores=[0]):
        Benchmark.__init__(self, environ, cores)
        self._operation = operation
        self._cmd = self._benchmark_dir + '/stream'
        self._params = [str(operation)]
        self._name = "stream_" + self._bmark.lower()

    def _setup(self):
        pass

    def _teardown(self):
        pass

    def _process_output(self, output):
        regex = r"Function\W*Rate\W\(MB/s\)\W*Avg time\W*Min time\W*Max time\n%(bmark)s:\W*([0-9]+\.[0-9]*)\W*([0-9]+\.[0-9]*)\W*([0-9]+\.[0-9]*)\W*([0-9]+\.[0-9]*)" % {'bmark': self._bmark}
        result = re.search(regex, output)
        if result == None:
            logging.warning('Mismatch: %s', output)
            raise Exception('No match found')
        feature = {
                'bandwidth': float(result.group(1)),
                'avg_time': float(result.group(2)),
                'min_time': float(result.group(3)), 
                'max_time': float(result.group(4))
            }
        return feature

class StreamInterfereBase(Interference):
    
    def __init__(self, environ, operation=1, cores=[0], nice=0):
        Interference.__init__(self, environ, cores, nice)
        self._operation = operation
        self._params = [str(self._operation)]
        self._cmd = self._benchmark_dir + '/stream_interfere'
        self._name = 'stream_' + self._bmark.lower()

class Stream(Benchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = '' # Full stream suite
        Benchmark.__init__(self, environ, cores)
        self._params = ["0"]
        self._cmd = self._benchmark_dir + '/stream'
        self._name = "stream"

    def _setup(self):
       pass

    def _teardown(self):
       pass

    def _process_output(self, output):
       regex = r"%(bmark)s:\s*([0-9]+\.[0-9]*)\s*([0-9]+\.[0-9]*)\s*([0-9]+\.[0-9]*)\s*([0-9]+\.[0-9]*)"
       bandwidths = {}
       for operation in ["Copy", "Scale", "Add", "Triad"]:
           pattern = regex % {'bmark': operation}
           result = re.search(pattern, output)
           if result == None:
               logging.warning('Mismatch: %s', output)
               raise Exception('No match found')
           bandwidths[operation.lower()] = float(result.group(1))
       recip = map(lambda x: 1/x, bandwidths.values())
       denom = reduce(lambda x, y: x + y, recip, 0)
       harmonic_mean = len(bandwidths.values()) / denom
       features = {'bandwidth': harmonic_mean}
       features.update(bandwidths)
       return features

class StreamInterfere(StreamInterfereBase):
   def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
       self._bmark = ''
       StreamInterfereBase.__init__(self, environ, 0, cores, nice)

class StreamCopy(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Copy'
        StreamBenchmark.__init__(self, environ, 1, cores)

class StreamCopyInterfere(StreamInterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Copy'
        StreamInterfereBase.__init__(self, environ, 1, cores, nice)

class StreamScale(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Scale'
        StreamBenchmark.__init__(self, environ, 2, cores)

class StreamScaleInterfere(StreamInterfereBase):
    def __init__(self, enrivon, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Scale'
        StreamInterfereBase.__init__(self, environ, 2, cores, nice)

class StreamAdd(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Add'
        StreamBenchmark.__init__(self, environ, 3, cores)

class StreamAddInterfere(StreamInterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1): 
        self._bmark = 'Add'
        StreamInterfereBase.__init__(self, environ, 3, cores, nice)

class StreamTriad(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Triad'
        StreamBenchmark.__init__(self, environ, 4, cores)

class StreamTriadInterfere(StreamInterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Triad'
        StreamInterfereBase.__init__(self, environ, 4, cores, nice)

# Basic parsing unit test
if __name__ == "__main__":

    test = """-------------------------------------------------------------
STREAM version $Revision: 5.9 $
-------------------------------------------------------------
This system uses 8 bytes per DOUBLE PRECISION word.
-------------------------------------------------------------
Array size = 4000000, Offset = 0
Total memory required = 91.6 MB.
Each test is run 10 times, but only
the *best* time for each is used.
-------------------------------------------------------------
Printing one line per active thread....
-------------------------------------------------------------
Your clock granularity/precision appears to be 1 microseconds.
Each test below will take on the order of 6181 microseconds.
    (= 6181 clock ticks)
Increase the size of the arrays if this shows that
you are not getting at least 20 clock ticks per test.
-------------------------------------------------------------
WARNING -- The above is only a rough guideline.
For best results, please be sure you know the
precision of your system timer.
-------------------------------------------------------------
Function      Rate (MB/s)   Avg time     Min time     Max time
Copy:       11024.9489       0.0072       0.0058       0.0107
-------------------------------------------------------------
Failed Validation on array a[]
        Expected  : 4613203124999999488.000000 
        Observed  : 8000000.000000 
-------------------------------------------------------------
"""

    benchmark = StreamCopy({'benchmark_dir': '', 'data_dir': ''})
    output = benchmark._process_output(test)

    if not output['bandwidth'] == 11024.9489:
        exit(1)

    if not output['avg_time'] == 0.0072:
        exit(2)

    if not output['min_time'] == 0.0058:
        exit(3)

    if not output['max_time'] == 0.0107:
        exit(4)
    exit(0)
