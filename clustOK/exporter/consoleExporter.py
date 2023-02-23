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
        for results in testResults:
            print("\n=============================================")
            print(results['testName'] + ":\n")

            print('Summary:\n')
            for condition, evaluation in results['evaluations'].items():
                    print(condition + ":" + "\t" + str(evaluation[0]), end="")
                    print("\t\t" + str(evaluation[1]) + " of " +  str([evaluation[2]]) + " needed \n\n")

            print("NODE(s),CODE,OUTPUT")

            # Iterate every result
            for result in results['detailedResults']:
                print(result["nodes"], end=",")
                print(str(result["returncode"]), end=",")
                print(result["output"])     

    def destroy(self):
        pass     

    @staticmethod
    def init(settings: OutputSettings):
        exporter = ConsoleExporter()
        return exporter   