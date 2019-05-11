#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto

'''Simple script to launch an experiment'''

from simulator.engine import Simulation
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid", {'axes.grid': False})


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


avgs = []
intervals = []
estimated = [113.07846854492246, 95.46493372986203, 86.06864618167405, 80.86538175592287, 78.2101831497693,
             77.32296215667644, 77.71167874433331, 79.17509929104153, 81.57159025970016, 84.91273300774284,
             89.1034847032894, 94.39719630734425, 100.30902666379102, 107.1280965479208, 115.64834164689006,
             125.55758354880959, 136.9199165397302, 150.04223400610223, 164.8316658573137, 183.08326103293797,
             203.06954693691512, 227.46497288875645, 254.36007810652274, 290.4940881359142, 328.153636784951,
             372.5603683635791, 429.2456900670159, 492.89556359234905, 573.6963831064331, 662.679122675888]


avgs_sync_time = []
intervals_sync = []
avgs_neg_time = []
intervals_neg = []

for nei in np.arange(30, 31):  # np.arange(5,26):
    print("# of neighbors: {}".format(nei))
    sync_lst = []
    negotiation_lst = []
    probs = []
    for i in range(1000):
        print("Exp: {}".format(i))
        simulation = Simulation(nei)
        simulation.prepare_simulation()
        #times = simulation.compute_eb_frequency_by_period(eb_period=15,sample_length=10000)
        #lamb_avg.append(np.average(times[:-1]))
        sync_time, negotiation_time = simulation.execute()
        sync_lst.append(sync_time)
        negotiation_lst.append(negotiation_time)
        print(sync_time,negotiation_time)
        print(np.average(negotiation_lst))
        print()

    st = mean_confidence_interval(sync_lst)
    avgs_sync_time.append(st[0])
    intervals_sync.append(st[0] - st[1])
    print(st)

    st = mean_confidence_interval(negotiation_lst)
    avgs_neg_time.append(st[0])
    intervals_neg.append(st[0] - st[1])
    print(st)






