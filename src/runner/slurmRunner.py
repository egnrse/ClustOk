import subprocess, time
from pathlib import Path
from functools import reduce

from typing import List, Tuple, Set, cast
from logging import Logger
from interfaces.runner import Runner
from interfaces.test import SlurmScriptPairTest, SlurmScriptTest, SlurmPairScript, SlurmScript
from interfaces.testresult import SingleResult
from utils.config.config import Config


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
            if hasattr(test, 'slurmScript'):
                slurmScriptTest = cast(SlurmScriptTest, test)
                self.logger.info('[%s]: Executing slurmScript-test..' % slurmScriptTest.name)
                result = self.slurmHelper.executeSlurmScript(slurmScriptTest.slurmScript, test.name)
                results.extend(result)

            elif hasattr(test, 'slurmPairScript'):
                slurmPairScript: SlurmScriptPairTest =  cast(SlurmScriptPairTest, test)
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
        cmd.append(str(fullPath))
        #self.logger.debug("cmd: %s", cmd)

        return node, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def collectResults(self, processes: Set[Tuple[str, subprocess.Popen]], testName: str) -> List[SingleResult]:
        results = []
        timeout = self.config.settings.timeout
        startTime = time.monotonic()

        for n,p in processes:
            if p.poll() is None:
                if timeout < 0:
                    p.wait()
                else:
                    elapsed = time.monotonic() - startTime
                    remaining = timeout - elapsed
                    try:
                        if remaining <= 0:
                            raise subprocess.TimeoutExpired(cmd=p.args, timeout=timeout, output=None, stderr=None)
                        p.wait(remaining)
                    except subprocess.TimeoutExpired:
                        self.logger.warning("Terminating process '%s:%s' (timeout)", testName, n);
                        p.terminate()

            returncode = p.returncode
            if returncode == None:
                returncode = 124    # returncode for terminated jobs
            stdout, stderr = p.communicate()

            singleResult = SingleResult(name=testName, returncode=returncode, output=stdout.rstrip(), nodes=n)
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

# vim: set et ts=4 sw=4 sts=4:
