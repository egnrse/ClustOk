# testing exporters
import pytest, logging, json

import requests
from prometheus_client.parser import text_string_to_metric_families

from interfaces.testresult import SingleResult

from utils.logger.customLogger import CustomLogger
from utils.config.config import DictToConf
from exporter.fileExporter import FileExporter
from exporter.prometheusExporter import PrometheusExporter
from exporter.consoleExporter import ConsoleExporter


input = [
    {
        "detailedResults": [SingleResult(name="Test min/max", nodes="local", output="6", returncode=0)],
        "evaluations": {"max": (True, 6.0, 7, None), "min": (True, 6.0, 5, None)},
        "testName": "Test min/max"
    },
    {
        "detailedResults": [SingleResult(name="StringTest", nodes="local", output="a test string\nline2", returncode=0)],
        "testName": "StringTest"
    }
]

class TestConsoleExporter:
    def test_output(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        e = ConsoleExporter.init({},{})
        e.update(input)
        e.destroy()

        content = capsys.readouterr()
        assert "ClustOk Testrun" in content.out
        assert "6.0 of [5] needed" in content.out
        assert "6.0 of [7] needed" in content.out
        assert "Test min/max" in content.out
        assert "6" in content.out
        assert "local" in content.out
        assert "" == content.err


file_conf = {'settings': {'output': {'file': {'dir': '/dev/null', 'fileName': 'testLog', 'format': 'json'}}}}
filePretty_conf = {'settings': {'output': {'file': {'dir': '/dev/null', 'fileName': 'testLog', 'format': 'pretty'}}}}

class TestfileExporter:
    def test_invalidPath(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(file_conf)
        e = FileExporter.init(logger, config.settings.output.file)
        with pytest.raises(SystemExit):
            e.update(input)

        captured = capsys.readouterr()
        assert "ERROR - " in captured.err
        assert "Cannot open output file" in captured.err
        assert "'/dev/null/testLog.json'" in captured.err

    def test_invalidPathPretty(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(filePretty_conf)
        e = FileExporter.init(logger, config.settings.output.file)
        with pytest.raises(SystemExit):
            e.update(input)

        captured = capsys.readouterr()
        assert "ERROR - " in captured.err
        assert "Cannot open output file" in captured.err
        assert "'/dev/null/testLog.txt'" in captured.err

    def test_validJSON(self, tmp_path):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(file_conf)
        config.settings.output.file.dir = str(tmp_path)
        e = FileExporter.init(logger, config.settings.output.file)
        e.update(input)
        e.destroy()

        f = tmp_path/"testLog.json"
        json.loads(f.read_text())

    def test_output(self, tmp_path):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(file_conf)
        config.settings.output.file.dir = str(tmp_path)
        e = FileExporter.init(logger, config.settings.output.file)
        e.update(input)
        e.destroy()

        file = tmp_path/"testLog.json"
        content = file.read_text()
        assert "testresults" in content
        assert "timestamp" in content
        assert "detailedResults" in content
        assert "evaluations" in content
        assert "testName" in content
        assert "Test min/max" in content
        assert "6" in content
        assert "local" in content

    def test_outputPretty(self, tmp_path):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(filePretty_conf)
        config.settings.output.file.dir = str(tmp_path)
        e = FileExporter.init(logger, config.settings.output.file)
        e.update(input)
        e.destroy()

        file = tmp_path/"testLog.txt"
        content = file.read_text()
        assert "6.0 of [5] needed" in content
        assert "6.0 of [7] needed" in content
        assert "Test min/max" in content
        assert "6" in content
        assert "local" in content



EXPORTER_URL = "http://localhost:56531/metrics"
prometheus_conf = {'settings': { 'output': {'prometheus': {'enable': True, 'port': 56531}}}, 'tests': [{'name': 'Test min/max', 'descr': '', 'command': 'echo 6', 'conditions': {'min': 5, 'max': 7}}, {'name': 'Script Test', 'descr': 'Executes a script', 'script': {'path': './testscripts/datetest.sh'}}]}

class TestPrometheusExporter:
    # only one test because of port/registry collisions
    def test_ALL(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(prometheus_conf)
        e = PrometheusExporter.init(logger, config)
        e.update(input)

        resp = requests.get(EXPORTER_URL, timeout=5)
        assert resp.status_code == 200

        metrics = list(text_string_to_metric_families(resp.text))
        assert len(metrics) > 3

        e.destroy()

        captured = capsys.readouterr()
        assert "INFO - " in captured.err
        assert "prometheus server" in captured.err
        assert "port 56531" in captured.err

# vim: set et ts=4 sw=4 sts=4:
