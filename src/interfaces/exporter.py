from typing import List, Any
from logging import Logger
from interfaces.testresult import TestResult
from utils.config.config import OutputSettings


class Exporter():

    @staticmethod
    def init(logger: Logger, settings: Any) -> object:
        """Inits the exporter"""
        raise NotImplementedError

    def update(self, testResult: List[TestResult]) -> None:
        """Inserts the latest testresults for exportation"""
        pass

    def destroy(self) -> None:
        """Closes open handles"""
        pass

# vim: set et ts=4 sw=4 sts=4:
