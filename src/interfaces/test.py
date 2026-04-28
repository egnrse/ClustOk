from typing import Dict    


class Test:
    name: str
    descr: str
    conditions: Dict[str, int]
    noFail: bool
    maxDifference: int

class CommandTest(Test):
    command: str

class Script:
    path: str
class ScriptTest(Test):
    script: Script

class SlurmScript:
    path: str
    nodeLists: str
class SlurmScriptTest(Test):
    slurmScript: SlurmScript

class SlurmPairScript:
    pairSize: int
    path: str
    nodeLists: str
class SlurmScriptPairTest(Test):
    slurmPairScript: SlurmPairScript

# vim: set et ts=4 sw=4 sts=4:
