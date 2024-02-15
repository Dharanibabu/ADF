
import yaml
from os.path import join, dirname
from jinja2 import Environment, FileSystemLoader

SRC_ROOT = dirname(__file__)
LIB_ROOT = dirname(SRC_ROOT)
LOGGER_CONFIG_FILE = join(SRC_ROOT, 'logger.yml')
USE_CASE_TEMPLATES_DIR = join(LIB_ROOT, 'bundle')

jinja_env = Environment(loader=FileSystemLoader(USE_CASE_TEMPLATES_DIR))


def read_yaml_config(config_path: str):
    """
    Method to read yaml config file. By default it reads generic config file
    :param config_path: path of the yaml file
    :return: dict - containing configs defined in file
    """
    with open(config_path, 'r') as config:
        return yaml.safe_load(config.read())

