#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto


class Packet:

    def __init__(self, node, payload,priority, is_eb = False, is_6p = False):
        self.node = node
        self.payload = payload
        self.attempts_left = 4
        self.sent_asn = 0
        self.received_asn = 0
        self.is_forwarding = False
        self.is_eb = is_eb
        self.destination = None
        self.is_6p = is_6p
        self.backoff_counter = 0
        self.priority = priority

    def __str__(self):
        return ', '.join(['{key}={value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])

