import logging
import subprocess

from utils.configManager import Config
from runner.slurmRunner import SlurmHelper
from testEvaluator import TestEvaluator


class TestRunner:
    def __init__(self, logger: logging.Logger, config: Config):
        self.logger = logger
        self.config = config
        self.slurmHelper = SlurmHelper(logger, config)
        self.evaluator = TestEvaluator(logger, config)
        return

    def execute(self):
        self.logger.info('Executing Tests...')
        results = {}

        for test in self.config.tests:
            summary = {}
            if 'command' in test:
                self.logger.info('[%s]: Executing test-command..' % test['name'])
                result = self.executeCommand(test['command'])

            elif 'script' in test:
                self.logger.info('[%s]: Executing test-script..' % test['name'])
                result = self.executeSingleBash(test['script'])
            
            elif 'slurmScript' in test:
                self.logger.info('[%s]: Executing slurm test-script..' % test['name'])
                result = self.slurmHelper.executeSlurmScript(test['slurmScript'])

            elif 'slurmPairScript' in test:
                self.logger.info('[%s]: Executing slurm test-script in pairs..' % test['name'])
                result = self.slurmHelper.executeSlurmScriptInPairs(test['slurmPairScript'])
            
            evaluation = self.evaluator.evaluate(test, result, summary)
            results[test["name"]] = ({"name": test["name"], "result": result, "test": test, "evaluation": evaluation, "summary": summary})

        return results

    def executeCommand(self, command):
        result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8').rstrip())]

    def executeSingleBash(self, test):
        result = subprocess.run([test['path']], stdout=subprocess.PIPE)
        return [('local', result.returncode, result.stdout.decode('utf-8').rstrip())]