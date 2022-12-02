from io import TextIOWrapper
from interfaces.exporter import Exporter

from utils.config.config import OutputSettings
from datetime import datetime

import json


class ConsoleExporter(Exporter):
    def __init__(self):
        pass

    def update(self, testResults):

        print("ClustOK Testrun " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")

        # Iterate every testName
        for testName, results in testResults.items():
            print("\n=============================================")
            print(testName + ":\n")
            print("NODE(s),CODE,OUTPUT")

            # Iterate every result
            for result in results:
                print(result["nodes"], end=",")
                print(str(result["returncode"]), end=",")
                print(result["output"])     

    def destroy(self):
        pass     

    @staticmethod
    def init(settings: OutputSettings):
        exporter = ConsoleExporter()
        return exporter   