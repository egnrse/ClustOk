import logging
import subprocess
from subprocess import PIPE, Popen

from configManager import Config

from slurmHelper import SlurmHelper
from testEvaluator import TestEvaluator


class TestRunner:
    def __init__(self, logger: logging.Logger, config: Config):
        self.logger = logger
        self.config = config
        self.slurmHelper = SlurmHelper(logger, config)
        self.evaluator = TestEvaluator(logger, config)
        return

    def executeTests(self):
        self.logger.info('Executing Tests...')
        result = 0

        for test in self.config.tests: 
            if 'command' in test:
                self.logger.info('[%s]: Executing test-command..' % test['name'])
                results = self.executeCommand(test['command'])

            elif 'script' in test:
                self.logger.info('[%s]: Executing test-script..' % test['name'])
                results = self.executeSingleBash(test['script'])
            
            elif 'slurmScript' in test:
                self.logger.info('[%s]: Executing slurm test-script..' % test['name'])
                results = self.slurmHelper.executeSlurmScript(test['slurmScript'])

            elif 'slurmPairScript' in test:
                self.logger.info('[%s]: Executing slurm test-script in pairs..' % test['name'])
                results = self.slurmHelper.executeSlurmScriptInPairs(test['slurmPairScript'])

            result += self.evaluator.evaluate(test, results)

        if result > 0:
            self.logger.error('%d/%d tests failed!', result, len(self.config.tests))

    def executeCommand(self, command):
        result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8'))]

    def executeSingleBash(self, test):
        result = subprocess.run([test['path']], stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8'))]