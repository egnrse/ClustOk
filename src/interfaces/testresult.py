from dataclasses import dataclass
from typing import List, Dict, Tuple


# [did it pass, measured value, should value, error message]
SingleEval = Tuple[bool, float|None, float, str|None]


@dataclass
class SingleResult(): 
    name: str
    nodes: str
    output: str
    returncode: int

@dataclass
class TestResult():
    testName: str
    detailedResults: List[SingleResult]
    evaluations: Optional[Dict[str, SingleEval]] = None

# vim: set et ts=4 sw=4 sts=4:
