#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto
from simulator.packet import Packet
from random import randint
from simulator.util import print_log, rand_uuid

class Status6PTypes:
    [IDLE, SENT_REQUEST, REQUEST_RECEIVED, SENT_RESPONSE] = range(4)


class Node:

    def __init__(self, id, is_infrastructure=True):
        self.id = id
        self.queue = []
        self.asn_next_eb_enqueue = 0
        self.asn_next_dio_enqueue = 0
        self.is_synchronized = True
        self.active_frequency = 0
        self.parent = None
        self.status = Status6PTypes.IDLE
        self.requester = None
        self.asn_request = None
        self.asn_request_timeout = None
        self.uuid = rand_uuid()
        self.is_infrastructure = is_infrastructure

    def get_next_packet(self):
        if len(self.queue) > 0:

            pkt = self.next_6p_packet()
            if pkt:
                if pkt.backoff_counter > 0:
                    pkt.backoff_counter -= 1
                else:
                    return pkt
        return None

    def get_next_broadcast_packet(self):
        for pkt in self.queue:
            if pkt.is_eb or pkt.is_dio:
                return pkt
        return None

    def remove_broadcast_packet(self):
        for pkt in self.queue:
            if pkt and (pkt.is_eb or pkt.is_dio):
                self.queue.remove(pkt)

    def next_6p_packet(self):
        for pkt in self.queue:
            if pkt.is_6p:
                return pkt
        return None


    def next_eb_packet(self):
        for pkt in self.queue:
            if pkt.is_eb:
                return pkt
        return None

    def next_dio_packet(self):
        for pkt in self.queue:
            if pkt.is_dio:
                return pkt
        return None

    def enqueue_eb(self):
        packet = Packet(self.id, "", priority=0, is_eb=True)
        self.queue.append(packet)

    def enqueue_dio(self):
        if self.is_infrastructure:
            packet = Packet(self.id, "", priority=0, is_dio=True)
            self.queue.append(packet)

    def enqueue_6p(self, destination,payload):
        packet = Packet(self.id,payload, priority=1, is_6p=True)
        packet.destination = destination
        self.queue.append(packet)

    def remove_eb_packet(self):
        for pkt in self.queue:
            if pkt.is_eb:
                self.queue.remove(pkt)
                return True
        return False

    def remove_dio_packet(self):
        for pkt in self.queue:
            if pkt.is_dio:
                self.queue.remove(pkt)
                return True
        return False

    def remove_transmitted_packet(self):
        self.queue.pop(0)

    def failed_6p_transmissions(self,asn):
        packet_6p = self.next_6p_packet()
        if packet_6p.attempts_left >= 1:
            print_log(asn, "6P packet collided - {}".format(self.id))
            packet_6p.attempts_left -= 1
            packet_6p.backoff_counter = randint(0,2)
        else:
            print_log(asn,"6P packet dropped - {}".format(self.id))
            self.queue.remove(packet_6p)
            self.status = Status6PTypes.IDLE

            if not self.requester:
                self.enqueue_6p(self.parent, "6P request")
                print_log(asn, "6P packet enqueued - {}".format(self.id))

            #print_log(asn,"Failed negotiation ({})".format(self.id))

    def __str__(self):
        return ', '.join(['{key}={value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])
