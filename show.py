import pickle
import os
import sys

from deap.tools import ParetoFront
import matplotlib.pyplot as plt

from analysis import load_run_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Need only one argument')
        exit(1)

    arg = sys.argv[1]

    print('file           instance       runtime        cxmethod  cxpb      indpb     mu        ngen      seed      min                 avg                 max                 unique')
    if os.path.isdir(arg):
        for (dirpath, dirnames, filenames) in os.walk(arg):
            for file in filenames:
                instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop = load_run_file(f'{arg}\{file}')
                print(f'{file: <15}{instance: <15}{runtime: <15.2f}{cxmethod: <10}{cxpb: <10}{indpb: <10}{mu: <10}{ngen: <10}{seed: <10}{logbook.select("min")[-1]: <20}{logbook.select("avg")[-1]: <20}{logbook.select("max")[-1]: <20}{logbook.select("unique")[-1]: <20}')
    else:
        instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop = load_run_file(arg)

        file = os.path.basename(arg)
        print(f'{file: <15}{instance: <15}{runtime: <15.2f}{cxmethod: <10}{cxpb: <10}{indpb: <10}{mu: <10}{ngen: <10}{seed: <10}{logbook.select("min")[-1]: <20}{logbook.select("avg")[-1]: <20}{logbook.select("max")[-1]: <20}{logbook.select("unique")[-1]: <20}')

        pareto_front = ParetoFront()
        pareto_front.update(pop)

        x, y = zip(*[ind.fitness.values for ind in pop])
        pfx, pfy = zip(*[ind.fitness.values for ind in pareto_front])

        plt.title(timestamp)
        plt.plot(x, y, "b.")
        plt.plot(pfx, pfy, "r.")
        plt.show()
