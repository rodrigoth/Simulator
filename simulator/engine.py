#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto


from simulator.node import Node
from simulator.schedule import Slotframe
from random import randint
import numpy as np

class Simulation:
    FIRST_EB_RANDOM_WINDOW = 500
    EB_PERIOD = 1000 # in ASN
    JITTER = 200 # in ASN

    def __init__(self, number_of_nodes):
        sink = Node('Sink')
        sink.rank = 256

        self.number_of_nodes = number_of_nodes
        self.nodes = [sink]
        self.slotframe = Slotframe()

        self.joining_node_freq = randint(11,26)
        self.times = []

    def build_topology(self):
        sink = self.nodes[0]
        sink.rank = 256

        for node in range(self.number_of_nodes):
            new_node = Node("Node {}".format(node))
            new_node.rank = sink.rank + 256
            self.nodes.append(new_node)

    def compute_frequency(self,asn, channel_offset):
        return 11 + (asn + channel_offset)%16

    def check_eb_queuing(self,asn):
        times = []
        for node in self.nodes:
            # first queuing
            if not node.asn_next_enqueue:
                node.asn_next_enqueue = asn + randint(1, self.FIRST_EB_RANDOM_WINDOW)
            else:
                if asn == node.asn_next_enqueue:
                    node.enqueue_eb()
                    node.asn_next_enqueue = asn + randint(self.EB_PERIOD - self.JITTER,self.EB_PERIOD + self.JITTER)



    def get_all_eb_transmitters(self):
        return [node for node in self.nodes if len(node.queue) > 0]

    def prepare_simulation(self):
        self.build_topology()

    def execute(self):
        current_cell_index = 0
        asn = 1
        tries = 0
        one_transmitter = 0

        while True:
            current_cell = self.slotframe.cells[current_cell_index]
            current_frequency = self.compute_frequency(asn,current_cell.channel)

            if current_cell.shared:
                eb_transmitters = self.get_all_eb_transmitters()
                if len(eb_transmitters) == 1:
                    one_transmitter += 1
                    self.times.append(float(asn * 15) / 1000)
                    #print("{} transmitting in ASN {} frequency {}".format(eb_transmitters[0].id,asn,current_frequency))
                    if current_frequency == self.joining_node_freq:
                        #print("Joining time {}".format((asn*15)/1000))
                        #print("Tries: {}".format(tries))
                        #print(self.times)

                        return float(asn*15)/1000,self.times

                    eb_transmitters[0].remove_transmitted_packet()


                else:
                    if len(eb_transmitters) > 1:
                        for n in eb_transmitters:
                            self.times.append(float(asn * 15) / 1000)
                        [node.remove_transmitted_packet() for node in eb_transmitters]
                tries += 1

            self.check_eb_queuing(asn)

            if current_cell.is_the_last_cell():
                current_cell_index = 0
            else:
                current_cell_index += 1

            asn += 1