import os
import sys
from time import time
import itertools
from statistics import median, mean, stdev

from scipy import stats

from deap.tools import ParetoFront
from deap.benchmarks.tools import igd, diversity, convergence, hypervolume

import matplotlib.pyplot as plt

from show import load_run_file


CXMETHOD = ['mate_aligned']
CXPB = [0.6]
INDPB = [0.01]
MU = [100, 152, 200]
NGEN = [1500, 2000, 2500]


if __name__ == "__main__":
    start = int(time())

    if len(sys.argv) != 2:
        print(f'Usage:  analysis.py <PATH>')
        exit(1)
    path = sys.argv[1]

    (dirpath, dirnames, filenames) = next(os.walk(f'{path}/runs'))
    if not filenames:
        print('No Files')
        exit()

    ref_front = ParetoFront()

    raw_data = {}
    for file in filenames:
        (instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(f'{dirpath}\{file}')
        ref_front.update(pop)
        param_id = ';'.join([str(value) for value in [indpb,cxpb,cxmethod,mu,ngen]])
        raw_data[param_id] = raw_data[param_id] if param_id in raw_data else []
        run_front = ParetoFront()
        run_front.update(pop)
        data = {}
        data['timestamp'] = timestamp
        data['runfront'] = run_front
        data['runtime'] = runtime
        raw_data[param_id].append(data)

    ref_front_values = [ind.fitness.values for ind in ref_front]
    obj1_values, obj2_values = zip(*ref_front_values)
    nadir_point = (max(obj1_values), max(obj2_values))
    ref_hv = hypervolume(ref_front, nadir_point)

    params = [';'.join([str(p) for p in cb]) for cb in itertools.product(INDPB, CXPB, CXMETHOD, MU, NGEN)]
    rhv = {}
    for param_id in sorted(raw_data.keys()):
        if param_id in params:
            runtime = []
            rhv[param_id] = []
            print(param_id, end=';')
            for data in raw_data[param_id]:
                #print(f"{data['timestamp']}.p")
                runtime.append(data['runtime'])
                #invgd = igd([ind.fitness.values for ind in run_front], ref_front_values)
                #conv = convergence(run_front, ref_front_values)
                #div = diversity(run_front, ref_front_values[0], ref_front_values[-1])
                hv = hypervolume(data['runfront'], nadir_point)
                rhv[param_id].append(hv/ref_hv)
            print(f"{median(rhv[param_id]):.4f};{mean(rhv[param_id]):.4f};{stdev(rhv[param_id]):.4f};{mean(runtime):.1f};{stdev(runtime):.2f};{stats.kstest(rhv[param_id], 'norm').pvalue:.2E}")

    print(f'kruskal pvalue={stats.kruskal(*rhv.values()).pvalue:.2E}')
    
    matpvalue = []
    matcolor = []
    yticks = []
    for i, gt in enumerate(rhv.keys()):
        indpb, cxpb, cxmethod, mu, ngen = gt.split(';')
        yticks.append(f'{mu};{ngen} - {i}')
        matpvalue.append([])
        matcolor.append([])
        for j, le in enumerate(rhv.keys()):
                mannwhitneyu = stats.mannwhitneyu(rhv[gt], rhv[le], alternative='greater')
                matpvalue[-1].append(mannwhitneyu.pvalue)
                if i == j:
                    matcolor[-1].append((1.,1.,1.))
                elif mannwhitneyu.pvalue < 0.001:
                    matcolor[-1].append((0.0,0.353,0.196))
                elif mannwhitneyu.pvalue < 0.01:
                    matcolor[-1].append((0.137,0.545,0.271))
                elif mannwhitneyu.pvalue < 0.05:
                    matcolor[-1].append((0.631,0.851,0.608))
                else: 
                    matcolor[-1].append((0.937,0.231,0.173))

    fig, ax = plt.subplots(figsize=(5,5))

    ax.matshow(matcolor)

    for i, row in enumerate(matpvalue):
        for j, cell in enumerate(row):
            ax.text(j, i, f'{cell:.2f}', va='center', ha='center')

    plt.yticks(range(len(rhv)), yticks)
    # Minor ticks
    ax.set_xticks([x-0.5 for x in range(1,len(rhv))], minor=True)
    ax.set_yticks([x-0.5 for x in range(1,len(rhv))], minor=True)
    # Gridlines based on minor ticks
    ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
    # Remove minor ticks
    ax.tick_params(which='minor', top=False, bottom=False, left=False)

    plt.tight_layout()
    plt.savefig(f'{path}/{os.path.basename(os.path.normpath(path))}.png')
    
    runtime = time()-start
    print(f'runtime {runtime}')