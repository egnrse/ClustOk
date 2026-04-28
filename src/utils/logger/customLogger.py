import logging


class Color:
    """A class for terminal color codes."""

    BOLD = "\033[1m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_WHITE = BOLD + WHITE
    BOLD_BLUE = BOLD + BLUE
    BOLD_GREEN = BOLD + GREEN
    BOLD_YELLOW = BOLD + YELLOW
    BOLD_RED = BOLD + RED
    END = "\033[0m"

class CustomFormatter(logging.Formatter):
    reset = "\x1b[0m"
    prefix = "%(asctime)s - %(name)s "
    formatStr = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: prefix + Color.WHITE + formatStr + reset,
        logging.INFO: prefix + Color.GREEN + formatStr + reset,
        logging.WARNING: prefix + Color.YELLOW + formatStr + reset,
        logging.ERROR: prefix + Color.RED + formatStr + reset,
        logging.CRITICAL: prefix + Color.BOLD_RED + formatStr + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class CustomLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.WARNING)                

        console = logging.StreamHandler()
        console.setFormatter(CustomFormatter())

        self.propagate = False
        self.addHandler(console)

        logging.basicConfig()  
        logging.setLoggerClass(CustomLogger)

        return

# vim: set et ts=4 sw=4 sts=4:
