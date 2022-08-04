from io import TextIOWrapper
from interfaces.exporter import Exporter

class FileExporter(Exporter):
    def __init__(self):
        self.file: TextIOWrapper

    def update(self, testResults):
        for result in testResults[0]:
            self.file.write("=============================================\n")
            self.file.write(result["name"] + ":\n")
            self.file.write("NODE(s)\t\t\t\t\t\t\tCODE\t\t\tOUTPUT\n")
            for output in result["result"]:
                self.file.write(output[0] + "\t\t\t\t\t\t\t")
                self.file.write(str(output[1]) + "\t\t\t")
                self.file.write(output[2])
                self.file.write('\n')
            self.file.write("\n")
            

    def destroy(self):
        self.file.close()     

    @staticmethod
    def init(filePath: str):
        exporter = FileExporter()
        exporter.file = open(filePath, "w")
        return exporter   