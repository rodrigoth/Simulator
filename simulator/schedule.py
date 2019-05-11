#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto

SLOTFRAME_LENGTH = 101

class Cell:
    def __init__(self, timeslot, channel, is_shared_cell, is_eb_cell):
        self.timeslot = timeslot
        self.channel = channel
        self.sender = None
        self.used = False
        self.shared = is_shared_cell
        self.eb_cell = is_eb_cell

    def is_the_last_cell(self):
        if self.timeslot == SLOTFRAME_LENGTH - 1:
            return True
        return False

    def __str__(self):
        return ', '.join(['{key}={value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


class Slotframe:
    def __init__(self):
        self.cells = []

        self.cells.append(Cell(0, 0, True, False))  # shared cell
        self.cells.append(Cell(1, 0, False, True))
        for i in range(2, SLOTFRAME_LENGTH):
            self.cells.append(Cell(i, 0, False, False))
