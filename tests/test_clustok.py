# testing the main function of clustok
import pytest
from pathlib import Path

from clustok.clustok import realmain as co


#example_conf = {'settings': {'interval': 3600, 'timeout': 1000, 'slurm': {'dir': '/usr/local/slurm/bin/', 'partition': 'q_staff', 'args': ['--comment="clustok job"']}, 'output': {'dir': './', 'fileName': 'log', 'format': 'json'}, 'logging': {'level': 'INFO'}, 'prometheus': {'enable': False, 'port': 8000}}, 'nodeLists': {'hydraCompute': {'nodeNames': 'hydra[01-5]'}}, 'tests': [{'name': 'Command Test', 'descr': 'An optional description', 'command': 'echo 6', 'conditions': {'min': 5, 'max': 7}}, {'name': 'Script Test', 'descr': 'Executes a script', 'script': {'path': './testscripts/datetest.sh'}}]}

def test_invalid_conf1(capsys):
    with pytest.raises(SystemExit):
        co(config="")
    captured = capsys.readouterr()
    assert "ERROR - " in captured.err
    assert "Config file not found: " in captured.err

# tests if ../config.yml is valid
def test_validConfigRun(fp, monkeypatch, tmp_path):
    base_dir = Path(__file__).resolve().parent
    CONFIG = base_dir / "../config.yml"

    import builtins, json
    REAL_OPEN = builtins.open

    # patch prometheusExporter (avoids REGISTRY/port collisions)
    class PrometheusPatch:
        def __init__(self, logger, config):
            pass
        def update(self, _):
            pass
        def destroy(self):
            pass

    def mock_open(file, mode="e", *args, **kwargs):
        # read actial config file
        if "config.yml" in str(file) and "r" in mode:
            return REAL_OPEN(file, mode, *args, **kwargs)
        # write files to tmp_path
        if "w" in mode:
            filename = file.split("/")[-1]
            return REAL_OPEN(tmp_path / filename, mode, *args, **kwargs)
        # allow special dirs
        if str(file).startswith("/proc") or str(file).startswith("/dev"):
            return REAL_OPEN(file, mode, *args, **kwargs)
        # return nothing, else
        return ""

    # patch stuff
    from exporter.prometheusExporter import PrometheusExporter
    monkeypatch.setattr(PrometheusExporter, 'init', PrometheusPatch)
    monkeypatch.setattr(builtins, 'open', mock_open)

    fp.register(["echo", "6"], stdout="6")
    fp.register(["./example/testscripts/succeedscript.sh"], stdout="")
    # fp did not handle '//' well
    fp.register([fp.program("sinfo"), "-hN", fp.any(min=4)], stdout="hydra01\t\tidle\nhydra02\t\tidle\nhydra03\t\tidle\nhydra04\t\tidle\nhydra05\t\tidle\n")
    fp.register([fp.program("srun"), fp.any(min=2)], stdout="15\n25")
    fp.keep_last_process(True)

    # run
    co(config=CONFIG, repeat=False, v=True, vv=True)

    # test if output exists and is proper json
    matches = list(tmp_path.glob("*.json"))
    for f in matches:
        json.loads(f.read_text())
    assert matches, "no '*.json' file found"

# vim: set et ts=4 sw=4 sts=4:
