import logging


class BaseEvaluator:
    def __init__(self, logger: logging.Logger, config):
        self.logger = logger
        self.config = config
        return

    def evaluate(self, testResults):
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
                if result['returncode'] != 0:
                    endResult = False
                    errors.append('error: [%d]: %s' % result['returncode'], result['output'])
                    failedNodes.append(result['nodes'])

            # Check conditions of tests
            if hasattr(test, 'conditions'):
                
                #if isinstance(conditions, list):
                #    outputs = tuple(map(lambda output: output.split('\n'), outputs))
                #    if len(conditions) != 0 and len(outputs[0]) != len(conditions):
                #        self.logger.error('Result of test with multiple conditions has to have one output per condition!')
                #        exit(6)

                #    for i in range(0, len(conditions)-1):
                #        result &= self.evaluateSubCondition(outputs[i], conditions[i], summary)

                #else:
                outputs = (map(lambda res: res['output'], results))

                testEvaluation = {}
                testEvaluation['testName'] = testName
                testEvaluation['detailedResults'] = results
                testEvaluation['evaluations'] = self.evaluateSubCondition(outputs, test.conditions)
                endResults.append(testEvaluation)

        return endResults

    def evaluateSubCondition(self, outputs, conditions):
        endResults = {}

        if hasattr(conditions, 'min') or  hasattr(conditions,'max') or hasattr(conditions,'difference'):
            try:
                numberOutputs = *map(lambda output: float(output), outputs),

                if hasattr(conditions, 'min'):
                    endResults['min'] = self.evaluateMin(numberOutputs, conditions.min)

                if hasattr(conditions,'max'):
                    endResults['max'] = self.evaluateMax(numberOutputs, conditions.max)

                
                if hasattr(conditions,'difference'):
                    endResults['difference'] = self.evaluateDifference(numberOutputs, conditions.difference)

            except Exception as err:
                self.logger.error('Results of tests have to be parseable as number if numeric condition is specified!')
                self.logger.error(err)
                exit(5)
        
        return endResults

    def evaluateMin(self, results, minThreshold):
        min_val = min(results)

        self.logger.debug("Minimum result is %f out of required %f", min_val, minThreshold)
        if (min_val < minThreshold):
            error = f'Min value threshold violated. {min_val} instead of {minThreshold}'
            self.logger.warn(error)
            return (False, min_val, minThreshold, error)

        return (True, min_val, minThreshold, None)

    def evaluateMax(self, results, maxThreshold):
        max_val = max(results)

        self.logger.debug("Maximum result is %f of %f allowed", max_val, maxThreshold)
        if (max_val > maxThreshold):
            error = f'Max value threshold violated. {max_val} instead of {maxThreshold}'
            self.logger.warn(error)
            return (False, max_val, maxThreshold, error)
        
        return (True, max_val, maxThreshold, None)

    def evaluateDifference(self, results,  maxDifference):
        max_val = max(results)
        min_val = min(results)
        difference = max_val - min_val

        self.logger.debug("Max difference is %f of %f allowed", difference, maxDifference)
        if difference > maxDifference:
            error = f'Difference threshold violated. Highest difference is {difference} instead of allowed {maxDifference}'
            self.logger.warn(error)
            return (False, difference, maxDifference, error)

        return (True, difference, maxDifference, None)

    
