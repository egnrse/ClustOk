# testing evaluater
import pytest, logging
import copy

from interfaces.testresult import SingleResult, TestResult

from utils.logger.customLogger import CustomLogger
from utils.config.config import DictToConf
from evaluator.baseEvaluator import BaseEvaluator

eval_conf = {'tests': [{'name': 'Test min/max', 'descr': '', 'command': 'echo 6', 'conditions': {'min': 5, 'max': 7}}, {'name': 'Script Test', 'descr': 'Executes a script', 'script': {'path': './testscripts/datetest.sh'}}]}
eval_input1 = {"Test min/max": [SingleResult(name="Test min/max", returncode=0, output="6", nodes="local")]}

class Test_BaseEvaluater:
    # set 'output' values in the input structure
    def setInput(self, input, value):
        out = copy.deepcopy(input)
        if isinstance(out, dict):
            for k,v in out.items():
                if k == "output":
                    out[k] = value
                else:
                    out[k] = self.setInput(v, value)
        elif isinstance(out, list):
            out = [self.setInput(item, value) for item in out]
        elif isinstance(out, SingleResult):
            if hasattr(out, "output"):
                out.output = value
        return out

    def test_detailedResults(self):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        result = ev.evaluate(eval_input1)
        assert isinstance(result[0], TestResult)
        #assert "detailedResults" in result[0]
        assert len(result[0].detailedResults) > 0
        assert isinstance(result[0].detailedResults[0], SingleResult)

    def test_Min1(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        result = ev.evaluate(eval_input1)
        expected = (True, 6.0, 5, None)
        assert result[0].evaluations is not None
        assert "min" in result[0].evaluations
        assert result[0].evaluations['min'] == expected

        captured = capsys.readouterr()
        assert "DEBUG - " in captured.err
        assert "Minimum result is 6" in captured.err
        assert "out of required 5" in captured.err

    def test_Min2(self):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        input = self.setInput(eval_input1, 5)
        result = ev.evaluate(input)
        expected = (True, 5.0, 5, None)
        assert result[0].evaluations is not None
        assert "min" in result[0].evaluations
        assert result[0].evaluations['min'] == expected

    def test_Min3(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        input = self.setInput(eval_input1, 4)
        result = ev.evaluate(input)
        expected = (False, 4.0, 5, 'Min value threshold violated. 4.0 instead of 5')
        assert result[0].evaluations is not None
        assert "min" in result[0].evaluations
        assert result[0].evaluations['min'] == expected

        captured = capsys.readouterr()
        assert "WARNING - " in captured.err
        assert "Min value threshold violated" in captured.err


    def test_Max1(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        input = self.setInput(eval_input1, 10230)
        result = ev.evaluate(input)
        expected = (False, 10230.0, 7, 'Max value threshold violated. 10230.0 instead of 7')
        assert result[0].evaluations is not None
        assert "max" in result[0].evaluations
        assert result[0].evaluations['max'] == expected

        captured = capsys.readouterr()
        assert "DEBUG - " in captured.err
        assert "Maximum result is 10230" in captured.err
        assert "instead of 7" in captured.err
        assert "WARNING - " in captured.err
        assert "Max value threshold violated" in captured.err

    def test_Max2(self, capsys):
        logger = CustomLogger('[ClustOk]')
        logger.setLevel(logging.DEBUG)
        config = DictToConf(eval_conf)
        ev = BaseEvaluator(logger, config)

        input = self.setInput(eval_input1, -10)
        result = ev.evaluate(input)
        expected = (True, -10, 7, None)
        assert result[0].evaluations is not None
        assert "max" in result[0].evaluations
        assert result[0].evaluations['max'] == expected

        captured = capsys.readouterr()
        assert "DEBUG - " in captured.err
        assert "Maximum result is -10" in captured.err
        assert "of allowed 7" in captured.err

    @pytest.mark.skip(reason="test not implemented")
    def test_Diff(self):
        assert False
        

# vim: set et ts=4 sw=4 sts=4:
