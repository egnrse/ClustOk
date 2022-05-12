from logging import Logger
from platform import node
import subprocess

from psutil import Popen
from configManager import Config

from test import SlurmPairScript, SlurmScript

class SlurmHelper:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        return

    def fetchNodeInfo(self, nodeNames):
        result = subprocess.run( [self.config.slurmdir + '/sinfo', '-hN' ,'-p', 'q_staff,q_staff_tesla', '-O', 'NodeList,StateCompact', '-n', nodeNames], stdout=subprocess.PIPE)
        nodeInfo = result.stdout.decode('utf-8').splitlines()
        nodes = *map(lambda node: tuple(node.split()), nodeInfo),

        self.logger.info("%d/%d Nodes of %s are idle and availiable for the test", len(nodes), len(nodeInfo), nodeNames)

        return nodes

    def getIdleNodes(self, nodeNames):
        nodeInfo = self.fetchNodeInfo(nodeNames)
        return list(map(lambda node: node[0], list(filter(lambda node: node[1] == 'idle', nodeInfo))))

    def executeSlurmScriptInPairs(self, test: SlurmPairScript):
        nodes = self.config.parseNodeNames(test['nodeLists'])
        nodes = self.getIdleNodes(nodes)

        processes = set()

        for i in range(0, len(nodes) // test['pairSize']):
            nodePair = ''

            for j in range(0, test['pairSize']):
                nodePair += nodes[(len(nodes) // test['pairSize']) * j + i] + ',' 

            self.logger.debug("Executing test on node-pair %s", nodePair)
            processes.add(self.srun(test, nodePair))

        if len(nodes) % test['pairSize'] != 0:
            nodePair = ''
            for j in range(1, test['pairSize'] +1):
                nodePair += nodes[-j] + ',' 

            self.logger.debug("Executing test on node-pair %s (extra) ", nodePair)
            processes.add(self.srun(test, nodePair))

        return self.collectResults(processes)

    def executeSlurmScript(self, test: SlurmScript):
        nodes = self.config.parseNodeNames(test['nodeLists'])
        nodes = self.getIdleNodes(nodes)

        processes = set()

        # Execute command on every specified node
        for node in nodes:
            self.logger.debug("Executing test on node %s" % node)
            processes.add(self.srun(test, node))

        return self.collectResults(processes)

    def srun(self, test: SlurmScript, node: str):
        if ('options' in test):
            return (node, Popen([self.config.slurmdir + 'srun', *test['options'], '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path']], stdout=subprocess.PIPE))
        else:
            return (node, Popen([self.config.slurmdir + 'srun', '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path']], stdout=subprocess.PIPE))

    def collectResults(self, processes):
        results = []

        for p in processes:
            if p[1].poll() is None:
                p[1].wait(self.config.timeout)
            results.append((p[0], p[1].poll(), p[1].communicate()[0].decode('utf-8')))

        return results
