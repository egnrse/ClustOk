#!/usr/bin/python

import time, fire, logging

from typing import List, Dict
from interfaces.runner import Runner
from interfaces.evaluator import Evaluator
from interfaces.exporter import Exporter
from interfaces.testresult import SingleResult
from utils.config.config import Config

from runner.localRunner import LocalTestRunner
from runner.slurmRunner import SlurmTestRunner
from evaluator.baseEvaluator import BaseEvaluator
from exporter.consoleExporter import ConsoleExporter
from exporter.fileExporter import FileExporter
from exporter.prometheusExporter import PrometheusExporter
from utils.config.configManager import ConfigManager
from utils.logger.customLogger import CustomLogger


# Called by fire after handling arguments
def realmain(config:str="/etc/clustok/config.yml", repeat:bool=False, v:bool=False, vv:bool=False) -> None:
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
    cfg: Config = configManager.config
    settings = cfg.settings

    if (not v and not vv):
        logger.setLevel(settings.logging.level)

    evaluators.append(BaseEvaluator(logger, cfg))
    runners.append(LocalTestRunner(logger, cfg))
    runners.append(SlurmTestRunner(logger, cfg))

    if (cfg.settings.output.prometheus.enable):
        exporters.append(PrometheusExporter.init(logger, cfg))
    if (cfg.settings.output.console):
        exporters.append(ConsoleExporter.init(logger, settings.output))
    if (cfg.settings.output.file is not None):
        exporters.append(FileExporter.init(logger, settings.output.file))
    if len(exporters) <= 0:
        logger.warn("No output type active (eg.: file/console/prometheus)")

    # Main Loop
    while True:
        results: Dict[str, List[SingleResult]] = {}

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

        logger.info("Waiting %d seconds", cfg.settings.interval)
        time.sleep(cfg.settings.interval)

    for exporter in exporters:
        exporter.destroy()

# Handle arguments
def main() -> None:
    fire.Fire(realmain)

# vim: set et ts=4 sw=4 sts=4:
