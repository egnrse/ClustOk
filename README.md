# ClustOk

An universal cluster monitoring tool, that allows to easily execute arbitrary test-scripts.


## Installing
(On some distros you might need to replace `pip` with `pipx`.)

You need `python3` and `pip` (or `pipx`) installed on your system.

Then clone the repo and cd into it:
```sh
git clone https://hellogitty.par.tuwien.ac.at/sysadmin/clustok.git
cd clustok
```

Afterwards run:
```sh
pip install build
python -m build
pip install dist/clustok-*.whl
```

To install this package in development mode, instead run:  
```sh
pip install -e .
```


Deprecated (ONLY before v0.2.0):
```sh
python setup.py install
```


## Usage

```
SYNOPSIS
    clustok <flags>

FLAGS
    -c, --config=CONFIG
        Default: '/etc/clustok/config.yml'
    -r, --repeat         (continuous execution)
    -v, -vv              (set log level to info/debug)
    -h, --help           (show a help menu)
```


## Config
For an example config look at [config.yml](./config.yml).
