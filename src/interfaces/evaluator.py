from typing import List, Dict
from interfaces.testresult import TestResult, SingleResult


class Evaluator:
    def evaluate(self, testResults: Dict[str,List[SingleResult]]) -> List[TestResult]:
        """Evaluates testResults"""
        raise NotImplementedError

# vim: set et ts=4 sw=4 sts=4:
