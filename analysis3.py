import os
import sys
from time import time
import itertools
from statistics import median, mean, stdev

from scipy import stats

from deap.tools import ParetoFront
from deap.benchmarks.tools import igd, diversity, convergence, hypervolume

import matplotlib.pyplot as plt
from scipy.stats import norm

from show import load_run_file

from math import dist

CXMETHOD = ['mate_aligned']
CXPB = [0.6]
INDPB = [0.01]
MU = [200]
NGEN = [2500]


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
    puntosx = []
    puntosy = []
    raw_data = {}
    for file in filenames:
        (instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(f'{dirpath}\{file}')
        ref_front.update(pop)
        param_id = ';'.join([str(value) for value in [indpb,cxpb,cxmethod,mu,ngen]])
        raw_data[param_id] = raw_data[param_id] if param_id in raw_data else []
        run_front = ParetoFront()
        run_front.update(pop)
        x,y = (zip(*[ind.fitness.values for ind in pop]))
        puntosx.append(x)
        puntosy.append(y)
        data = {}
        data['timestamp'] = timestamp
        data['runfront'] = run_front
        data['runtime'] = runtime
        raw_data[param_id].append(data)

    ref_front_values = [ind.fitness.values for ind in ref_front]
    obj1_values, obj2_values = zip(*ref_front_values)
    nadir_point = (max(obj1_values), max(obj2_values))
    ref_hv = hypervolume(ref_front, nadir_point)

    plt.title(path)
    plt.plot(puntosx,puntosy, "b.")
    plt.plot(obj1_values, obj2_values, "r.")
    plt.show()
    params = [';'.join([str(p) for p in cb]) for cb in itertools.product(INDPB, CXPB, CXMETHOD, MU, NGEN)]
    rhv = {}
    for param_id in sorted(raw_data.keys()):
        if param_id in params:
            runtime = []
            rhv[param_id] = []
            div = []
            invgd = []
            pnd = []
            print(param_id, end=';')
            for data in raw_data[param_id]:
                #print(f"{data['timestamp']}.p")
                runtime.append(data['runtime'])
                invgd.append(igd([ind.fitness.values for ind in data['runfront']], ref_front_values))
                #conv = convergence(run_front, ref_front_values)
                div.append(diversity(data['runfront'], ref_front_values[0], ref_front_values[-1]))
                hv = hypervolume(data['runfront'], nadir_point)
                rhv[param_id].append(hv/ref_hv)
                pnd.append(len(data['runfront']))

            print(f"{mean(rhv[param_id]):.4f};{stdev(rhv[param_id]):.4f};{mean(runtime):.1f};{stdev(runtime):.2f};{mean(invgd):.4f};{stdev(invgd):.4f};{mean(div):.4f};{stdev(div):.4f};{min(obj1_values):.4f};{min(obj2_values):.4f};{mean(pnd):.4f};{stdev(pnd):.4f};")
            loc, scale = norm.fit(rhv[param_id])
            Hiper = norm(loc=loc, scale=scale)
            loc, scale = norm.fit(invgd)
            # create a normal distribution with loc and scale
            Generation = norm(loc=loc, scale=scale)
            loc, scale = norm.fit(runtime)
            # create a normal distribution with loc and scale
            run = norm(loc=loc, scale=scale)
            loc, scale = norm.fit(div)
            # create a normal distribution with loc and scale
            Diver = norm(loc=loc, scale=scale)
            loc, scale = norm.fit(pnd)
            # create a normal distribution with loc and scale
            puntos = norm(loc=loc, scale=scale)
            print(f"{stats.kstest(rhv[param_id], Hiper.cdf).pvalue:.2E};{stats.kstest(invgd, Generation.cdf).pvalue:.2E};{stats.kstest(runtime,run.cdf).pvalue:.2E};{stats.kstest(div,Diver.cdf).pvalue:.2E};{stats.kstest(pnd, puntos.cdf).pvalue:.2E}")
            print(f"{stats.normaltest(rhv[param_id]).pvalue};{stats.normaltest(invgd).pvalue};{stats.normaltest(runtime).pvalue};{stats.normaltest(div).pvalue};{stats.normaltest(pnd).pvalue}")
        distancia = 50000;
        punto = [0,0]
        ref = [min(obj1_values),min(obj2_values)]
        for p in ref_front_values:
            distActual = dist(p,ref)
            if distActual<distancia:
                distancia=distActual
                punto = p
        print(f"{punto}")