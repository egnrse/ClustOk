# ClustOk

An universal cluster monitoring tool, that allows to easily execute arbitrary test-scripts.


## Installing
You need `python3` and `pip` (or `pipx`) installed on your system.

Then clone the repo, cd into it and install the package:
```sh
git clone https://hellogitty.par.tuwien.ac.at/sysadmin/clustok.git
cd clustok
pip install -U .
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
