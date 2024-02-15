
import logging
from adf.core.data import Payload
from adf.core.base import ThreadProcess, BaseRunnable, get_runner_name
from adf.core.base import BaseCollector, BasePreparator, BaseProcessor, BaseReporter

log = logging.getLogger(__name__)


class Collector(ThreadProcess):

    def __init__(self, dc_obj: BaseCollector):
        name = get_runner_name(dc_obj)
        super(Collector, self).__init__(name)
        self.__collector = dc_obj

    def process(self):
        log.info('Data collection is in progress')
        
        while True:

            try:
                payload: Payload = self.__collector.extract_data()
                if not payload:
                    raise Exception('Payload not returned by callable process')
            except Exception as ex:
                payload: Payload = Payload()
                payload._stop_node = True
                log.error('Unable to collect data')
                log.exception(ex)

            # publish payload to linked nodes irrespective of exception
            self.publish_payload_to_connected_nodes(payload)

            # stop the loop if exception had occurred or stop_runner flag in payload is set to True
            if payload._stop_node or payload._stop_runner:
                break


class Preparator(BaseRunnable):

    def __init__(self, dp_obj: BasePreparator):
        super(Preparator, self).__init__(dp_obj)

    def execute(self, payload: Payload):
        executable: BasePreparator = self.get_callable_obj()
        return executable.prepare_data(payload)


class Processor(BaseRunnable):

    def __init__(self, dp_obj: BaseProcessor):
        super(Processor, self).__init__(dp_obj)

    def execute(self, payload: Payload):
        executable: BaseProcessor = self.get_callable_obj()
        return executable.process_data(payload)


class Reporter(BaseRunnable):

    def __init__(self, dp_obj: BaseReporter):
        super(Reporter, self).__init__(dp_obj)

    def execute(self, payload: Payload):
        executable: BaseReporter = self.get_callable_obj()
        return executable.generate_report(payload)
