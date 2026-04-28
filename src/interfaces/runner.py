from typing import List
from interfaces.testresult import SingleResult


class Runner:
    def execute(self) -> List[SingleResult]:
        """Runs the test provided in config"""
        raise NotImplementedError

# vim: set et ts=4 sw=4 sts=4:
