# some default values for the config
DEFAULTS = {
    "settings": {
        "interval": 3600,
        "timeout": -1,
        "logging": {
            "level": "WARN"
        },
        "output": {
            "file": None,
            "console": False,
            "prometheus": {
                "port": 8000,
                "enable": False,
            },
        }
    }
}

# vim: set et ts=4 sw=4 sts=4:
