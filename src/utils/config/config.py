from typing import List, Dict, Any
from interfaces.test import Test


class SlurmSettings:
    dir: str
    partition: str
    args: List[str]
    
class NodeLists:
    nodenames: str

class LoggingSettings:
    dir: str
    level: int

class FileSettings:
    fileName: str
    dir: str
    format: str

class PrometheusSettings:
    port: int
    enable: bool

class OutputSettings:
    file: FileSettings
    console: bool
    prometheus: PrometheusSettings

class Settings:
    interval: int
    timeout: int
    slurm: SlurmSettings
    output: OutputSettings
    logging: LoggingSettings

class Config:
    settings: Settings
    nodeLists: Dict[str, NodeLists]
    tests: List[Test]

class DictToConf(Config):
    def __init__(self, in_dict:Dict[str, Any]):
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

# vim: set et ts=4 sw=4 sts=4:
