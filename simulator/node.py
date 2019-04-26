#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto
from simulator.packet import Packet
from simulator.util import print_log

class Node:

    def __init__(self, id):
        self.id = id
        self.queue = []
        self.asn_next_enqueue = 0

    def get_next_packet(self):
        if len(self.queue) > 0:
            return self.queue[0]
        return None

    def enqueue_eb(self):
        packet = Packet(self.id,"",is_eb=True)
        self.queue.append(packet)

    def remove_transmitted_packet(self):
        print_log("Removing transmitted packet. Node:{} / Payload:{}".format(self.id,self.queue[0].payload),
        #          header=False)
        self.queue.pop(0)

    def remove_dropped_packet(self):
        #print_log("Removing dropped packet. Node:{} / Payload:{}".format(self.id, self.queue[0].payload),
        #          header=False)
        self.queue.pop(0)

    def __str__(self):
        return self.id
