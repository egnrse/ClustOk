
from ctypes import sizeof
from functools import reduce
import logging
from optparse import Option
import yaml
from schema import Schema, SchemaError, Or, Optional

config_schema = Schema({
    "nodeLists": {
        object: {
            "nodeNames": str
        }
    },
    "tests": [
        Or({
            "name": str,
            "script": {
                "path": str
            },
            Optional("conditions"): 
                {
                    Optional("min"): int,
                    Optional("max"): int
                    
                }
        },
        {
            "name": str,
            "command": str,
            Optional("conditions"): 
                {
                    Optional("min"): int,
                    Optional("max"): int
                    
                }
        },
        {
            "name": str,
            "slurmScript": {
                "path": str,
                "nodeLists": str,
                Optional("options"): [
                    str
                ]
            },
            Optional("conditions"): 
                {
                    Optional("min"): int,
                    Optional("max"): int,
                    Optional("difference"): int
                    
                }
        },
        error="Test must be one of command, script, or slurmscript"
        )
    ],
    "settings": {
        "interval": int,
        "timeout": int,
        "slurmdir": str
    }
})


class Config:
    def __init__(self, logger: logging.Logger, config="/etc/clustOk/config.yml"):
        self.logger = logger
        with open(config) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
            self.validateConfig(config)

            self.tests = config['tests']
            self.interval = config['settings']['interval']
            self.nodeLists = config['nodeLists']
            self.timeout = config['settings']['timeout']
            self.slurmdir = config['settings']['slurmdir']

            self.logger.info("Found %d tests", len(self.tests))
        
    def parseNodeNames(self, nodeLists):
        lists = nodeLists.split(',')

        if len(lists) <= 1:
            return self.nodeLists[lists[0]]['nodeNames']
        
        return reduce(lambda a, b: self.nodeLists[a]['nodeNames'] + ',' + self.nodeLists[b]['nodeNames'], lists)

    def validateConfig(self, config): 
        try:
            config_schema.validate(config)
            self.logger.info('Configuration loaded sucessfully')

        except SchemaError as se:
            self.logger.error('Configuration is invalid. Exiting..')
            self.logger.error(se)
            exit(2)
