import json
from datetime import datetime

from logging import Logger
from interfaces.exporter import Exporter
from utils.config.config import OutputSettings



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
        
        try:
            with open(fileName + ".json", "w") as outputFile:
                outputFile.write(json.dumps(jsoninfo, indent=4))
        except (OSError, PermissionError) as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Cannot open output file for writing: '{fileName}.json'")
            exit(1)

    def prettyPrint(self, testResults, fileName):
        try:
            with open(fileName + ".txt", "w") as outputFile:
                outputFile.write("ClustOk Testrun " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n")

                # Iterate every testName
                for results in testResults:
                    outputFile.write("\n=============================================\n")
                    outputFile.write(results['testName'] + ":\n\n")
                    
                    if ('evaluations' in results):
                        outputFile.write("Evaluation:\n")
                        for condition, evaluation in results['evaluations'].items():
                            outputFile.write(condition + ":" + "\t" + str(evaluation[0]))
                            outputFile.write("\t\t" + str(evaluation[1]) + " of " +  str([evaluation[2]]) + " needed \n")
                        outputFile.write("\n")

                    outputFile.write("Detail:\n")
                    outputFile.write("NODE(s)\t\t\t\t\t\t\tCODE\t\t\tOUTPUT\n")

                    # Iterate every result
                    for result in results['detailedResults']:
                        outputFile.write(result["nodes"] + "\t\t\t\t\t\t\t")
                        outputFile.write(str(result["returncode"]) + "\t\t\t\t")
                        outputFile.write(result["output"])
                        outputFile.write('\n')
        except (OSError, PermissionError) as e:
            self.logger.debug(f"{e}")
            self.logger.error(f"Cannot open output file for writing: '{fileName}.txt'")
            exit(1)

    @staticmethod
    def init(logger: Logger, outputSettings: OutputSettings):
        exporter = FileExporter()
        exporter.dir = outputSettings.dir
        exporter.fileName = outputSettings.fileName
        exporter.format = outputSettings.format
        exporter.logger = logger
        return exporter   

# vim: set et ts=4 sw=4 sts=4:
