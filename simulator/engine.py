#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto


from simulator.node import Node, Status6PTypes
from simulator.schedule import Slotframe
from simulator.util import print_log
from random import randint
from collections import defaultdict


class Simulation:
    FIRST_EB_RANDOM_WINDOW = 600
    EB_PERIOD = 1000  # in ASN
    JITTER = 200  # in ASN
    RANK_INCREASE = 256

    def __init__(self, number_of_nodes, optimized=False):
        sink = Node('Sink')
        sink.rank = self.RANK_INCREASE

        self.number_of_nodes = number_of_nodes
        self.nodes = [sink]
        self.optimized = optimized
        self.slotframe = Slotframe(optimized)

    def build_topology(self):
        sink = self.nodes[0]

        index = 0
        while self.number_of_nodes > len(self.nodes) + 1:
            new_node = Node("Node {}".format(index))
            index += 1

            if len(self.nodes) == 1:
                new_node.rank = sink.rank + self.RANK_INCREASE
                new_node.parent = sink
            else:
                parent = self.nodes[randint(0, len(self.nodes) - 1)]
                new_node.parent = parent
                new_node.rank = parent.rank + self.RANK_INCREASE

            self.nodes.append(new_node)

        joining_node = Node("Joining node", is_infrastructure=False)
        joining_node.is_synchronized = False
        joining_node.active_frequency = randint(11, 26)
        self.nodes.append(joining_node)

    def compute_frequency(self, asn, channel_offset):
        return 11 + (asn + channel_offset) % 16

    def check_queuing(self, asn):
        for node in self.nodes:
            if node.is_synchronized and node.is_infrastructure:
                # first queuing
                if not node.asn_next_eb_enqueue:
                    node.asn_next_eb_enqueue = asn + randint(1, self.FIRST_EB_RANDOM_WINDOW)
                    node.asn_next_dio_enqueue = asn + randint(1, self.FIRST_EB_RANDOM_WINDOW)
                else:
                    if asn == node.asn_next_eb_enqueue:
                        node.enqueue_eb()
                        node.asn_next_eb_enqueue = asn + randint(self.EB_PERIOD - self.JITTER,
                                                                 self.EB_PERIOD + self.JITTER)
                    if asn == node.asn_next_dio_enqueue:
                        node.enqueue_dio()
                        node.asn_next_dio_enqueue = asn + randint(self.EB_PERIOD - self.JITTER,
                                                                  self.EB_PERIOD + self.JITTER)

    def get_all_eb_transmitters(self, asn):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized:
                packet = node.next_eb_packet()
                if packet:
                    if self.optimized:
                        node.active_frequency = randint(11,26)
                    transmitters.append(node)
        return transmitters

    def get_all_dio_transmitters(self):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized and node.is_infrastructure:
                packet = node.next_dio_packet()
                if packet:
                    transmitters.append(node)
        return transmitters

    def get_all_6p_transmitters(self):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized:
                packet = node.get_next_packet()
                if packet:
                    transmitters.append(node)
        return transmitters

    def prepare_simulation(self):
        self.build_topology()

    def update_nodes_active_frequency(self, new_frequency):
        for node in self.nodes:
            if node.is_synchronized:
                node.active_frequency = new_frequency

    def get_joining_node(self):
        return self.nodes[-1]

    def is_collision(self, transmitters):
        return len(transmitters) > 1

    def check_6P_timeout(self, asn):
        for node in self.nodes:
            if node.status == Status6PTypes.SENT_REQUEST:
                if node.asn_request_timeout < asn:
                    node.status = Status6PTypes.IDLE
                    self.get_joining_node().enqueue_6p(node.parent, "6P request")
                    print_log(asn, "Negotiation timeout - {}".format(node.id))
                    print_log(asn, "6P packet enqueued - {}".format(node.id))

    def get_non_colliding_nodes(self, all_transmiters, channel):
        non_colliding = []
        dic = defaultdict(list)

        [dic[t.active_frequency].append(t) for t in all_transmiters if t.active_frequency != channel]
        for k, v in dic.items():
            if len(v) == 1:
                non_colliding.append(v[0])
        return non_colliding

    def get_parent(self, transmitters):
        for t in transmitters:
            if t.active_frequency == self.get_joining_node().active_frequency:
                return t
        return None

    def get_all_broadcast_transmitters(self):
        transmitters = []
        for node in self.nodes:
            if node.is_synchronized and node.is_infrastructure:
                packet = node.get_next_broadcast_packet()
                if packet:
                    transmitters.append(node)
        return transmitters

    def __execute_optimized(self):
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
                all_eb_transmitters = [x for x in self.get_all_eb_transmitters(asn) if x not in all_6p_transmitters]
                all_dio_transmitters = [x for x in self.get_all_dio_transmitters() if
                                        x not in all_6p_transmitters and x not in all_eb_transmitters]

                all_transmitters = all_6p_transmitters + all_dio_transmitters + all_eb_transmitters

                if all_transmitters:
                    if self.is_collision(all_transmitters):
                        [t.remove_dio_packet() for t in all_dio_transmitters]
                        [t.failed_6p_transmissions(asn) for t in all_6p_transmitters]
                        [t.remove_eb_packet() for t in all_eb_transmitters if t.active_frequency == current_frequency]

                        non_colliding_nodes = self.get_non_colliding_nodes(all_eb_transmitters, current_frequency)

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

                            [eb_transmitter.remove_eb_packet() for eb_transmitter in non_colliding_nodes]
                    else:
                        transmitter = all_transmitters[0]
                        pkt = transmitter.queue[0]
                        if pkt.is_6p:
                            if transmitter.status == Status6PTypes.IDLE:
                                transmitter.status = Status6PTypes.SENT_REQUEST
                                transmitter.asn_request = asn
                                transmitter.asn_request_timeout = asn + 800

                                if transmitter.parent.status == Status6PTypes.IDLE:
                                    print_log(asn, "{} received 6P request".format(transmitter.parent.id))
                                    transmitter.parent.enqueue_6p(transmitter, '6P response')
                                    transmitter.parent.requester = transmitter.id
                                    transmitter.parent.status = Status6PTypes.REQUEST_RECEIVED

                            else:
                                if transmitter.status == Status6PTypes.REQUEST_RECEIVED:
                                    print_log(asn, "Negotiation successful")
                                    negotiation_time = float(asn * 15) / 1000 - sync_time
                                    return sync_time, negotiation_time
                        else:
                            if pkt.is_dio:
                                print_log(asn, "DIO transmitted - {}".format(transmitter.id))
                            else:
                                if not self.get_joining_node().is_synchronized and self.get_joining_node().active_frequency == current_frequency:
                                    print_log(asn, "Synchronized")
                                    self.get_joining_node().is_synchronized = True
                                    parent = transmitter
                                    self.get_joining_node().active_frequency = parent.active_frequency
                                    self.get_joining_node().rank = parent.rank + self.RANK_INCREASE
                                    self.get_joining_node().parent = parent
                                    self.get_joining_node().enqueue_6p(parent, "6P request")
                                    sync_time = float(asn * 15) / 1000
                                    print_log(asn, "6P packet enqueued - {}".format(self.get_joining_node().id))

                        transmitter.queue.remove(pkt)

            self.check_queuing(asn)

            if current_cell.is_the_last_cell():
                current_cell_index = 0
            else:
                current_cell_index += 1

            asn += 1

    def __execute_default(self):
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
                all_broadcast_transmitters = [x for x in self.get_all_broadcast_transmitters() if
                                              x not in all_6p_transmitters]

                all_transmitters = all_6p_transmitters + all_broadcast_transmitters

                if all_transmitters:
                    if self.is_collision(all_transmitters):
                        [t.remove_broadcast_packet() for t in all_broadcast_transmitters]
                        [t.failed_6p_transmissions(asn) for t in all_6p_transmitters]
                    else:
                        transmitter = all_transmitters[0]
                        pkt = transmitter.queue[0]
                        if pkt.is_6p:
                            if transmitter.status == Status6PTypes.IDLE:
                                transmitter.status = Status6PTypes.SENT_REQUEST
                                transmitter.asn_request = asn
                                transmitter.asn_request_timeout = asn + 800

                                if transmitter.parent.status == Status6PTypes.IDLE:
                                    print_log(asn, "{} received 6P request".format(transmitter.parent.id))
                                    transmitter.parent.enqueue_6p(transmitter, '6P response')
                                    transmitter.parent.requester = transmitter.id
                                    transmitter.parent.status = Status6PTypes.REQUEST_RECEIVED

                            else:
                                if transmitter.status == Status6PTypes.REQUEST_RECEIVED:
                                    print_log(asn, "Negotiation successful")
                                    negotiation_time = float(asn * 15) / 1000 - sync_time
                                    return sync_time, negotiation_time
                        else:
                            if pkt.is_dio:
                                print_log(asn, "DIO transmitted - {}".format(transmitter.id))
                            else:
                                if not self.get_joining_node().is_synchronized and self.get_joining_node(

                                ).active_frequency == current_frequency:
                                    print_log(asn, "Synchronized")
                                    self.get_joining_node().is_synchronized = True
                                    parent = transmitter
                                    self.get_joining_node().active_frequency = parent.active_frequency
                                    self.get_joining_node().rank = parent.rank + self.RANK_INCREASE
                                    self.get_joining_node().parent = parent
                                    self.get_joining_node().enqueue_6p(parent, "6P request")
                                    sync_time = float(asn * 15) / 1000
                                    print_log(asn, "6P packet enqueued - {}".format(self.get_joining_node().id))

                        transmitter.queue.remove(pkt)

            self.check_queuing(asn)

            if current_cell.is_the_last_cell():
                current_cell_index = 0
            else:
                current_cell_index += 1

            asn += 1

    def execute(self):
        if self.optimized:
            print_log("", "Enabling optimized mode")
            return self.__execute_optimized()
        else:
            print_log("", "Enabling default mode")
            return self.__execute_default()
