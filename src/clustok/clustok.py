#!/usr/bin/python

import time, fire, logging

from typing import List
from interfaces.runner import Runner
from interfaces.evaluator import Evaluator
from interfaces.exporter import Exporter

from runner.localRunner import LocalTestRunner
from runner.slurmRunner import SlurmTestRunner
from evaluator.baseEvaluator import BaseEvaluator
from exporter.consoleExporter import ConsoleExporter
from exporter.fileExporter import FileExporter
from exporter.prometheusExporter import PrometheusExporter
from utils.config.configManager import ConfigManager
from utils.logger.customLogger import CustomLogger


# Called by fire after handling arguments
def realmain(config="/etc/clustok/config.yml", repeat=False, v=False, vv=False):
    exporters: List[Exporter] = []
    runners: List[Runner] = []
    evaluators: List[Evaluator] = []
    
    # Setup Logger
    logger = CustomLogger('[ClustOk]')

    if (v):
        logger.setLevel(logging.INFO)
    elif (vv):
        logger.setLevel(logging.DEBUG)

    # Load Config
    configManager = ConfigManager(logger, config)
    config = configManager.config
    settings = config.settings

    if (not v and not vv):
        logger.setLevel(settings.logging.level)

    evaluators.append(BaseEvaluator(logger, config))
    runners.append(LocalTestRunner(logger, config))
    runners.append(SlurmTestRunner(logger, config))

    if (config.settings.output.prometheus.enable):
        exporters.append(PrometheusExporter.init(logger, config))
    if (config.settings.output.console):
        exporters.append(ConsoleExporter.init(logger, settings.output))
    if (config.settings.output.file is not None):
        exporters.append(FileExporter.init(logger, settings.output.file))
    if len(exporters) <= 0:
        logger.warn("No output type active (eg.: file/console/prometheus)")

    # Main Loop
    while True:
        results: dict = {}

        # Execute tests
        for runner in runners:
            result = runner.execute()

            # Collect results
            for singleResult in result:
                if singleResult.name not in results:
                    results[singleResult.name] = []

                results[singleResult.name].append(singleResult)
            
        for _,resultList in results.items():
            resultList.sort(key=lambda result: result.nodes)

        # Evaluate results
        for evaluator in evaluators:
            resultsWithEvaluation = evaluator.evaluate(results) # Right now basically only one evaluator is working. If more are to come I need to merge results

        # Update exporters
        for exporter in exporters:
            exporter.update(resultsWithEvaluation)
    
        if not repeat:
            break

        logger.info("Waiting %d seconds", config.settings.interval)
        time.sleep(config.settings.interval)

    for exporter in exporters:
        exporter.destroy()

# Handle arguments
def main():
    fire.Fire(realmain)

# vim: set et ts=4 sw=4 sts=4:
