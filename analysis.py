import os
import json
import pickle
import sys
from time import time
from statistics import median, mean, stdev

from scipy import stats

from deap.tools import ParetoFront
from deap.benchmarks.tools import igd, diversity, convergence, hypervolume


def load_inst_file(file):
    with open(file) as f:
        try:
            data = json.load(f)
            sources = data['sources']
            targets = data['targets']
        except:
            print(f'Unable to load file {file}')
            exit(1)
    return sources, targets

def load_run_file(file):
    with open(file, 'rb') as f:
        try:
            data = pickle.load(f)
            instance = data['instance']
            timestamp = data['timestamp']
            runtime = data['runtime']
            cxmethod = data['cxmethod']
            cxpb = data['cxpb']
            indpb = data['indpb']
            mu = data['mu']
            ngen = data['ngen']
            seed = data['seed']
            logbook = data['logbook']
            pop = data['pop']
        except:
            print(f'Unable to load file {file}')
            exit(1)
    return (instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop)


if __name__ == "__main__":
    start = int(time())

    if len(sys.argv) != 2:
        print(f'Usage:  analysis.py <PATH>')
        exit(1)
    path = sys.argv[1]

    inst_file = f'{path}/{os.path.basename(os.path.normpath(path))}.json'
    (sources, targets) = load_inst_file(inst_file)

    (dirpath, dirnames, filenames) = next(os.walk(f'{path}/runs'))
    if not filenames:
        print('No Files')
        exit()

    ref_front = ParetoFront()

    raw_data = {}
    for file in filenames:
        (instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(f'{dirpath}\{file}')
        ref_front.update(pop)
        param_id = ';'.join([str(value) for value in [cxmethod,cxpb,indpb]])
        raw_data[param_id] = raw_data[param_id] if param_id in raw_data else []
        run_front = ParetoFront()
        run_front.update(pop)
        data = {}
        data['timestamp'] = timestamp
        data['runfront'] = run_front
        raw_data[param_id].append(data)

    ref_front_values = [ind.fitness.values for ind in ref_front]
    obj1_values, obj2_values = zip(*ref_front_values)
    nadir_point = (max(obj1_values), max(obj2_values))
    ref_hv = hypervolume(ref_front, nadir_point)


    rhv = {}
    print('cxmethod;cxpb;indpb;median;mean;stdev;kstest')
    for param_id in raw_data.keys():
        rhv[param_id] = []
        print(param_id, end=';')
        for data in raw_data[param_id]:
            #invgd = igd([ind.fitness.values for ind in run_front], ref_front_values)
            #conv = convergence(run_front, ref_front_values)
            #div = diversity(run_front, ref_front_values[0], ref_front_values[-1])
            rhv[param_id].append(hypervolume(data['runfront'], nadir_point)/ref_hv)
        print(f"{median(rhv[param_id])};{mean(rhv[param_id])};{stdev(rhv[param_id])};{stats.kstest(rhv[param_id], 'norm').pvalue}")

    print(stats.kruskal(*[values for values in rhv.values()]))

    for gt in rhv.keys():
        for le in rhv.keys():
            mannwhitneyu = stats.mannwhitneyu(rhv[gt], rhv[le], alternative='greater')
            result = f'{gt} > {le}' if mannwhitneyu.pvalue < 0.05 else f'{gt} . {le}'
            print(f'{result: <65} ... pvalue: {mannwhitneyu.pvalue}')



    runtime = time()-start
    print(f'runtime {runtime}')