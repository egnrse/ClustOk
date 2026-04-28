# testing runner
import pytest, logging

from interfaces.testresult import SingleResult

from utils.logger.customLogger import CustomLogger
from utils.config.config import DictToConf
from runner.slurmRunner import SlurmTestRunner
from runner.localRunner import LocalTestRunner


#slurm_conf_min = {'settings': {'slurm': {'dir': './invalid/directory', 'partition': 'test_part', 'args': ['--comment="clustok test job"']}}, 'tests': []}
slurm_conf = {'settings': {'timeout': '-1', 'slurm': {'dir': './invalid/directory', 'partition': 'test_part', 'args': ['--comment="clustok test job"']}}, 'nodeLists': {'testCompute': {'nodeNames': 'testnode[01-9]'}}, 'tests': [{'name': 'SlurmScript', 'descr': '', 'slurmScript': {'path': './test.sh', 'nodeLists': 'testCompute'}}, {'name': 'SlurmPairScript', 'descr': '', 'slurmPairScript': {'path': './test.sh', 'nodeLists': 'testCompute', 'pairSize': 2}}]}

class Test_SlurmRunner:
    # prepare some general things
    def prepare(self, fp):
        # you need to register once per call
        for i in range(0,2):
            fp.register(["./invalid/directory/sinfo", "-hN", "-O","NodeList,StateCompact", fp.any()], stdout="testnode01\t\tidle\ntestnode02\t\tidle\ntestnode03\t\tidle\ntestnode04\t\tidle\ntestnode05\t\tidle\ntestnode06\t\tdown\ntestnode07\t\talloc\ntestnode08\t\tdrain\ntestnode09\t\tidle\n")
        for i in range(0,13):
            fp.register(["./invalid/directory/srun", fp.any()], stdout="test output")
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(slurm_conf)
        return SlurmTestRunner(logger, config)

    def test_slurmNotFoundWarning(self, capsys, fp):
        sr = self.prepare(fp)
        captured = capsys.readouterr()
        assert "WARNING - " in captured.err
        assert "Slurm binaries" in captured.err
        assert "./invalid/directory" in captured.err

    def test_slurmInfo(self, capsys, fp):
        sr = self.prepare(fp)
        result = sr.execute()
        #assert result == ""
        captured = capsys.readouterr()
        assert "INFO - " in captured.err
        assert "Executing Slurm Tests" in captured.err
        assert "7/9 Nodes of testnode[01-9] are available for the test" in captured.err
        assert "[SlurmScript]: Executing slurmScript-test" in captured.err
        assert "[SlurmPairScript]: Executing slurm test-script in pairs" in captured.err

    def test_slurmDebug(self, capsys, fp):
        sr = self.prepare(fp)
        result = sr.execute()
        captured = capsys.readouterr()
        assert "DEBUG - " in captured.err
        assert "Executing test on node testnode01" in captured.err
        assert "Executing test on node-pair testnode" in captured.err #node pairs are not stable

    def test_slurmScript(self, capsys, fp):
        sr = self.prepare(fp)
        result = sr.execute()
        expected = SingleResult(
            name="SlurmScript",
            nodes="testnode04",
            output="test output",
            returncode=0
        )
        assert expected in result

    def test_slurmPairScript(self, capsys, fp):
        sr = self.prepare(fp)
        result = sr.execute()
        expected = [
            SingleResult(
                name="SlurmPairScript",
                returncode=0,
                output="test output",
                nodes="testnode03,testnode07,"
            ),
            SingleResult(
                name="SlurmPairScript",
                returncode=0,
                output="test output",
                nodes="testnode09,testnode07,"
            ),
            SingleResult(
                name="SlurmPairScript",
                returncode=0,
                output="test output",
                nodes="testnode01,testnode04,"
            ),
            SingleResult(
                name="SlurmPairScript",
                returncode=0,
                output="test output",
                nodes="testnode02,testnode05,"
            )
        ]
        # the node combinations are not stable
        for exp in expected:
            assert any(exp.name == act.name for act in result)
            assert any(exp.output == act.output for act in result)
            assert any(exp.returncode == act.returncode for act in result)


local_conf = {'tests': [{'name': 'Command Test', 'descr': 'a description', 'command': 'echo 6', 'conditions': {'min': 5, 'max': 7}}, {'name': 'Script Test', 'descr': 'script description', 'script': {'path': './testpath/script.sh'}}]}

class Test_LocalRunner:
    def raiseFileNotFoundError(self, process):
        process.returncode = 1
        raise FileNotFoundError("test exception raised by subprocess")

    def test_localInfo(self, capsys, fp):
        fp.register(["echo", "6"], stdout="6")
        fp.register(["./testpath/script.sh", fp.any()], stdout="test output")
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(local_conf)
        lr = LocalTestRunner(logger, config)

        lr.execute()
        captured = capsys.readouterr()
        assert "INFO - " in captured.err
        assert "Executing Basic Tests" in captured.err
        assert "[Command Test]: Executing command-test" in captured.err
        assert "[Script Test]: Executing test-script" in captured.err

    def test_localNotFoundErrorCommand(self, capsys, fp):
        fp.register(["echo", "6"], callback=self.raiseFileNotFoundError)
        fp.register(["./testpath/script.sh", fp.any()], stdout="test output")
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(local_conf)
        lr = LocalTestRunner(logger, config)

        # catch SystemExit
        with pytest.raises(SystemExit) as e:
            lr.execute()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "DEBUG - test exception raised by subprocess" in captured.err
        assert "ERROR - Unable to execute: 'echo 6'" in captured.err

    def test_localNotFoundErrorScript(self, capsys, fp):
        fp.register(["echo", "6"], stdout="6")
        fp.register(["./testpath/script.sh", fp.any()], callback=self.raiseFileNotFoundError)
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(local_conf)
        lr = LocalTestRunner(logger, config)

        # catch SystemExit
        with pytest.raises(SystemExit) as e:
            lr.execute()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "DEBUG - test exception raised by subprocess" in captured.err
        assert "ERROR - Unable to execute the script: './testpath/script.sh'" in captured.err

    def test_localCommand(self, capsys, fp):
        fp.register(["echo", "6"], stdout="6")
        fp.register(["./testpath/script.sh", fp.any()], stdout="test output")
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(local_conf)
        lr = LocalTestRunner(logger, config)

        result = lr.execute()
        expected = SingleResult(
            name='Command Test',
            nodes='local',
            output='6',
            returncode=0
        )
        assert expected in result

    def test_localScript(self, capsys, fp):
        fp.register(["echo", "6"], stdout="testecho")
        fp.register(["./testpath/script.sh", fp.any()], stdout="testtext\nline2")
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(local_conf)
        lr = LocalTestRunner(logger, config)

        result = lr.execute()
        expected = SingleResult(
            name='Script Test',
            nodes='local',
            output='testtext\nline2',
            returncode=0
        )
        assert expected in result


# vim: set et ts=4 sw=4 sts=4:
