import sys
import copy

import numpy as np

from ae import load_inst_file
from evaluation import Evaluation

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage:  greedy1.py <INSTANCE>')
        exit(1)
    file = sys.argv[1]

    sources, targets = load_inst_file(file)

    last_order_time = max(targets, key=lambda t: t[0])[0]
    targets = [(last_order_time-t[0],t[1],t[2]) for t in targets]

    eval = Evaluation(sources, targets)

    src2tgt = copy.deepcopy(eval.src2tgt)
    tgt2tgt = copy.deepcopy(eval.tgt2tgt)

    sol = []
    unselected = set(range(len(targets)))
    for i in range(len(sources)):
        sol.append([])
        selected = np.argmin(src2tgt[i])
        for src in src2tgt:
            src[selected] = float('inf')
        for tgt in tgt2tgt:
            tgt[selected] = float('inf')
        unselected.remove(selected)
        sol[i].append(selected)
    while len(unselected):
        for i in range(len(sources)):
            selected = np.argmin(tgt2tgt[sol[i][-1]])
            for tgt in tgt2tgt:
                tgt[selected] = float('inf')
            unselected.remove(selected)
            sol[i].append(selected)

    src = []
    tgt = []
    for i, path in enumerate(sol):
        src.extend([i] * len(path))
        tgt.extend(path)
    print(f'{eval.evaluate((src , tgt))}')

