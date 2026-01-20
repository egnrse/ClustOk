from logging import INFO, DEBUG, CRITICAL, ERROR, WARN
from typing import List, Dict

from interfaces.test import Test

class OutputSettings:
    fileName: str
    dir: str
    format: str

class SlurmSettings:
    dir: str
    partition: str
    args: List[str]
    
class NodeLists:
    nodenames: str

class LoggingSettings:
    dir: str
    level: INFO | DEBUG | CRITICAL | ERROR | WARN

class PrometheusSettings:
    port: int
    enable: bool

class Settings:
    interval: int
    timeout: int
    slurm: SlurmSettings
    prometheus: PrometheusSettings
    output: OutputSettings

class Config:
    logging: LoggingSettings
    settings: Settings
    nodeLists: Dict[str, NodeLists]
    tests: List[Test]

class DictToConf(Config):
    def __init__(self, in_dict:dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictToConf(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictToConf(val) if isinstance(val, dict) else val)

    def __str__(self) -> str:
        res = "{"
        for property, value in vars(self).items():
            item = property + ":" + str(value)
            res += item + ","

        res += "}"

        return res

