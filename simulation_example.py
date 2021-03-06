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
# estimated = [108.29084816967293, 90.31584351440738, 79.2968973446165, 72.91388986902942, 69.04294997041633,
#              66.86064282392951, 65.63657034052454, 65.23905687228151, 65.47813036536584, 66.32451472654485,
#              67.50555244920352, 69.32655631649223, 71.56503481837231, 74.03193532569234, 77.27925729497224,
#              80.21702986295932, 84.00323439983052, 88.75743055861393, 90.60972842054233, 97.2989217818168,
#              102.62420057206032, 109.62192847742452, 113.27309415801804, 121.76737433883679, 132.9418297769606,
#              139.2065272602568, 147.07615040062228, 155.13644031941269, 164.63927022519556, 176.28949926525382]
# estimated = [113.37827068240938, 96.21331408434233, 86.17925714182331, 80.87878182361423, 78.22418146098798,
#              77.33750144308932, 77.66659287630713, 79.24758285402876, 81.25875579431559, 84.62153464748798,
#              88.36046084310595, 93.61677676311734, 99.83772134898778, 106.65547299594776, 115.75569990642246,
#              124.20081642176888, 135.4580493624678, 150.26926618695555, 156.25896377753767, 178.97861652465565,
#              198.3460883770298, 225.61498894869126, 240.69353684554716, 278.1169312764043, 332.5454737697812,
#              365.74729205242545, 410.2879322176699, 459.27000238342987, 521.5192214600748, 604.6909624159388]

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

for nei in np.arange(1, 31):  # np.arange(5,26):
    print("# of neighbors: {}".format(nei))
    sync_lst = []
    negotiation_lst = []
    probs = []
    for i in range(1000):
        simulation = Simulation(nei)
        simulation.prepare_simulation()
        #times = simulation.compute_eb_frequency_by_period(eb_period=15,sample_length=10000)
        #lamb_avg.append(np.average(times[:-1]))
        sync_time, negotiation_time = simulation.execute()

        sync_lst.append(sync_time)
        negotiation_lst.append(negotiation_time)


    st = mean_confidence_interval(sync_lst)
    avgs_sync_time.append(st[0])
    intervals_sync.append(st[0] - st[1])

    st = mean_confidence_interval(negotiation_lst)
    avgs_neg_time.append(st[0])
    intervals_neg.append(st[0] - st[1])


fig = plt.figure(1)
ax = fig.add_subplot(111)


ax.tick_params(axis='both', which='major', labelsize=12)
ax.tick_params(axis='both', which='minor', labelsize=12)

p1 = plt.bar(np.arange(1, 31), avgs_sync_time, yerr=intervals_sync)
p2 = plt.bar(np.arange(1, 31), avgs_neg_time, bottom=avgs_sync_time, yerr=intervals_neg)
plt.ylabel("Joining time (s)", fontsize='14')
plt.xlabel("Number of neighbors", fontsize='14')
plt.ylim([0,1200])
p3 = plt.plot(np.arange(1, 31), estimated, linestyle=":")
plt.legend((p1[0], p2[0], p3[0]), ('Synchronization', 'Negotiation', "Model estimate"),fontsize='14')


plt.show()
