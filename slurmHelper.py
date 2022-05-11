from logging import Logger
import subprocess

from psutil import Popen
from configManager import Config

from test import SlurmScript

class SlurmHelper:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        return

    def fetchNodeInfo(self, nodeNames):
        result = subprocess.run( [self.config.slurmdir + '/sinfo', '-hN' ,'-p', 'q_staff,q_staff_tesla', '-O', 'NodeList,StateCompact', '-n', nodeNames], stdout=subprocess.PIPE)
        nodeInfo = result.stdout.decode('utf-8').splitlines()

        nodes = []

        for info in nodeInfo:
            nodes.append(tuple(info.split()))

        return nodes

    def getIdleNodes(self, nodeNames):
        nodeInfo = self.fetchNodeInfo(nodeNames)
        return list(map(lambda node: node[0], list(filter(lambda node: node[1] == 'idle', nodeInfo))))

    
    def executeSlurmScript(self, test: SlurmScript):
        nodes = self.config.parseNodeNames(test['slurmScript']['nodeLists'])
        nodes = self.getIdleNodes(nodes)

        processes = set()
        results = []

        # Execute command on every specified node
        for node in nodes:
            #self.logger.debug("Executing test on node %s" % node)
            if ('options' in test['slurmScript']):
                processes.add((node, Popen([self.config.slurmdir + 'srun', *test['slurmScript']['options'], '-p', 'q_staff,q_staff_tesla',  '-w', node, test['slurmScript']['path']], stdout=subprocess.PIPE)))
            else:
                processes.add((node, Popen([self.config.slurmdir + 'srun', '-p', 'q_staff,q_staff_tesla',  '-w', node, test['slurmScript']['path']], stdout=subprocess.PIPE)))


        # Collect results
        for p in processes:
            if p[1].poll() is None:
                p[1].wait(self.config.timeout)
            results.append((p[0], p[1].poll(), p[1].communicate()[0].decode('utf-8')))

        return results