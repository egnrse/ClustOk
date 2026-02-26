from prometheus_client.core import  REGISTRY
from prometheus_client import start_http_server, Gauge, Enum
import prometheus_client

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
        self.collectors = {}

        for test in self.config.tests:
            self.collectors[test.name] = Enum(test.name, test.descr, states=['good', 'faulty'])

            if hasattr(test, 'conditions'):
                for condition, value in test.conditions.__dict__.items():
                    name = test.name + '_' + condition
                    self.collectors[name] = Gauge(name, 'Result of the test')
                    self.collectors[name + "_success"] = Enum(name + "_success", test.descr + " Checking for: " + condition, states=['good', 'faulty'])
                    self.collectors[name + "_required"] = Gauge(name + "_required", 'Required value for: ' + name)
                    self.collectors[name + "_required"].set(value)


    def update(self, testResults):
        self.testResults = testResults

        # TODO: make this a config option
        self.config.settings.prometheus.exportStrings = True
        if self.config.settings.prometheus.exportStrings:
            exportStrings = True
        else:
            exportStrings = False

        for results in testResults:
            if 'evaluations' in results:
                for condition, evaluation in results['evaluations'].items():
                    collectorName = results["testName"] + "_" + condition
                    totalResult = True

                    self.collectors[collectorName].set(evaluation[1])

                    if evaluation[0] == True:
                        self.collectors[collectorName + "_success" ].state('good')
                    else:
                        totalResult = False
                        self.collectors[collectorName + "_success" ].state('faulty')

                if (totalResult):
                    self.collectors[results["testName"]].state('good')
                else:
                    self.collectors[results["testName"]].state('faulty')

        

            for result in results['detailedResults']:
                collectorName = results["testName"] + result["nodes"].replace(',', "")
                
                if collectorName not in self.collectors:
                    self.collectors[collectorName] = Gauge(collectorName, "Detailed results for test '" + results["testName"] + "' for nodes " +  result["nodes"])
                if exportStrings:
                    collectorNameStr = results["testName"] + result["nodes"].replace(',', "") + "_str"
                    if collectorNameStr not in self.collectors:
                        self.collectors[collectorNameStr] = Gauge(collectorNameStr, "Detailed results for test '" + results["testName"] + "' for nodes " +  result["nodes"] + " as a String", ["output"])
                    self.collectors[collectorNameStr].labels(output=str(result["output"])).set(1)

                try:
                    self.collectors[collectorName].set(result["output"])
                except (ValueError, TypeError) as e:
                    self.collectors[collectorName].set(-1)
                    if not exportStrings:
                        self.logger.debug(f"{e}")
                        self.logger.info(f"prometheus: ignoring result '{result['output']}' (NaN) from '{results['testName']}'")
   

    @staticmethod
    def init(logger: Logger, config: Config):
        exporter = PrometheusExporter(logger, config)

        exporter.logger.info('Starting prometheus server on port ' + str(config.settings.prometheus.port))
        try:
            start_http_server(config.settings.prometheus.port)
            # REGISTRY.register(exporter)
        except OSError as e:
            exporter.logger.debug(f"{e}")
            exporter.logger.error(f"Unable to start prometheus server on port '{config.settings.prometheus.port}'")
            exit(1)

        return exporter
