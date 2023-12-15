import sys
import copy
from itertools import cycle, dropwhile, islice
import json
from time import time

import numpy as np

from evaluation import Evaluation


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


def greedy(eval: Evaluation):
    travel_min = float('inf')
    src_count = len(eval.src2tgt)
    tgt_count = len(eval.tgt2tgt)

    src_cycled = []
    for i in range(src_count):
        cycled = cycle(range(src_count))  # cycle thorugh the list 'l'
        skipped = dropwhile(lambda x: x != i, cycled)  # drop the values until x==i
        sliced = islice(skipped, None, src_count)  # take the first len(l) values
        src_cycled.append(list(sliced))


    for perm in src_cycled:
        src2tgt = copy.deepcopy(eval.src2tgt)
        tgt2tgt = copy.deepcopy(eval.tgt2tgt)

        sol = {}
        unselected = set(range(tgt_count))
        for i in perm:
            sol[i] = []
            selected = np.argmin(src2tgt[i])
            for src in src2tgt:
                src[selected] = float('inf')
            for tgt in tgt2tgt:
                tgt[selected] = float('inf')
            unselected.remove(selected)
            sol[i].append(selected)
        while len(unselected):
            for i in perm:
                if len(unselected):
                    selected = np.argmin(tgt2tgt[sol[i][-1]])
                    for tgt in tgt2tgt:
                        tgt[selected] = float('inf')
                    unselected.remove(selected)
                    sol[i].append(selected)

        src = []
        tgt = []
        for i, path in sol.items():
            src.extend([i] * len(path))
            tgt.extend(path)

        travel, _ = eval.evaluate((src , tgt))
        if travel < travel_min:
            travel_min = travel
            greedy = (src,tgt)

    return greedy


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage:  greedy1.py <INSTANCE>')
        exit(1)
    file = sys.argv[1]

    sources, targets = load_inst_file(file)

    last_order_time = max(targets, key=lambda t: t[0])[0]
    targets = [(last_order_time-t[0],t[1],t[2]) for t in targets]

    start = time()

    eval = Evaluation(sources, targets)

    ind = greedy(eval)

    print(ind[0])
    print(ind[1])
    print(f'{eval.evaluate(ind)}')
    print(f'runtime {time()-start}')

