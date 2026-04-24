from typing import Dict    


class Test:
    noFail: bool
    maxDifference: int
    descr: str
    name: str
    conditions: Dict[str, int]

class ScriptTest(Test):
    path: str

class CommandTest(Test):
    command: str

class SlurmScript(Test):
    path: str
    nodeLists: str

class SlurmPairScript(Test):
    pairSize: int
    path: str
    nodeLists: str

class SlurmScriptPairTest(Test):
    slurmPairScript: SlurmPairScript

class SlurmScriptTest(Test):
    slurmScript: SlurmScript

# vim: set et ts=4 sw=4 sts=4:
