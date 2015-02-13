
import gevent.greenlet as greenlet
import gevent.subprocess as subprocess

class ApplicationBase():

    def __init__(self, start_cores, run_cores):
        self._run_cores = run_cores
        self._start_cores = start_cores
        
        self._loaded = False
        self._started = False

        self._application_dir = ""
        self._load_args = []
        self._start_args = []
        self._run_args = []
        self._stop_args = []
        self._cleanup_args = []

    def load(self):
        """ Load data ahead of any potential benchmark run """
        cmd = ["%s/load.sh" % (self._application_dir)]
        cmd = cmd + self._load_args
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        self._loaded = True

    # TODO, improve to use the with ... as ... idiom

    def start(self):
        """ Start and run the actual benchmark """
        if self._started or not self._loaded:
            # TODO, raise error here
            pass

        cores = ','.join(map(lambda x: str(x), self._start_cores))
        cmd = ['taskset', '-c', cores]
        cmd = cmd + ["%s/start.sh" % (self._application_dir)]
        cmd = cmd + self._start_args
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        self._started = True

    
    def run(self):
        if not self._started or not self._loaded:
            # TODO, raise error here
            pass
        return self._run()

    def stop(self):
        """ Stop and benchmark background operations """
        if not self._started:
            # TODO, raise error here
            pass

        cmd = ["%s/stop.sh" % (self._application_dir)]
        cmd = cmd + self._stop_args
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        self._started = False

    def cleanup(self):
        """ Perform any final cleanup needed """
        if self._loaded = False:
            # TODO, raise error here
            pass

        cmd = ["%s/cleanup.sh" % (self._appliation_dir)]
        cmd = cmd + self._cleanup_args
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        self._loaded = False

class Application(ApplicationBase):

    def __init__(self, start_cores=[0], run_cores=[0]):
        ApplicationBase.__init__(self, start_cores, run_cores])

    
    def __enter__(self):
        self._start()

    def __exit__(self):
        self._stop()
    
    def _run(self):
        """ Run the actual app which generates parseable output """
        cores = ','.join(map(lambda x: str(x), self._run_cores))
        cmd = ['taskset', '-c', cores]
        cmd = cmd + ["%s/run.sh" % (self._application_dir)]
        cmd = cmd + self._run_args
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        features = self._process_output(output)
        return features

    def _process_output(self, output):
        """ Process the textual output from the run.sh script """
        pass

class ApplicationInterfere(ApplicationBase):

    def __init__(self, start_cores=[0], run_cores=[0]):
        ApplicationBase.__init__(self, start_cores, run_cores)
        self._keep_running = True

    def stop(self):
        self._keep_running = False
        # TODO Join with background greenlet
        # TODO, call base class stop()

    def _run(self):
        cores = ','.join(map(lambda x: str(x), self._run_cores))
        cmd = ['taskset', '-c', cores]
        # TODO, set this up inside a greenlet