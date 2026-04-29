from typing import Dict, List


class Test:
    name: str
    descr: str
    conditions: Dict[str, int]

class CommandTest(Test):
    command: str

class Script:
    path: str
class ScriptTest(Test):
    script: Script

class SlurmScript:
    path: str
    nodeLists: str
    options: List[str]
class SlurmScriptTest(Test):
    slurmScript: SlurmScript

class SlurmPairScript(SlurmScript):
    pairSize: int
class SlurmScriptPairTest(Test):
    slurmPairScript: SlurmPairScript

# vim: set et ts=4 sw=4 sts=4:
