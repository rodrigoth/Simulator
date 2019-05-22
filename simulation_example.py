#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto

'''Simple script to launch an experiment'''

from simulator.engine import Simulation
import numpy as np
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


for nei in np.arange(31, 32):
    sync_lst = []
    negotiation_lst = []
    for i in range(1000):
        simulation = Simulation(nei, optimized=True)
        simulation.prepare_simulation()
        sync_time, negotiation_time = simulation.execute()
        sync_lst.append(sync_time)
        negotiation_lst.append(negotiation_time)

    st = mean_confidence_interval(sync_lst)
    print(st)

    st = mean_confidence_interval(negotiation_lst)
    print(st)
    print("")
