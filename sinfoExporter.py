#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: spreitzer@par.tuwien.ac.at
simple promtheus exporter for detecting broken nodes in slurm
"""

import subprocess as sub
import prometheus_client as prom
import time
from threading import Thread
from flask import Flask
from flask_prometheus import monitor

#for logging
import logging

#helper function to create a matrix list from a list
def makeMatrix(list, elements):
        return [list[i:i+elements]for i in range(0, len(list), elements)]

#function to get the node states
def getStates():

        while True:
                logging.info("Get sinfo data")
                #get sinfo
                out = sub.Popen(["/opt/slurm/bin/sinfo","-aN"],
                        stdout=sub.PIPE,
                        stderr=sub.STDOUT)

                stdout, stderr = out.communicate()

                #check if return contains data
                if len(stdout) > 5:
                        logging.info("Got enough data from sinfo, len is %s", len(stdout))
                        break

                logging.info("Got not enough data, len is %s! Start another poll of sinfo!" , len(stdout))

        #decode the byteinformation to string
        decoded = stdout.decode("utf-8")
        #cast string to list
        casted = decoded.split()
        #make the list 6d
        listed = makeMatrix(casted, 4)

        #get number of partitions
        firstPartition = listed[1][2]
        CountPartition = 0
        for row in listed[2::]:
                CountPartition += 1
                if row[2] == firstPartition:
                        break

        #count states
        CounterAlloc = 0
        CounterIdle = 0
        CounterDrained = 0
        CounterDown = 0
        CounterOthers = 0

        NodeStates=[]

        #Statecodes: 1=Alloc, 2=Idle, 3=Drain, 4=Down, 5=Other

        for row in listed[1::CountPartition]:
                if row[3] == "alloc":
                        CounterAlloc += 1
                        NodeStates.append(1)
                elif row[3] == "idle":
                        CounterIdle += 1
                        NodeStates.append(2)
                elif row[3] == "drained" or row[3] == "drain":
                        CounterDrained += 1
                        NodeStates.append(3)
                elif row[3] == "down":
                        CounterDown += 1
                        NodeStates.append(4)
                else:
                        CounterOthers += 1
                        NodeStates.append(5)

        logging.info("before returning NodeStates to main, the len is: %s", len(NodeStates))
        return (CounterAlloc, CounterIdle, CounterDrained, CounterDown, CounterOthers, NodeStates)

def main():

        #Logstuff
        logging.basicConfig(filename="/usr/local/sbin/prometheusSinfoExporter/prometheusSinfoExporter.log", level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s",  datefmt="%d-%m-%Y %I:%M:%S")

        req_summary = prom.Summary("slurmctld_exporter", "How many nodes are in drained state")
        app = Flask("pyProm")

        AllocNodes = prom.Gauge("hydra_slurm_allocated_nodes", "The number of allocated nodes @Hydra")
        IdleNodes = prom.Gauge("hydra_slurm_idle_nodes", "The number of idle nodes @Hydra")
        DrainedNodes = prom.Gauge("hydra_slurm_drained_nodes", "The number of drained nodes @Hydra")
        DownNodes = prom.Gauge("hydra_slurm_down_nodes", "The number of down nodes @Hydra")
        OtherNodes = prom.Gauge("hydra_slurm_other_nodes", "The number of nodes in any other state @Hydra")


        #build objects for the (36) Nodes
        Nodes=[]
        for Node in range(1,37):
                if Node < 10:
                        Nodes.append(prom.Gauge("hydra_slurm_node0{}_state".format(Node), "The state of the Node0{} @Hydra".format(Node)))
                else:
                        Nodes.append(prom.Gauge("hydra_slurm_node{}_state".format(Node), "The state of the Node{} @Hydra".format(Node)))

        def thr():
                while True:
                        logging.info("#####################################")
                        logging.info("Started a new run to gather the states!")
                        CounterAlloc, CounterIdle, CounterDrained, CounterDown, CounterOthers, NodeStates = getStates()

                        AllocNodes.set(CounterAlloc)
                        IdleNodes.set(CounterIdle)
                        DrainedNodes.set(CounterDrained)
                        DownNodes.set(CounterDown)
                        OtherNodes.set(CounterOthers)

                        logging.info("Got CounterAlloc: %s", CounterAlloc)
                        logging.info("Got CounterIdle: %s", CounterIdle)
                        logging.info("Got CounterDrained: %s", CounterDrained)
                        logging.info("Got CounterDown: %s", CounterDown)
                        logging.info("Got CounterOthers: %s", CounterOthers)

                        logging.info("Got %s NodeStates", len(NodeStates))

                        #check if return contains data, update node states
                        if len(NodeStates) == 36:
                                i=0
                                for Node in Nodes:
                                        Node.set(NodeStates[i])
                                        i += 1
                        else:
                                logging.info("Got no exact data from getStates(), len is NOT 36!")
                                logging.info("Waiting for the next run!")

                        time.sleep(10)

        Thread(target=thr).start()
        monitor(app, port=9101)

        return 0


if __name__ == "__main__":
        main()