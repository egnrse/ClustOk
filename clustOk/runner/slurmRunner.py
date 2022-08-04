from logging import Logger
import subprocess

from psutil import Popen

class SlurmHelper:
    def __init__(self, logger: Logger, config):
        self.logger = logger
        self.config = config
        return

    def getIdleNodes(self, nodeNames):
        result = subprocess.run( [self.config.slurmdir + '/sinfo', '-hN' ,'-p', 'q_staff,q_staff_tesla', '-O', 'NodeList,StateCompact', '-n', nodeNames], stdout=subprocess.PIPE)
        nodeInfo = result.stdout.decode('utf-8').splitlines()
        nodes = *map(lambda node: tuple(node.split()), nodeInfo),
        nodes = *filter(lambda node: (node[1] not in ['down', 'drain', 'down*', 'drain*']), nodes),

        nodes = *list(map(lambda node: node[0], nodes)),

        self.logger.info("%d/%d Nodes of %s are not down or drained and availiable for the test", len(nodes), len(nodeInfo), nodeNames)
        return nodes

    def executeSlurmScriptInPairs(self, test):
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

    def executeSlurmScript(self, test):
        nodes = self.config.parseNodeNames(test['nodeLists'])
        nodes = self.getIdleNodes(nodes)

        processes = set()

        # Execute command on every specified node
        for node in nodes:
            self.logger.debug("Executing test on node %s" % node)
            processes.add(self.srun(test, node))

        return self.collectResults(processes)

    def srun(self, test, node: str):
        if ('options' in test):
            self.logger.debug(self.config.slurmdir + 'srun', *test['options'], '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path'])

            return (node, Popen([self.config.slurmdir + 'srun', *test['options'], '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path']], stdout=subprocess.PIPE))
        else:
            self.logger.debug(self.config.slurmdir + 'srun', '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path'])
            return (node, Popen([self.config.slurmdir + 'srun', '-p', 'q_staff,q_staff_tesla',  '-w', node, test['path']], stdout=subprocess.PIPE))

    def collectResults(self, processes):
        results = []

        for p in processes:
            if p[1].poll() is None:
                p[1].wait(self.config.timeout)
            results.append((p[0], p[1].poll(), p[1].communicate()[0].decode('utf-8').rstrip()))

        return results
