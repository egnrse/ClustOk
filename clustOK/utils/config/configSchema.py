from schema import Schema, SchemaError, Or, Optional

config_schema = Schema({
    "nodeLists": {
        object: {
            "nodeNames": str
        }
    },

    "tests": [
        Or({
            "name": str,
            Optional("descr"): str,
            "script": {
                "path": str
            },
            Optional("conditions"): 
                {
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int)
                    
                }
        },
        {
            "name": str,
            Optional("descr"): str,
            "command": str,
            Optional("conditions"): 
                {
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int)
                    
                }
        },
        {
            "name": str,
            Optional("descr"): str,
            "slurmScript": {
                "path": str,
                "nodeLists": str,
                Optional("options"): [
                    str
                ]
            },
            Optional("conditions"): 
                Or({
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int),
                    Optional("difference"): Or(float, int)
                    
                },
                [{
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int),
                    Optional("difference"): Or(float, int),
                    #Optional("lessThen"): int,
                    #Optional("greaterThen"): int,
                    #Optional("equalTo"): int
                    
                }])
        },
        {
            "name": str,
            Optional("descr"): str,
            "slurmPairScript": {
                "path": str,
                "pairSize": int,
                "nodeLists": str,
                Optional("options"): [
                    str
                ]
            },
            Optional("conditions"): 
                Or({
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int),
                    Optional("difference"): Or(float, int)
                    
                },
                [{
                    Optional("min"): Or(float, int),
                    Optional("max"): Or(float, int),
                    Optional("difference"): Or(float, int),
                    #Optional("lessThen"): int,
                    #Optional("greaterThen"): int,
                    #Optional("equalTo"): int
                    
                }])
        },
        error="Test must be one of command, script, slurmscript or slurmPairScript"
        )
    ],
    "settings": {
        "interval": int,
        "timeout": int,
        "slurmdir": str,
        Optional("output"): {
            "dir": str,
            "fileName": str,
            "format": Or("pretty", "json")
        },
        "prometheus": {
            "port": int,
            "enable": bool
        },
        "logging": {
            "level": Or("INFO", "DEBUG", "CRITICAL", "ERROR", "WARN")
        }
    }
})