from yaml import safe_load
from schema import SchemaError

from typing import Dict, Any
from logging import Logger
from utils.config.config import Config, DictToConf

from utils.config.configSchema import config_schema
from utils.config.defaults import DEFAULTS


class ConfigManager(Config):
    def __init__(self, logger: Logger, configPath: str):
        self.logger = logger

        try:
            with open(configPath, 'r') as configFile:
                # Load an validate config
                config: Dict[str, Any] = safe_load(configFile)
                self.validateConfig(config)
                self.applyDefaults(config)

                # Parse config as object for better typesafety
                self.config = DictToConf(config)

                self.logger.info("Found %d tests", len(self.config.tests))
        except FileNotFoundError as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Config file not found: '{configPath}'")
            exit(1)

    def applyDefaults(self, config: Dict[str, Any], defaults: dict[str, Any] = DEFAULTS) -> None:
        for key, value in defaults.items():
            if isinstance(value, dict):
                config.setdefault(key, {})
                self.applyDefaults(config[key], value)
            else:
                config.setdefault(key, value)

    def validateConfig(self, config: Dict[str, Any]) -> None: 
        try:
            config_schema.validate(config, pass_error=True) # type: ignore[arg-type]
            self.logger.info('Configuration loaded sucessfully')

        except SchemaError as se:
            self.logger.error('Configuration is invalid. Exiting..')
            self.logger.error(se.code)
            self.logger.debug(se.autos)
            #self.logger.debug(se.errors)
            exit(2)

# vim: set et ts=4 sw=4 sts=4:
