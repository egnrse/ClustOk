# testing the main function of clustok
import pytest
from clustok.clustok import realmain as co

def test_invalid_conf1(capsys):
    with pytest.raises(SystemExit):
        co(config="")
    captured = capsys.readouterr()
    assert "ERROR - " in captured.err
    assert "Config file not found: " in captured.err


@pytest.mark.skip(reason="test not implemented")
def test_todo():
    assert False
    #co(config="./test_conf.yml", repeat=False, v=True, vv=True)

# vim: set et ts=4 sw=4 sts=4:
