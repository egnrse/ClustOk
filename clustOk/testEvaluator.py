import logging

from configManager import Config


class TestEvaluator:
    def __init__(self, logger: logging.Logger, config: Config):
        self.logger = logger
        self.config = config
        return

    def evaluate(self, test, results):
        self.logger.info('[%s]: Evaluating results for test...', test['name'])
        result = True
        failures = []
        

        for res in results:
            if res[1] != 0:
                result = False
                error = '[%s]: Node "%s" failed with error: [%d]: %s' % (test['name'], res[0], res[1], res[2])
                self.logger.warn(error)
                failures.append(error)

        if 'conditions' in test:
            conditions = test['conditions']

            outputs = *map(lambda result: result[2], results),

            print(outputs)
            print(conditions)

            if isinstance(conditions, list):
                outputs = tuple(map(lambda output: output.split('\n'), outputs))
                if len(conditions) != 0 and len(outputs[0]) != len(conditions):
                    self.logger.error('Result of test with multiple conditions has to have one output per condition!')
                    exit(6)

                for i in range(0, len(conditions)-1):
                    result &= self.evaluateSubCondition(outputs[i], conditions[i])

            else:
                result &= self.evaluateSubCondition(outputs, conditions)



        if result:
            self.logger.info('[%s] Succeeded!', test['name'])
            return 0
        
        return 1

    def evaluateSubCondition(self, outputs, conditions):
        result = True

        if 'min' in conditions or 'max' in conditions or 'difference' in conditions:
            try:
                outputs = *map(lambda output: float(output), outputs),

                if 'min' in conditions:
                    result &= self.evaluateMin(outputs, conditions['min'])
                
                if 'max' in conditions:
                    result &= self.evaluateMax(outputs, conditions['max'])
                
                if 'difference' in conditions:
                    result &= self.evaluateDifference(outputs, conditions['difference'])

            except Exception as err:
                self.logger.error('Results of tests have to be parseable as number if numeric condition is specified!')
                self.logger.error(err)
                exit(5)
        
        return result

    def evaluateMin(self, results, minThreshold):
        min_val = min(results)
        self.logger.debug("Minimum result is %d out of required %d", min_val, minThreshold)
        if (min_val < minThreshold):
            self.logger.warn('Min value threshold violated. %d instead of %d', min_val, minThreshold)
            return False

        return True

    def evaluateMax(self, results, maxThreshold):
        max_val = max(results)
        self.logger.debug("Maximum result is %d of %d allowed", max_val, maxThreshold)
        if (max_val > maxThreshold):
            self.logger.warn('Max value threshold violated. %d instead of %d', max_val, maxThreshold)
            return False
        
        return True

    def evaluateDifference(self, results, maxDifference):
        max_val = max(results)
        min_val = min(results)
        difference = max_val - min_val
        self.logger.debug("Max difference is %d of %d allowed", difference, maxDifference)
        if difference > maxDifference:
            self.logger.warn('Difference threshold violated. Highest difference is %d istead of allowed %d', difference, maxDifference)
            return False

        return True

    