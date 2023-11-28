import pickle
import os
import sys
import json

from deap.benchmarks.tools import hypervolume
from deap.tools import ParetoFront
import matplotlib.pyplot as plt

from evaluation import Evaluation


def minimum(pop):
    return f"[{min(pop, key=lambda ind: ind.fitness.values[0]).fitness.values[0]:.2f}, {min(pop, key=lambda ind: ind.fitness.values[1]).fitness.values[1]:.2f}]"

def maximum(pop):
    return f"[{max(pop, key=lambda ind: ind.fitness.values[0]).fitness.values[0]:.2f}, {max(pop, key=lambda ind: ind.fitness.values[1]).fitness.values[1]:.2f}]"

def unique(pop):
    unique = []
    for idx, i in enumerate(pop):
        for j in pop[idx+1:]:
            if i[0]==j[0] and i[1]==j[1]:
                break
        else:
            unique.append(i)
    return unique

def load_file(file, *, dir=None):
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


if len(sys.argv) not in [2, 3]:
    print(f'Need one or two arguments')
    exit(1)

arg = sys.argv[1]

if os.path.isdir(arg):
    for (dirpath, dirnames, filenames) in os.walk(arg):
        print('file           instance       runtime        cxpb      indpb     mu        ngen      seed      min                 max                 unique')
        for file in filenames:
            instance, timestamp, runtime, cxpb, indpb, mu, ngen, seed, logbook, pop = load_file(file, dir=arg)
            print(f'{file: <15}{instance: <15}{runtime: <15.2f}{cxpb: <10}{indpb: <10}{mu: <10}{ngen: <10}{seed: <10}{minimum(pop): <20}{maximum(pop): <20}{len(unique(pop))}')
else:
    instance, timestamp, runtime, cxpb, indpb, mu, ngen, seed, logbook, pop = load_file(arg)

    if len(sys.argv) == 2:
        file = os.path.basename(arg)
        ind_unique = unique(pop)
        print('file           instance       runtime        cxpb      indpb     mu        ngen      seed      min                 max                 unique')
        print(f'{file: <15}{instance: <15}{runtime: <15.2f}{cxpb: <10}{indpb: <10}{mu: <10}{ngen: <10}{seed: <10}{minimum(pop): <20}{maximum(pop): <20}{len(unique(ind_unique))}')

        pareto_front = ParetoFront()
        pareto_front.update(pop)

        print("Final population hypervolume is %f" % hypervolume(pop))

        x, y = zip(*[ind.fitness.values for ind in pop])
        pfx, pfy = zip(*[ind.fitness.values for ind in pareto_front])

        plt.title(timestamp)
        plt.plot(x, y, "b.")
        plt.plot(pfx, pfy, "r.")
        plt.axis("tight")
        plt.show()
    else:
        ind = int(sys.argv[2])

        file = 'inst1.json'
        with open(file) as f:
            data = json.load(f)
            sources = data['sources']
            targets = data['targets']
        last_order_time = max(targets, key=lambda t: t[0])[0]
        targets = [(last_order_time-t[0],t[1],t[2]) for t in targets]
        evaluation = Evaluation(sources, targets)

        print(evaluation.evaluate(pop[ind], show=True))

