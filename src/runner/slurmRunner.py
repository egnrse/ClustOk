from logging import Logger
import subprocess

from psutil import Popen
from typing import List
from pathlib import Path
from functools import reduce

from interfaces.runner import Runner
from utils.config.config import Config
from interfaces.test import SlurmScriptPairTest, SlurmScriptTest, SlurmPairScript, SlurmScript
from interfaces.testresult import SingleResult


class SlurmTestRunner(Runner):
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        self.slurmHelper = SlurmHelper(logger, config)

        # test if slurm binaries exists
        slurmdir = self.config.settings.slurm.dir
        try:
            open(f"{slurmdir}/srun", 'r')
            open(f"{slurmdir}/sinfo", 'r')
        except FileNotFoundError as e:
            self.logger.debug(f"{e}")
            self.logger.warning(f"Slurm binaries not found in: '{slurmdir}'")
            #exit(1)

        return

    def execute(self) -> List[SingleResult]:
        self.logger.info('Executing Slurm Tests...')
        results = []

        for test in self.config.tests:
            summary = {}          
            
            if hasattr(test, 'slurmScript'):
                slurmScriptTest: SlurmScriptTest = test
                self.logger.info('[%s]: Executing slurmScript-test..' % slurmScriptTest.name)
                result = self.slurmHelper.executeSlurmScript(slurmScriptTest.slurmScript, test.name)
                results.extend(result)

            elif hasattr(test, 'slurmPairScript'):
                slurmPairScript: SlurmScriptPairTest = test
                self.logger.info('[%s]: Executing slurm test-script in pairs..' % slurmPairScript.name)
                result = self.slurmHelper.executeSlurmScriptInPairs(slurmPairScript.slurmPairScript, test.name)
                results.extend(result)

        return results


class SlurmHelper:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        return

    def getIdleNodes(self, nodeNames):
        cmd = [self.config.settings.slurm.dir + '/sinfo',
                '-hN',
                '-O', 'NodeList,StateCompact',
                '-n', nodeNames
        ]
        if hasattr(self.config.settings.slurm, 'partition'):
            cmd.append("-p")
            cmd.append(self.config.settings.slurm.partition)
        #self.logger.debug("cmd: %s", cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        nodeInfo = result.stdout.decode('utf-8').splitlines()
        nodes = *map(lambda node: tuple(node.split()), nodeInfo),
        nodes = *filter(lambda node: (node[1] not in ['down', 'drain', 'down*', 'drain*', 'boot^', 'boot^*', 'boot*']), nodes),

        nodes = *list(map(lambda node: node[0], nodes)),

        self.logger.info("%d/%d Nodes of %s are available for the test", len(nodes), len(nodeInfo), nodeNames)
        return nodes

    def srun(self, test, node: str, name: str=""):
        jobName="ClustOk "+name
        cmd = [self.config.settings.slurm.dir + '/srun',
                '-J', jobName,
                '-w', node,
        ]

        # handle optional arguments
        if hasattr(self.config.settings.slurm, 'partition'):
            cmd.append("-p")
            cmd.append(self.config.settings.slurm.partition)
        if hasattr(self.config.settings.slurm, 'args'):
            cmd.extend(self.config.settings.slurm.args)
        if hasattr(test, 'options'):
            cmd.extend(test.options)

        fullPath = Path(test.path).resolve()
        cmd.append(fullPath)
        #self.logger.debug("cmd: %s", cmd)

        return node, Popen(cmd, stdout=subprocess.PIPE)

    def collectResults(self, processes, testName):
        results = []

        for p in processes:
            if p[1].poll() is None:
                p[1].wait(self.config.settings.timeout)
            singleResult = { "name": testName, "returncode": 0, "output": p[1].communicate()[0].decode('utf-8').rstrip(), "nodes": p[0]}
            results.append(singleResult)

        return results

    def executeSlurmScriptInPairs(self, test: SlurmPairScript, name: str) -> List[SingleResult]:
        nodes = self.parseNodeNames(test.nodeLists)
        nodes = self.getIdleNodes(nodes)

        if test.pairSize > len(nodes):
            self.logger.warning("pairSize cant be greater than the amount of available nodes: %i > %i", test.pairSize, len(nodes))
            test.pairSize = len(nodes)
        if test.pairSize < 1:
            self.logger.warning("pairSize cant be smaller than 1: %i < 1", test.pairSize)
            test.pairSize = 1


        processes = set()

        for i in range(0, len(nodes) // test.pairSize):
            nodePair = ''

            for j in range(0, test.pairSize):
                nodePair += nodes[(len(nodes) // test.pairSize) * j + i] + ',' 

            self.logger.debug("Executing test on node-pair %s", nodePair)
            processes.add(self.srun(test, nodePair, name))

        if len(nodes) % test.pairSize != 0:
            nodePair = ''
            for j in range(1, test.pairSize +1):
                nodePair += nodes[-j] + ',' 

            self.logger.debug("Executing test on node-pair %s (extra) ", nodePair)
            processes.add(self.srun(test, nodePair, name))

        return self.collectResults(processes, name)

    def executeSlurmScript(self, test: SlurmScript, name: str) -> List[SingleResult]:
        nodes = self.parseNodeNames(test.nodeLists)
        nodes = self.getIdleNodes(nodes)

        processes = set()

        # Execute command on every specified node
        for node in nodes:
            self.logger.debug("Executing test on node %s" % node)
            processes.add(self.srun(test, node, name))

        return self.collectResults(processes, name)

    def parseNodeNames(self, nodeLists):
        lists = nodeLists.split(',')

        if len(lists) <= 1:
            return getattr(self.config.nodeLists, lists[0]).nodeNames
        
        return reduce(lambda a, b: getattr(self.config.nodeLists, lists[a]).nodeNames + ',' + getattr(self.config.nodeLists, lists[b]).nodeNames, lists)


