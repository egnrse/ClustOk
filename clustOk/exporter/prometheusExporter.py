from prometheus_client.core import  REGISTRY
from prometheus_client import start_http_server, Gauge, Enum
import prometheus_client

from logging import Logger

from interfaces.exporter import Exporter

REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

class PrometheusExporter(Exporter):
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.collectors = {}

        for test in self.config.tests:
            self.collectors[test["name"]] = Enum(test["name"], test.get("descr", ''), states=['good', 'faulty'])

            if "conditions" in test:
                for condition in test["conditions"]:
                    name = test["name"] + '_' + condition
                    self.collectors[name] = Gauge(name, 'Required: ' + str(test["conditions"][condition]))

    def collect(self):
      # nothing
      print('what')


    def update(self, testResults):
        self.testResults = testResults

        for test in self.config.tests:
            result = testResults[test["name"]]
            if (result["evaluation"] <= 0):
                self.collectors[test["name"]].state('good')
            else:
                self.collectors[test["name"]].state('faulty')

            if "conditions" in test:
                for condition in test["conditions"]:
                    name = test["name"] + '_' + condition
                    self.collectors[name].set(result["summary"][condition])       

    @staticmethod
    def init(logger: Logger, config):
        exporter = PrometheusExporter(logger, config)

        exporter.logger.info('Starting prometheus server on port ' + str(config.prometheus['port']))
        start_http_server(config.prometheus['port'])
        # REGISTRY.register(exporter)
        return exporter