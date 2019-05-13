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
# estimated = [113.07846854492246, 95.46493372986203, 86.06864618167405, 80.86538175592287, 78.2101831497693,
#              77.32296215667644, 77.71167874433331, 79.17509929104153, 81.57159025970016, 84.91273300774284,
#              89.1034847032894, 94.39719630734425, 100.30902666379102, 107.1280965479208, 115.64834164689006,
#              125.55758354880959, 136.9199165397302, 150.04223400610223, 164.8316658573137, 183.08326103293797,
#              203.06954693691512, 227.46497288875645, 254.36007810652274, 290.4940881359142, 328.153636784951,
#              372.5603683635791, 429.2456900670159, 492.89556359234905, 573.6963831064331, 662.679122675888]

estimated = [110.52980699513944, 92.48989338298718, 82.61946922607152, 76.88089988177872, 73.61414357987171,
             72.03792508356089, 71.65550004077988, 72.20693958251002, 73.55622918565209, 75.66153248990958,
             78.42930639086221, 82.00088921825164, 86.02239602437015, 90.6651711130427, 96.44487259220634,
             103.11946697811365, 110.70187687206192, 119.36434001383356, 129.01299219110055, 140.76897687701882,
             153.4727177307687, 168.7713491892365, 185.4117634805574, 207.4571365603913, 230.1190120912571,
             256.5040200937441, 289.7546336426642, 326.6292854450297, 372.8842928735651, 423.2555055919437]





avgs_sync_time = []
intervals_sync = []
avgs_neg_time = []
intervals_neg = []

lamb_avg = []
ebs = []
for nei in np.arange(1, 31):  # np.arange(5,26):
    print("# of neighbors: {}".format(nei))
    sync_lst = []
    negotiation_lst = []
    probs = []
    for i in range(1000):
        simulation = Simulation(nei,optimized=False)
        simulation.prepare_simulation()
        # times,eb_prop = simulation.compute_broadcast_frequency_by_period(eb_period=15,sample_length=10000)
        # lamb_avg.append(np.average(times[:-1]))
        # ebs.append(eb_prop)
        sync_time, negotiation_time = simulation.execute()
        sync_lst.append(sync_time)
        negotiation_lst.append(negotiation_time)
        # print(sync_time,negotiation_time)
        # print(np.average(sync_lst), np.average(negotiation_lst))
        # print()

    st = mean_confidence_interval(sync_lst)
    avgs_sync_time.append(st[0])
    intervals_sync.append(st[0] - st[1])
    print(st)

    st = mean_confidence_interval(negotiation_lst)
    avgs_neg_time.append(st[0])
    intervals_neg.append(st[0] - st[1])
    print(st)



fig = plt.figure(1)
ax = fig.add_subplot(111)


ax.tick_params(axis='both', which='major', labelsize=12)
ax.tick_params(axis='both', which='minor', labelsize=12)

p1 = plt.bar(np.arange(1, 31), avgs_sync_time, yerr=intervals_sync)
p2 = plt.bar(np.arange(1, 31), avgs_neg_time, bottom=avgs_sync_time, yerr=intervals_neg)
plt.ylabel("Joining time (s)", fontsize='14')
plt.xlabel("Number of neighbors", fontsize='14')
plt.ylim([0,800])
p3 = plt.plot(np.arange(1, 31), estimated, linestyle=":")
plt.legend((p1[0], p2[0], p3[0]), ('Synchronization', 'Negotiation', "Model estimate"),fontsize='14',loc='upper left')


plt.show()

#
#
# # #
# print(lamb_avg)
# print(ebs)