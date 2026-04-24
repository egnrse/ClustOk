from typing import List
from interfaces.testresult import TestResult


class Exporter():

    @staticmethod
    def init() -> object:
        """Inits the exporter"""
        pass

    def update(self, testResult: List[TestResult]):
        """Inserts the latest testresults for exportation"""
        pass

    def destroy(self):
        """Closes open handles"""
        pass

# vim: set et ts=4 sw=4 sts=4:
