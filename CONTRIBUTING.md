# Contributing

Overview over the directory structure:
```
├─ config.yml                 example config
├─ example/                   files for tests that we use
├─ pyproject.toml             project packageing information
├─ src/                       program source code
│  ├─ clustok/
│  │  └─ clustok.py           main project file
│  ├─ evaluator/              constrain evaluators for the test
│  ├─ interfaces/             some class interfaces
│  ├─ runner/                 the runners/executers for the tests
│  └─ utils
│     ├─ config/              config file reader
│     └─ logger/              custom logger
└─ tests/                     unit tests
```

## Install (dev)
You might want to use a virtual environment:  
```sh
# create a venv (in the current location)
python -m venv .venv
# actiave the venv
source .venv/bin/activate
# to deactivate a venv again run 'deactivate'
```

To install the package in development mode  
run the following in the root of the repo:  
```sh
pip install -e .
```

To create and install a release build run:  
```sh
python -m build
pip install dist/clustok-*.whl
```

## Tests
There are some unit-tests in the [tests/](./tests/) directory.

```sh
# install modules needed for the unit-tests
pip install -U .[test]
# run the tests
pytest
```

