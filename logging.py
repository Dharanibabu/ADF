
import os
import mlflow
import logging
import logging.config
from os.path import isdir, isfile, exists, join
from adf.utils import LOGGER_CONFIG_FILE, read_yaml_config


class AutoDFLogger:

    def __init__(self, name):
        self.log = logging.getLogger(name)

    def info(self, msg, *args, **kwargs):
        self.log.info(self.build_log(msg, *args, **kwargs))
        self._track_metric(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log.error(self.build_log(msg, *args, **kwargs))
        self._track_metric(msg, *args, **kwargs)

    def exception(self, msg):
        self.log.exception(msg)

    @classmethod
    def init_logger(cls, config_path: str=LOGGER_CONFIG_FILE, level=logging.DEBUG, log_dir='/var/log/adf/'):
        if exists(config_path):
            log_config = read_yaml_config(config_path)
            log_file_name = log_config['handlers']['file_handler']['filename']
            log_file_path = join(log_dir, log_file_name)
            log_config['handlers']['file_handler']['filename'] = log_file_path
            if not exists(log_dir):
                os.makedirs(log_dir)
            logging.config.dictConfig(log_config)
        else:
            logging.basicConfig(level=level)

    @staticmethod
    def build_log(msg, *args, **kwargs):
        log_msg = msg
        if args:
            log_msg += ' '+str(args)
        if kwargs:
            log_msg += ' '+str(kwargs)
        return log_msg

    def _track_metric(self, key, *args, **kwargs):
        self.log.debug(str(key)+', args='+str(len(args))+', kwargs='+str(len(kwargs)))
        if type(key) is str and isdir(key):
            mlflow.log_artifacts(key)
        elif type(key) is str and isfile(key):
            mlflow.log_artifact(key)
        elif len(args) == 2 or 'step' in kwargs:
            step = args[1] if len(args) == 2 else kwargs.get('step')
            mlflow.log_metric(key, int(args[0]), step=step)
        elif len(args) == 1:
            mlflow.log_param(key, args[0])
