
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
    format = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: prefix + Color.WHITE + format + reset,
        logging.INFO: prefix + Color.GREEN + format + reset,
        logging.WARNING: prefix + Color.YELLOW + format + reset,
        logging.ERROR: prefix + Color.RED + format + reset,
        logging.CRITICAL: prefix + Color.BOLD_RED + format + reset
    }

    def format(self, record):
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