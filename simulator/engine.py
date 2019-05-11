#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto

import numpy as np
from simulator.node import Node, Status6PTypes
from simulator.schedule import Slotframe
from simulator.util import print_log
from random import randint
from itertools import groupby
from collections import defaultdict

class Simulation:
    FIRST_EB_RANDOM_WINDOW = 500
    EB_PERIOD = 1000  # in ASN
    JITTER = 200  # in ASN
    RANK_INCREASE = 256

    def __init__(self, number_of_nodes):
        sink = Node('Sink')
        sink.rank = self.RANK_INCREASE

        self.number_of_nodes = number_of_nodes
        self.nodes = [sink]
        self.slotframe = Slotframe()

    def build_topology(self):
        sink = self.nodes[0]

        for node in range(self.number_of_nodes):
            new_node = Node("Node {}".format(node))

            if len(self.nodes) == 1:
                new_node.rank = sink.rank + self.RANK_INCREASE
                new_node.parent = sink
            else:
                parent = self.nodes[randint(0, len(self.nodes) - 1)]
                new_node.parent = parent
                new_node.rank = parent.rank + self.RANK_INCREASE

            self.nodes.append(new_node)

        joining_node = Node("Joining node")
        joining_node.is_synchronized = False
        joining_node.active_frequency = randint(11, 26)
        print("Joining node frequency")
        self.nodes.append(joining_node)

    def compute_frequency(self, asn, channel_offset):
        return 11 + (asn + channel_offset) % 16

    def check_eb_queuing(self, asn):
        for node in self.nodes:
            if node.is_synchronized:
                # first queuing
                if not node.asn_next_enqueue:
                    node.asn_next_enqueue = asn + randint(1, self.FIRST_EB_RANDOM_WINDOW)
                else:
                    if asn == node.asn_next_enqueue:
                        node.enqueue_eb()
                        node.asn_next_enqueue = asn + randint(self.EB_PERIOD - self.JITTER,
                                                              self.EB_PERIOD + self.JITTER)

    def get_all_eb_transmitters(self,asn):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized:
                packet = node.get_next_packet()
                if packet and packet.is_eb:
                    node.active_frequency = (abs(hash(node.uuid)) + asn) % 16 + 11
                    transmitters.append(node)
        return transmitters

    def get_all_6p_transmitters(self):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized:
                packet = node.get_next_packet()
                if packet and packet.is_6p:
                    transmitters.append(node)
        return transmitters

    def prepare_simulation(self):
        self.build_topology()

    def update_nodes_active_frequency(self, new_frequency):
        for node in self.nodes:
            if node.is_synchronized:
                node.current_frequency = new_frequency

    def get_joining_node(self):
        return self.nodes[-1]

    def is_collision(self, transmitters):
        return len(transmitters) > 1

    def check_6P_timeout(self,asn):
        for node in self.nodes:
            if node.status == Status6PTypes.SENT_REQUEST:
                if node.asn_request_timeout < asn:
                    node.status = Status6PTypes.IDLE
                    self.get_joining_node().enqueue_6p(node.parent, "6P request")
                    print_log(asn,"Negotiation timeout - {}".format(node.id))
                    print_log(asn, "6P packet enqueued - {}".format(node.id))

    def get_non_colliding_nodes(self,all_transmiters):
        non_colliding = []
        dic = defaultdict(list)

        [dic[t.active_frequency].append(t) for t in all_transmiters]
        for k,v in dic.items():
            if len(v) == 1:
                non_colliding.append(v[0])
        return non_colliding

    def get_parent(self,transmitters):
        for t in transmitters:
            if t.active_frequency == self.get_joining_node().active_frequency:
                return t
        return None

    def execute(self):
        current_cell_index = 0
        asn = 1
        sync_time = 0

        while True:
            current_cell = self.slotframe.cells[current_cell_index]
            current_frequency = self.compute_frequency(asn, current_cell.channel)
            self.update_nodes_active_frequency(current_frequency)

            self.check_6P_timeout(asn)

            if current_cell.shared:
                all_6p_transmitters = self.get_all_6p_transmitters()
                if all_6p_transmitters:
                    if self.is_collision(all_6p_transmitters):
                        [node.failed_6p_transmissions(asn) for node in all_6p_transmitters]
                    else:
                        transmitter = all_6p_transmitters[0]

                        if transmitter.status == Status6PTypes.IDLE:
                            transmitter.status = Status6PTypes.SENT_REQUEST
                            transmitter.asn_request = asn
                            transmitter.asn_request_timeout = asn + 1500

                            if transmitter.parent.status == Status6PTypes.IDLE:
                                print_log(asn, "{} received 6P request".format(transmitter.parent.id))
                                transmitter.parent.enqueue_6p(transmitter, '6P response')
                                transmitter.parent.requester = transmitter.id
                                transmitter.parent.status = Status6PTypes.REQUEST_RECEIVED

                        else:
                            if transmitter.status == Status6PTypes.REQUEST_RECEIVED:
                                print_log(asn, "Negotiation successful")
                                transmitter.remove_transmitted_packet()
                                negotiation_time = float(asn * 15) / 1000 - sync_time
                                return sync_time, negotiation_time

                    transmitter.remove_transmitted_packet()

            if current_cell.eb_cell:
                all_eb_transmitters = self.get_all_eb_transmitters(asn)

                if all_eb_transmitters:
                    non_colliding_nodes = self.get_non_colliding_nodes(all_eb_transmitters)

                    if non_colliding_nodes:
                        actives_frequencies = [t.active_frequency for t in non_colliding_nodes]
                        if not self.get_joining_node().is_synchronized and self.get_joining_node().active_frequency in actives_frequencies:
                            print_log(asn, "Synchronized")
                            self.get_joining_node().is_synchronized = True
                            parent = self.get_parent(non_colliding_nodes)
                            self.get_joining_node().active_frequency = parent.active_frequency
                            self.get_joining_node().rank = parent.rank + self.RANK_INCREASE
                            self.get_joining_node().parent = parent
                            self.get_joining_node().enqueue_6p(parent, "6P request")
                            sync_time = float(asn * 15) / 1000
                            print_log(asn, "6P packet enqueued - {}".format(self.get_joining_node().id))

                    [eb_transmitter.remove_eb_packet() for eb_transmitter in all_eb_transmitters]

            self.check_eb_queuing(asn)

            if current_cell.is_the_last_cell():
                current_cell_index = 0
            else:
                current_cell_index += 1

            asn += 1

    def compute_eb_frequency_by_period(self, eb_period, sample_length=1000,):
        current_cell_index = 0
        asn = 1
        times = []

        while True and len(times) <= sample_length:
            current_cell = self.slotframe.cells[current_cell_index]
            current_frequency = self.compute_frequency(asn, current_cell.channel)

            if current_cell.shared:
                transmitters = self.get_all_transmitters()

                if self.is_collision(transmitters):
                    for node in transmitters:
                        node.remove_eb_packet()
                        times.append(asn*0.015)
                else:
                    if transmitters:
                        transmitter = transmitters[0]
                        packet = transmitters[0].queue[0]
                        if packet.is_eb:
                            if not self.get_joining_node().is_synchronized and \
                                    current_frequency == self.get_joining_node().active_frequency:
                                # print_log(asn, "Synchronized")
                                self.get_joining_node().active_frequency = current_frequency
                                self.get_joining_node().is_synchronized = True
                        times.append(asn*0.015)
                        transmitter.remove_transmitted_packet()

            self.check_eb_queuing(asn)

            if current_cell.is_the_last_cell():
                current_cell_index = 0
            else:
                current_cell_index += 1

            asn += 1
        return [len(list(group)) for key, group in groupby([np.floor(d / eb_period) for d in times])]