from schema import Schema, SchemaError, Or, Optional

 
nodeList_schema = Schema({
    object: {
        "nodeNames": str
    }
}, name="nodeLists")

settings_schema = Schema({
    Optional("interval"): int,
    Optional("timeout"): int,
    "slurm": {
        "dir": str,
        Optional("partition"): str,
        Optional("args"): [str],
    },
    Optional("output"): {
		Optional("file"): {
			"dir": str,
			"fileName": str,
			"format": Or("pretty", "json"),
		},
		Optional("console"): bool,
		Optional("prometheus"): {
			"port": int,
			"enable": bool
		},
    },
    Optional("logging"): {
        "level": Or("INFO", "DETAIL", "DEBUG", "CRITICAL", "ERROR", "WARN")
    }
}, name="settings")


conditions_schema = Schema({
    Optional("min"): Or(float, int),
    Optional("max"): Or(float, int),
    Optional("difference"): Or(float, int)
    #Optional("lessThen"): int,
    #Optional("greaterThen"): int,
    #Optional("equalTo"): int
}, name="conditions")

script_test = Schema({
    "name": str,
    Optional("descr"): str,
    "script": {"path": str},
    Optional("conditions"): {
        Optional("min"): Or(int, float),
        Optional("max"): Or(int, float),
    }
}, name="script test")

command_test = Schema({
    "name": str,
    Optional("descr"): str,
    "command": str,
    Optional("conditions"): {
        Optional("min"): Or(int, float),
        Optional("max"): Or(int, float),
    }
}, name="command test")

slurm_test = Schema({
    "name": str,
    Optional("descr"): str,
    "slurmScript": {
        "path": str,
        "nodeLists": str,
        Optional("options"): [str],
    },
    Optional("conditions"): Or(
        conditions_schema,
        [ conditions_schema ]
    ),
}, name="slurmPair test")

slurm_pair_test = Schema({
    "name": str,
    Optional("descr"): str,
    "slurmPairScript": {
        "path": str,
        "pairSize": int,
        "nodeLists": str,
        Optional("options"): [str],
    },
    Optional("conditions"): Or(
        conditions_schema,
        [ conditions_schema ]
    ),
}, name="slurmPairScript test")

test_schema = Or(
    script_test,
    command_test,
    slurm_test,
    slurm_pair_test,
    error="Invalid test(s)! See -vv for more details." 
)

# schema for the config file
config_schema = Schema({
    "settings": settings_schema,
    "nodeLists": nodeList_schema,
    "tests": [ test_schema ],
})

# vim: set et ts=4 sw=4 sts=4:
