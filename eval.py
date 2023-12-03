import os
import json
import pickle
import sys
from time import time
import itertools

from scipy import stats

from deap.tools import ParetoFront
from deap.benchmarks.tools import igd, diversity, convergence, hypervolume


def load_inst_file(file, *, dir=None):
    with open(file) as f:
        try:
            data = json.load(f)
            sources = data['sources']
            targets = data['targets']
        except:
            print(f'Unable to load file {file}')
            exit(1)
    return sources, targets

def load_run_file(file, *, dir=None):
    if dir:
        file = f'{dir}/{file}'
    with open(file, 'rb') as f:
        try:
            data = pickle.load(f)
            instance = data['instance']
            timestamp = data['timestamp']
            runtime = data['runtime']
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
    return (instance, timestamp, runtime, cxpb, indpb, mu, ngen, seed, logbook, pop)


if __name__ == "__main__":
    start = int(time())

    if len(sys.argv) != 2:
        print(f'Usage:  eval.py <PATH>')
        exit(1)
    path = sys.argv[1]

    inst_file = f'{path}/{os.path.basename(os.path.normpath(path))}.json'
    (sources, targets) = load_inst_file(inst_file)

    ref_front = ParetoFront()
    (dirpath, dirnames, filenames) = next(os.walk(f'{path}/runs'))
    if not filenames:
        print('No Files')
        exit()

    cxpb_values = set()
    indp_values = set()
    mu_values = set()
    cxop_values = set()
    ngen_values = set()

    for file in filenames:
        (instance, timestamp, runtime, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(file, dir=dirpath)
        ref_front.update(pop)
        cxpb_values.add(cxpb)
        indp_values.add(indpb)
        mu_values.add(mu)
        #cxop_values.add(cx_operator)
        ngen_values.add(ngen)

    ref_front_values = [ind.fitness.values for ind in ref_front]
    obj1_values, obj2_values = zip(*ref_front_values)
    nadir_point = (max(obj1_values), max(obj2_values))
    ref_hv = hypervolume(ref_front, nadir_point)


    metrics = {}
    for file in filenames:
        (instance, timestamp, runtime, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(file, dir=dirpath)
        param_id = ';'.join([str(value) for value in [instance,cxpb,indpb,mu,ngen]])
        metrics[param_id] = metrics[param_id] if param_id in metrics else []
        run_front = ParetoFront()
        run_front.update(pop)
        data = {}
        data['timestamp'] = timestamp
        #data['igd'] = igd([ind.fitness.values for ind in run_front], ref_front_values)
        #data['convergence'] = convergence(run_front, ref_front_values)
        #data['diversity'] = diversity(run_front, ref_front_values[0], ref_front_values[-1])
        data['rhv'] = hypervolume(run_front, nadir_point)/ref_hv
        metrics[param_id].append(data)

    print(stats.kruskal(*[[v['rhv'] for v in alg] for alg in metrics.values()]))
    print(stats.friedmanchisquare(*[[v['rhv'] for v in alg] for alg in metrics.values()]))

    for key, values in metrics.items():
        print(key)
        print('timestamp;igd;convergence;diversity;rhv')
        for data in values:
            print(f"{data['timestamp']};{data['igd']};{data['convergence']};{data['diversity']};{data['rhv']}")
        print(f'kstest;statistic;pvalue;result')
        test = stats.kstest([data['igd'] for data in values], 'norm')
        print(f"igd;{test.statistic};{test.pvalue};{'not normal' if test.pvalue < 0.05 else 'normal'}")
        test = stats.kstest([data['convergence'] for data in values], 'norm')
        print(f"convergence;{test.statistic};{test.pvalue};{'not normal' if test.pvalue < 0.05 else 'normal'}")
        test = stats.kstest([data['diversity'] for data in values], 'norm')
        print(f"diversity;{test.statistic};{test.pvalue};{'not normal' if test.pvalue < 0.05 else 'normal'}")
        test = stats.kstest([data['rhv'] for data in values], 'norm')
        print(f"rhv;{test.statistic};{test.pvalue};{'unknown' if test.pvalue < 0.05 else 'normal'}")

        for jkey, jvalues in metrics.items():
            mannwhitneyu = stats.mannwhitneyu([v['rhv'] for v in values], [v['rhv'] for v in jvalues], alternative='greater')
            result = f'{key} > {jkey}' if mannwhitneyu.pvalue < 0.05 else f'{key} . {jkey}'
            print(f'{result} ... {mannwhitneyu}')


    runtime = time()-start
    print(runtime)