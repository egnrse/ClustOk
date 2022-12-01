from io import TextIOWrapper
from interfaces.exporter import Exporter

from utils.config.config import OutputSettings

class FileExporter(Exporter):
    def __init__(self):
        self.file: TextIOWrapper
        self.format: str

    def update(self, testResults):
        if self.format == 'pretty':
            self.prettyPrint(testResults)

        elif self.format == 'json':
            self.jsonPrint(testResults)
            

    def destroy(self):
        self.file.close()     

    def jsonPrint(self, testResults):
        print('test')

    def prettyPrint(self, testResults):
        # Iterate every testName
        for testName, results in testResults.items():
            self.file.write("=============================================\n")
            self.file.write(testName + ":\n")
            self.file.write("NODE(s)\t\t\t\t\t\t\tCODE\t\t\tOUTPUT\n")

            # Iterate every result
            for result in results:
                self.file.write(result["nodes"] + "\t\t\t\t\t\t\t")
                self.file.write(str(result["returncode"]) + "\t\t\t")
                self.file.write(result["output"])
                self.file.write('\n')
            self.file.write("\n")

    @staticmethod
    def init(outputSettings: OutputSettings):
        exporter = FileExporter()
        exporter.file = open(outputSettings.fileName, "w")
        exporter.format = outputSettings.format
        return exporter   