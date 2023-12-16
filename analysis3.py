import os
import sys
from time import time
from statistics import median, mean, stdev
from math import dist

from scipy import stats

from deap.tools import ParetoFront
from deap.benchmarks.tools import igd, diversity, convergence, hypervolume

import matplotlib.pyplot as plt

from show import load_run_file
from evaluation import Evaluation
from greedy import greedy, load_inst_file


if __name__ == "__main__":
    start = int(time())

    if len(sys.argv) != 2:
        print(f'Usage:  analysis.py <PATH>')
        exit(1)
    path = sys.argv[1]


    sources, targets = load_inst_file(f'{path}/{os.path.basename(os.path.normpath(path))}.json')
    last_order_time = max(targets, key=lambda t: t[0])[0]
    targets = [(last_order_time-t[0],t[1],t[2]) for t in targets]

    eval = Evaluation(sources, targets)
    gsol = greedy(eval)
    gpoint = eval.evaluate(gsol)

    (dirpath, dirnames, filenames) = next(os.walk(f'{path}/runs'))
    if not filenames:
        print('No Files')
        exit()

    ref_front = ParetoFront()
    pointsX = []
    pointsY = []
    raw_data = []
    for file in filenames:
        (instance, timestamp, runtime, cxmethod, cxpb, indpb, mu, ngen, seed, logbook, pop) = load_run_file(f'{dirpath}\{file}')
        ref_front.update(pop)
        run_front = ParetoFront()
        run_front.update(pop)
        x,y = (zip(*[ind.fitness.values for ind in pop]))
        pointsX.append(x)
        pointsY.append(y)
        data = {}
        data['timestamp'] = timestamp
        data['runfront'] = run_front
        data['runtime'] = runtime
        raw_data.append(data)

    ref_front_values = [ind.fitness.values for ind in ref_front]
    ref_front_pointsX, ref_front_pointsY = zip(*ref_front_values)
    nadir_point = (max(ref_front_pointsX), max(ref_front_pointsY))
    ref_hv = hypervolume(ref_front, nadir_point)

    plt.title('Soluciones')
    plt.plot(pointsX,pointsY, "b.")
    plt.plot(ref_front_pointsX, ref_front_pointsY, "r.")
    plt.tight_layout()
    plt.savefig(f'{path}/solutions.png')
    plt.cla()

    runtime = []
    invgd = []
    #gd = []
    #pnd = []
    div = []
    rhv = []
    comp_points = []
    for data in raw_data:
        #print(f"{data['timestamp']}.p")
        runfront = data['runfront']
        run_values = [ind.fitness.values for ind in runfront]
        runtime.append(data['runtime'])
        invgd.append(igd(run_values, ref_front_values))
        #gd.append(convergence(run_front, ref_front_values))
        #pnd.append(len(runfront))
        div.append(diversity(runfront, ref_front_values[0], ref_front_values[-1]))
        hv = hypervolume(runfront, nadir_point)
        rhv.append(hv/ref_hv)


        min_distance = float('inf')
        point = None
        for p in run_values:
            distance = dist(p, gpoint)
            if distance < min_distance:
                min_distance = distance
                point = p
        comp_points.append(point)
    t1 = [v1 for v1, _ in comp_points]
    t2 = [v2 for _, v2 in comp_points]

    print(f"{median(rhv):.4f};{mean(rhv):.4f};{stdev(rhv):.4f};{stats.normaltest(rhv).pvalue:.3f}")
    print(f"{median(invgd):.2f};{mean(invgd):.2f};{stdev(invgd):.4f};{stats.normaltest(invgd).pvalue:.3f}")
    #print(f"{median(gd):.2f};{mean(gd):.2f};{stdev(gd):.4f};{stats.normaltest(gd).pvalue:.3f}")
    #print(f"{median(pnd):.2f};{mean(pnd):.2f};{stdev(pnd):.4f};{stats.normaltest(pnd).pvalue:.3f}")
    print(f"{median(div):.4f};{mean(div):.4f};{stdev(div):.4f};{stats.normaltest(div).pvalue:.3f}")
    print(f"{median(runtime):.4f};{mean(runtime):.1f};{stdev(runtime):.2f};{stats.normaltest(runtime).pvalue:.3f}")
    print(f"{median(t1):.1f};{mean(t1):.1f};{stdev(t1):.1f};{stats.normaltest(t1).pvalue:.3f}")
    print(f"{median(t2):.1f};{mean(t2):.1f};{stdev(t2):.1f};{stats.normaltest(t2).pvalue:.3f}")

    print(f"{gpoint[0]:.1f};{median(t1):.1f};{(gpoint[0]-median(t1))*100/gpoint[0]:.1f}")
    print(f"{gpoint[1]:.1f};{median(t2):.1f};{(gpoint[1]-median(t2))*100/gpoint[1]:.1f}")

    fig = plt.figure()
    fig.subplots_adjust(wspace=0.60)
    for idx, (title,metric) in enumerate([('RHV',rhv), ('IGD',invgd), ('SPREAD',div), ('RT',runtime)]):
        ax = fig.add_subplot(1,4, idx+1)
        ax.set_title(title)
        ax.set_xticks([])
        mmean = mean(metric)
        mstddev = stdev(metric)
        ax.vlines([1], mmean-mstddev, mmean+mstddev, color=[0.12156863,0.46666667,0.70588235,1], linestyle='-', lw=6)
        showmeans = ax.violinplot(metric, showmedians=True, showmeans=True)
        showmeans['cmedians'].set_color('C1')
    plt.tight_layout()
    plt.savefig(f'{path}/violin.png')
