import prometheus_client, math
from prometheus_client.core import  REGISTRY
from prometheus_client import start_http_server, Gauge, Enum

from logging import Logger
from interfaces.exporter import Exporter
from utils.config.config import Config


REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

class PrometheusExporter(Exporter):
    def __init__(self, logger, config: Config):
        self.logger = logger
        self.config = config
        self.gauges: dict[str, Gauge] = {}
        self.enums: dict[str, Enum] = {}

        for test in self.config.tests:
            self.enums[test.name] = Enum(test.name, test.descr, states=['good', 'faulty'])

            if hasattr(test, 'conditions'):
                for condition, value in test.conditions.__dict__.items():
                    name = test.name + '_' + condition
                    self.gauges[name] = Gauge(name, 'Result of the test')
                    self.enums[name + "_success"] = Enum(name + "_success", test.descr + " Checking for: " + condition, states=['good', 'faulty'])
                    self.gauges[name + "_required"] = Gauge(name + "_required", 'Required value for: ' + name)
                    self.gauges[name + "_required"].set(value)


    def update(self, testResults):
        self.testResults = testResults

        # TODO: make this a config option
        self.config.settings.output.prometheus.exportStrings = True
        if self.config.settings.output.prometheus.exportStrings:
            exportStrings = True
        else:
            exportStrings = False

        for results in testResults:
            if results.evaluations is not None:
                for condition, evaluation in results.evaluations.items():
                    collectorName = results.testName + "_" + condition
                    totalResult = True

                    if evaluation[1] is not None:
                        self.gauges[collectorName].set(evaluation[1])
                    else:
                        self.gauges[collectorName].set(math.nan)
                        self.logger.debug("prometheus: ignoring %s evaluation value from test '%s' (NaN)", condition, results.testName)

                    if evaluation[0] == True:
                        self.enums[collectorName + "_success" ].state('good')
                    else:
                        totalResult = False
                        self.enums[collectorName + "_success" ].state('faulty')

                if (totalResult):
                    self.enums[results.testName].state('good')
                else:
                    self.enums[results.testName].state('faulty')

        

            for result in results.detailedResults:
                collectorName = results.testName + result.nodes.replace(',', "")
                
                if collectorName not in self.gauges:
                    self.gauges[collectorName] = Gauge(collectorName, "Detailed results for test '" + results.testName + "' for nodes " +  result.nodes)
                if exportStrings:
                    collectorNameStr = results.testName + result.nodes.replace(',', "") + "_str"
                    if collectorNameStr not in self.gauges:
                        self.gauges[collectorNameStr] = Gauge(collectorNameStr, "Detailed results for test '" + results.testName + "' for nodes " +  result.nodes + " as a String", ["output"])
                    self.gauges[collectorNameStr].labels(output=str(result.output)).set(1)

                try:
                    self.gauges[collectorName].set(result["output"])
                except (ValueError, TypeError) as e:
                    self.gauges[collectorName].set(math.nan)
                    if not exportStrings:
                        self.logger.debug(f"{e}")
                        self.logger.info(f"prometheus: ignoring result '{result['output']}' (NaN) from '{results.testName}'")
   

    @staticmethod
    def init(logger: Logger, config: Config):
        exporter = PrometheusExporter(logger, config)

        exporter.logger.info('Starting prometheus server on port ' + str(config.settings.output.prometheus.port))
        try:
            start_http_server(config.settings.output.prometheus.port)
            # REGISTRY.register(exporter)
        except OSError as e:
            exporter.logger.debug(f"{e}")
            exporter.logger.error(f"Unable to start prometheus server on port '{config.settings.output.prometheus.port}'")
            exit(1)

        return exporter

# vim: set et ts=4 sw=4 sts=4:
