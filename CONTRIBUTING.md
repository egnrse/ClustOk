# Contributing

Overview over the directory structure:
```
├─ config.example.yml         deprecated config
├─ config.yml                 example config
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
├─ testfiles/                 files for test that we use
└─ testscripts/               script for test that we use
```
