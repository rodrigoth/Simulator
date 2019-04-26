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
from itertools import groupby

sns.set_style("whitegrid", {'axes.grid': False})


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


avgs = []
intervals = []
estimated = [146.80285200929248, 107.86776971915364, 89.55245098850234, 79.09906158699143, 72.87309255538675, 69.03466752423938,
 66.78764763195483, 65.59336042724487, 65.2388813179544, 65.53892557928438, 66.3603283455861, 67.66843946058218,
 69.5316329107947, 71.54033262870867, 74.22884055144469, 77.13405345184947, 80.39328493790272, 84.49906325095493,
 88.6775409412028, 93.36875326073483, 98.0907548730977, 103.74198413241872, 109.74115774855454, 117.00458750397763,
 123.66854440674506, 132.4896142992175, 140.37353290670723, 149.58367698009528, 160.07635603033333, 170.283010455194]

lamb_avg = []

for nei in np.arange(1, 31):  # np.arange(5,26):
    print("# of neighbors: {}".format(nei))
    results = []
    probs = []
    lamb_avg = []
    for i in range(1000):
        simulation = Simulation(nei)
        simulation.prepare_simulation()
        joining, times = simulation.execute()
        results.append(joining)
        #input = [len(list(group)) for key, group in groupby([np.floor(d / 30) for d in times])]
        #lamb_avg.append(np.average(input))


    st = mean_confidence_interval(results, 0.95)
    avgs.append(st[0])
    intervals.append(st[0] - st[1])


plt.bar(np.arange(1, 31), avgs, yerr=intervals)
plt.plot(np.arange(1, 31), estimated)

plt.show()
