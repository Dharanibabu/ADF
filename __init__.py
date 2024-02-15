
import logging

log = logging.getLogger(__name__)

class Pipeline:
    
    def __init__(self, name: str):
        self.name = name
        self.stages = []
    
    def compose(self, stages: list):
        self.stages = stages
    
    def execute(self):
        try:
            
            log.info('Executing {} pipeline'.format(self.name))
            for stage in self.stages[::-1]:
                stage.start()
        
            for stage in self.stages:
                stage.stop()
                
        except Exception as ex:
            log.error('{} pipeline failed due to unexpected exception!'.format(self.name))
            log.exception(ex)
