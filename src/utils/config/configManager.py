
from yaml import safe_load
from logging import Logger

from utils.config.config import Config, DictToConf
from utils.config.configSchema import config_schema

from schema import SchemaError

class ConfigManager(Config):
    def __init__(self, logger: Logger, config):
        self.logger = logger

        try:
            with open(config, 'r') as configFile:
                # Load an validate config
                config = safe_load(configFile)
                self.validateConfig(config)

                # Parse config as object for better typesafety
                self.config = DictToConf(config)

                self.logger.info("Found %d tests", len(self.config.tests))
        except FileNotFoundError as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Config file not found: '{config}'")
            exit(1)

    def validateConfig(self, config): 
        try:
            config_schema.validate(config, pass_error=True)
            self.logger.info('Configuration loaded sucessfully')

        except SchemaError as se:
            self.logger.error('Configuration is invalid. Exiting..')
            self.logger.error(se.code)
            self.logger.debug(se.autos)
            #self.logger.debug(se.errors)
            exit(2)
