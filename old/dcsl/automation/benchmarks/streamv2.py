from stream import StreamBenchmark, StreamInterfereBase
import logging

# Use the non-optimized version
class StreamV2Benchmark(StreamBenchmark):
    def __init__(self, environ, operation=1, cores=[0]):
        StreamBenchmark.__init__(self, environ, operation, cores)
        self._cmd = self._benchmark_dir + '/streamV2_interfere'
        self._name = 'streamV2_' + self._bmark

# Use the non-optimized version
class StreamV2InterfereBase(StreamInterfereBase):
    def __init__(self, environ, operation=1, cores=[0], nice=0):
        StreamInterfereBase.__init__(self, environ, operation, cores, nice)
        self._cmd = self._benchmark_dir + '/streamV2_interfere'
        self._name = 'streamV2_' + self._bmark

# V2 benchmarks are non-optimized (slow)
class StreamV2Copy(StreamV2Benchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Copy'
        StreamBenchmark.__init__(self, environ, 1, cores)

class StreamV2CopyInterfere(StreamV2InterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Copy'
        StreamV2InterfereBase.__init__(self, environ, 1, cores, nice)

class StreamV2Scale(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Scale'
        StreamBenchmark.__init__(self, environ, 2, cores)

class StreamV2ScaleInterfere(StreamV2InterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Scale'
        StreamV2InterfereBase.__init__(self, environ, 2, cores, nice)

class StreamV2Add(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Add'
        StreamBenchmark.__init__(self, environ, 3, cores)

class StreamV2AddInterfere(StreamV2InterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1): 
        self._bmark = 'Add'
        StreamV2InterfereBase.__init__(self, environ, 3, cores, nice)

class StreamV2Triad(StreamBenchmark):
    def __init__(self, environ, cores=[0], instance=1):
        self._bmark = 'Triad'
        StreamBenchmark.__init__(self, environ, 4, cores)

class StreamV2TriadInterfere(StreamV2InterfereBase):
    def __init__(self, environ, cores=[0], extra_cores=[1], nice=0, instance=1):
        self._bmark = 'Triad'
        StreamV2InterfereBase.__init__(self, environ, 4, cores, nice)

