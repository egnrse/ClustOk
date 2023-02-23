import logging
import subprocess

from interfaces.test import CommandTest, ScriptTest
from interfaces.testresult import SingleResult
from interfaces.runner import Runner

from utils.config.config import Config

from typing import List

class LocalTestRunner(Runner):
    def __init__(self, logger: logging.Logger, config: Config):
        self.logger = logger
        self.config = config
        return

    def execute(self) -> List[SingleResult]:
        self.logger.info('Executing Basic Tests...')
        results = []

        for test in self.config.tests:
            summary = {}

            if hasattr(test, 'command'):
                commandTest: CommandTest = test
                self.logger.info('[%s]: Executing command-test..' % commandTest.name)
                result = self.executeCommand(commandTest.command)

                results.append({ "name": test.name, "returncode": result[0], "output": result[1], "nodes": 'local'})

            elif hasattr(test, 'script'):
                scriptTest: ScriptTest = test
                self.logger.info('[%s]: Executing test-script..' % scriptTest.name)
                result = self.executeSingleBash(scriptTest.script.path)

                results.append({ "name": test.name, "returncode": result[0], "output": result[1], "nodes": 'local'})

        return results

    def executeCommand(self, command) -> SingleResult:
        process = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
        return (process.returncode, process.stdout.decode('utf-8').rstrip())

    def executeSingleBash(self, path) -> SingleResult :
        result = subprocess.run([path], stdout=subprocess.PIPE)
        return (result.returncode, result.stdout.decode('utf-8').rstrip())