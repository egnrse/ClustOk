from io import TextIOWrapper
from interfaces.exporter import Exporter

from utils.config.config import OutputSettings
from datetime import datetime

import json


class FileExporter(Exporter):
    def __init__(self):
        self.format: str
        self.fileName: str
        self.dir: str
        self.rotate: str

    def update(self, testResults):
        fileName = datetime.now().strftime(self.fileName)

        if self.format == 'pretty':
            self.prettyPrint(testResults, self.dir + '/' + fileName)

        elif self.format == 'json':
            self.jsonPrint(testResults, self.dir + '/' +  fileName)
            

    def destroy(self):
        pass     

    def jsonPrint(self, testResults, fileName):
        jsoninfo = {}
        jsoninfo["testresults"] = testResults
        jsoninfo["timestamp"] = datetime.now().isoformat()
        
        with open(fileName + ".json", "w") as outputFile:
            outputFile.write(json.dumps(jsoninfo, indent=4))

    def prettyPrint(self, testResults, fileName):
        with open(fileName + ".txt", "w") as outputFile:
            outputFile.write("ClustOK Testrun " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n")


            # Iterate every testName
            for testName, results in testResults.items():
                outputFile.write("\n=============================================\n")
                outputFile.write(testName + ":\n\n")
                outputFile.write("NODE(s)\t\t\t\t\t\t\tCODE\t\t\tOUTPUT\n")

                # Iterate every result
                for result in results:
                    outputFile.write(result["nodes"] + "\t\t\t\t\t\t\t")
                    outputFile.write(str(result["returncode"]) + "\t\t\t\t")
                    outputFile.write(result["output"])
                    outputFile.write('\n')

    @staticmethod
    def init(outputSettings: OutputSettings):
        exporter = FileExporter()
        exporter.dir = outputSettings.dir
        exporter.fileName = outputSettings.fileName
        exporter.format = outputSettings.format
        return exporter   