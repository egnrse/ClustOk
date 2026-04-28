import logging

from typing import List, Dict
from interfaces.testresult import TestResult, SingleResult, SingleEval


class BaseEvaluator:
    # what conditions this evaluator supports
    SUPPORTED = ["max", "min", "difference"]
    
    def __init__(self, logger: logging.Logger, config):
        self.logger = logger
        self.config = config
        return

    def evaluate(self, testResults: Dict[str,SingleResult]) -> List[TestResult]:
        endResult = True
        endResults = []
        failures = []

        # Iterate every testName
        for testName, results in testResults.items():
            failedNodes = []
            test = next((x for x in self.config.tests if x.name == testName), None)

            if test is None:
                self.logger.warn('There are results for a not specified test. Exiting evaluation for this test: %s' % testname)
                continue

            # Check every returncode to be 0
            for result in results:
                errors = []
                if result.returncode != 0:
                    endResult = False
                    errors.append('error: [%d]: %s' % (result.returncode, result.output))
                    failedNodes.append(result.nodes)

            testEvaluation = {}
            testEvaluation['testName'] = testName
            testEvaluation['detailedResults'] = results

            # Check conditions of tests
            if hasattr(test, 'conditions'):
                outputs = [res.output for res in results]
                testEvaluation['evaluations'] = self.evaluateSubCondition(outputs, test.conditions, testName)

            endResults.append(testEvaluation)

        return endResults

    def evaluateSubCondition(self, outputs: List[str], conditions, name) -> Dict[str, SingleEval]:
        evaluations = {}

        if any(hasattr(conditions, cond) for cond in self.SUPPORTED):
            try:
                numberOutputs = [float(o) for o in outputs]
            except Exception as err:
                self.logger.debug(err)
                self.logger.error("Result of test '%s' are not parseable as number, but numeric condition is specified!", name)
                val = {}
                error = f"Result not parseable as a number: '{",".join(outputs)}'"
                for cond in self.SUPPORTED:
                    if hasattr(conditions, cond):
                        val[cond] = (False, None, getattr(conditions, cond), error)
                return val

            if hasattr(conditions, 'min'):
                evaluations['min'] = self.evaluateMin(numberOutputs, conditions.min)
            if hasattr(conditions,'max'):
                evaluations['max'] = self.evaluateMax(numberOutputs, conditions.max)
            if hasattr(conditions,'difference'):
                evaluations['difference'] = self.evaluateDifference(numberOutputs, conditions.difference)
        
        return evaluations

    def evaluateMin(self, results: List[float], minThreshold: float) -> SingleEval:
        min_val = min(results)

        self.logger.debug("Minimum result is %f out of required %f", min_val, minThreshold)
        if (min_val < minThreshold):
            error = f'Min value threshold violated. {min_val} instead of {minThreshold}'
            self.logger.warning(error)
            return (False, min_val, minThreshold, error)

        return (True, min_val, minThreshold, None)

    def evaluateMax(self, results: List[float], maxThreshold: float) -> SingleEval:
        max_val = max(results)

        self.logger.debug("Maximum result is %f of allowed %f", max_val, maxThreshold)
        if (max_val > maxThreshold):
            error = f'Max value threshold violated. {max_val} instead of {maxThreshold}'
            self.logger.warning(error)
            return (False, max_val, maxThreshold, error)
        
        return (True, max_val, maxThreshold, None)

    def evaluateDifference(self, results: List[float],  maxDifference: float) -> SingleEval:
        max_val = max(results)
        min_val = min(results)
        difference = max_val - min_val

        self.logger.debug("Max difference is %f of %f allowed", difference, maxDifference)
        if difference > maxDifference:
            error = f'Difference threshold violated. Highest difference is {difference} instead of allowed {maxDifference}'
            self.logger.warn(error)
            return (False, difference, maxDifference, error)

        return (True, difference, maxDifference, None)

# vim: set et ts=4 sw=4 sts=4:
