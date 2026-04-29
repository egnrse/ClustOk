import json
from datetime import datetime

from typing import List, Dict, Any
from logging import Logger
from interfaces.exporter import Exporter
from interfaces.testresult import TestResult
from utils.config.config import FileSettings



class FileExporter(Exporter):
    def __init__(self, logger: Logger, output: FileSettings):
        self.logger = logger
        self.dir = output.dir
        self.fileName = output.fileName
        self.format = output.format
        self.rotate: str
        return

    def update(self, testResults: List[TestResult]) -> None:
        fileName = datetime.now().strftime(self.fileName)

        if self.format == 'pretty':
            self.prettyPrint(testResults, self.dir + '/' + fileName)

        elif self.format == 'json':
            self.jsonPrint(testResults, self.dir + '/' +  fileName)
            

    def destroy(self) -> None:
        pass     

    def jsonPrint(self, testResults: List[TestResult], fileName: str) -> None:
        jsoninfo: Dict[str, Any] = {}
        jsoninfo["testresults"] = testResults
        jsoninfo["timestamp"] = datetime.now().isoformat()
        jsonOut = json.dumps(jsoninfo, indent=4, default=lambda o: o.__dict__)

        try:
            with open(fileName + ".json", "w") as outputFile:
                outputFile.write(jsonOut)
        except (OSError, PermissionError) as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Cannot open output file for writing: '{fileName}.json'")
            exit(1)

    def prettyPrint(self, testResults: List[TestResult], fileName: str) -> None:
        try:
            with open(fileName + ".txt", "w") as outputFile:
                outputFile.write("ClustOk Testrun " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n")

                # Iterate every testName
                for results in testResults:
                    outputFile.write("\n=============================================\n")
                    outputFile.write(results.testName + ":\n\n")
                    
                    if results.evaluations is not None:
                        outputFile.write("Evaluation:\n")
                        for condition, evaluation in results.evaluations.items():
                            outputFile.write(condition + ":" + "\t" + str(evaluation[0]))
                            outputFile.write("\t\t" + str(evaluation[1]) + " of " +  str([evaluation[2]]) + " needed \n")
                        outputFile.write("\n")

                    outputFile.write("Detail:\n")
                    outputFile.write("NODE(s)\t\t\t\t\t\t\tCODE\t\t\tOUTPUT\n")

                    # Iterate every result
                    for result in results.detailedResults:
                        outputFile.write(result.nodes + "\t\t\t\t\t\t\t")
                        outputFile.write(str(result.returncode) + "\t\t\t\t")
                        outputFile.write(result.output)
                        outputFile.write('\n')
        except (OSError, PermissionError) as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Cannot open output file for writing: '{fileName}.txt'")
            exit(1)

    @classmethod
    def init(cls, logger: Logger, outputSettings: FileSettings) -> Exporter:
        return cls(logger, outputSettings)

# vim: set et ts=4 sw=4 sts=4:
