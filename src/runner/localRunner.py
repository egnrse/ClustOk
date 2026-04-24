import subprocess

from typing import List
from logging import Logger
from interfaces.test import CommandTest, ScriptTest
from interfaces.testresult import SingleResult
from interfaces.runner import Runner
from utils.config.config import Config


class LocalTestRunner(Runner):
    def __init__(self, logger: Logger, config: Config):
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
                try:
                    result = self.executeCommand(commandTest.command, commandTest.name)
                    results.append(result)
                except (OSError, FileNotFoundError, PermissionError) as e:
                    self.logger.debug(f"{e}")
                    self.logger.error(f"Unable to execute: '{commandTest.command}'")
                    exit(1)

            elif hasattr(test, 'script'):
                scriptTest: ScriptTest = test
                self.logger.info('[%s]: Executing test-script..' % scriptTest.name)
                try:
                    result = self.executeSingleBash(scriptTest.script.path, scriptTest.name)
                    results.append(result)
                except (OSError, FileNotFoundError, PermissionError) as e:
                    self.logger.debug(f"{e}")
                    self.logger.error(f"Unable to execute the script: '{scriptTest.script.path}'")
                    exit(1)

        return results

    def collectResults(self, process, testName: str) -> SingleResult:
        p = process
        if p.poll() is None:
            timeout = self.config.settings.timeout
            if timeout < 0:
                p.wait()
            else:
                try:
                    p.wait(timeout)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Terminating process '%s' (timeout)", testName);
                    p.terminate()

        returncode = p.returncode
        if returncode == None:
            returncode = 124    # returncode for terminated jobs
        stdout, stderr = p.communicate()

        result = { "name": testName, "returncode": returncode, "output": stdout.rstrip(), "nodes": 'local'}
        return result

    def executeCommand(self, command, testName: str) -> SingleResult:
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return self.collectResults(process, testName)

    def executeSingleBash(self, path, testName: str) -> SingleResult :
        process = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return self.collectResults(process, testName)

# vim: set et ts=4 sw=4 sts=4:
