
import abc
import time
import queue
import logging
import threading
from adf.core.data import Payload

log = logging.getLogger(__name__)


def get_runner_name(obj):
    name = obj.name if hasattr(obj, 'name') else None
    return name or obj.__class__.__name__


class ThreadProcess(threading.Thread):

    _objects = []
    _callable = True

    def __init__(self, name):
        super(ThreadProcess, self).__init__()
        self.name = name
        self._queue = queue.Queue()

    def run(self):
        log.info('Starting {} thread.'.format(self.name))
        self.process()
        log.info('Exiting {} thread.'.format(self.name))

    def stop(self):
        self.join()
        self._callable = False

    @staticmethod
    def _insert(target_object: object, data: object):
        target_object._queue.put(data)

    def _get(self):
        if not self._queue.empty():
            return self._queue.get()

    def link_nodes(self, objects: list):
        self._objects = objects

    def next_node(self):
        return self._objects

    def publish_payload_to_connected_nodes(self, payload: Payload):
        if payload and self._objects:
            log.info('Publishing payload to connected nodes')
            for obj in self._objects:
                self._insert(obj, payload)

    def get_payload_from_queue(self):
        return self._get()

    def is_running(self):
        return self._callable

    def is_allowed_to_run(self):
        return self._callable

    def __str__(self):
        return self.name

    def get_all_objects(self):
        return self._objects

    @staticmethod
    def sleep(secs: float):
        time.sleep(secs)

    @abc.abstractmethod
    def process(self):
        pass


class BaseCallable:
    # Anything that returns some value is Callable.
    def __init__(self, name):
        self.name = name
        self.payload = Payload()
        self._callable = True

    def continue_runner(self):
        self.payload._stop_runner = False

    def stop_runnable_process(self):
        log.debug(self.name+' Peacefully exiting continuous process')
        self._callable = False

    def is_allowed_to_call(self):
        return self._callable


class BaseCollector(BaseCallable):

    def __init__(self, name):
        super(BaseCollector, self).__init__(name)

    @abc.abstractmethod
    def extract_data(self, *args, **kwargs):
        pass


class BasePreparator:

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def prepare_data(self, payload: Payload):
        pass


class BaseProcessor:

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def process_data(self, payload: Payload):
        pass


class BaseReporter:

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def generate_report(self, payload: Payload):
        pass


class BaseRunnable(ThreadProcess):

    def __init__(self, callable_obj):
        name = get_runner_name(callable_obj)
        super(BaseRunnable, self).__init__(name)
        self.__callable_obj = callable_obj

    def get_callable_obj(self):
        return self.__callable_obj

    @abc.abstractmethod
    def execute(self, payload: Payload):
        pass

    def process(self):

        while True:
            payload: Payload = self.get_payload_from_queue()
            if payload:
                # Check if previous node had asked to stop this node
                if not payload._stop_node:
                    try:
                        payload: Payload = self.execute(payload=payload)
                        if not payload:
                            raise Exception('Payload not returned by callable process')
                    except Exception as ex:
                        # Flag to stop this runner process and all linked nodes
                        payload._stop_node = True
                        log.error('Exception Occurred!')
                        log.exception(ex)

                    # publish payload to linked nodes irrespective of exception
                    self.publish_payload_to_connected_nodes(payload)

                    # stop the loop if exception had occurred or stop_runner flag in payload is set to True
                    if payload._stop_node or payload._stop_runner:
                        break
                else:
                    break

            self.sleep(5)
