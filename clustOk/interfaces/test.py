class Test:
    noFail: bool
    maxDifference: int

class Script(Test):
    path: str

class Command(Test):
    command: str

class SlurmScript(Test):
    path: str
    nodeLists: str

class SlurmPairScript(SlurmScript):
    pairSize: int