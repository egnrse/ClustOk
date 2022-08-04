from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

from interfaces.exporter import Exporter

class PrometheusExporter(Exporter):
    def __init__(self):
        self.testResults = 0

    def collect(self):
        server_status = self.testResults     ## place the logic here to get the server status
        cpu_usage = 7  		  ## place the logic here to get the CPU Usage.
        value = CounterMetricFamily("SERVER_STATUS", 'Help text', labels='value')
        value.add_metric(["server_status"], server_status)
        yield value

    def update(self, testResults: int):
        self.testResults = testResults

    @staticmethod
    def init():
        exporter = PrometheusExporter()
        start_http_server(9005)
        REGISTRY.register(exporter)
        return exporter