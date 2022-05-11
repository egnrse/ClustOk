import logging
import subprocess
from subprocess import PIPE, Popen

from configManager import Config

from slurmHelper import SlurmHelper


class TestRunner:
    def __init__(self, logger: logging.Logger, config: Config):
        self.logger = logger
        self.config = config
        self.slurmHelper = SlurmHelper(logger, config)
        return

    def executeTests(self):
        self.logger.info('Executing Tests...')
        result = 0

        for test in self.config.tests: 
            if 'command' in test:
                self.logger.debug('[%s]: Executing test-command..' % test['name'])
                results = self.executeCommand(test['command'])

            elif 'script' in test:
                self.logger.debug('[%s]: Executing test-script..' % test['name'])
                results = self.executeSingleBash(test['script'])
            
            elif 'slurmScript' in test:
                self.logger.debug('[%s]: Executing slurm test-script..' % test['name'])
                results = self.slurmHelper.executeSlurmScript(test)

            result += self.evaluate(test, results)

        if result > 0:
            self.logger.error('%d/%d tests failed!', result, len(self.config.tests))

    def executeCommand(self, command):
        result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8'))]

    def executeSingleBash(self, test):
        result = subprocess.run([test['path']], stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8'))]

    def evaluateMin(self, results, min):
        for result in results:
            if (result < min):
                self.logger.warn('Min value threshold violated. %d instead of %d', result, min)
                return False

        return True

    def evaluateMax(self, results, max):
        for result in results:
            if (result > max):
                self.logger.warn('Max value threshold violated. %d instead of %d', result, max)
                return False
        
        return True

    def evaluateDifference(self, results, maxDifference):
        max_val = max(results)
        min_val = min(results)
        difference = max_val - min_val

        if difference > maxDifference:
            self.logger.warn('Difference threshold violated. Highest difference is %d istead of allowed %d', difference, maxDifference)
            return False

        return True

    def evaluate(self, test, results):
        self.logger.debug('[%s]: Evaluating results for test...', test['name'])

        failures = []
        result = True

        for res in results:
            if res[1] != 0:
                result = False
                error = '[%s]: Node "%s" failed with error: [%d]: %s' % (test['name'], res[0], res[1], res[2])
                self.logger.warn(error)
                failures.append(error)

        if 'conditions' in test:
            conditions = test['conditions']

            if 'min' in conditions or 'max' in conditions or 'difference' in conditions:
                try:
                    outputs = *map(lambda res: float(res[2]), results),

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

        if result:
            self.logger.debug('[%s] Succeeded!', test['name'])
            return 0
        
        return 1