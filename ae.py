import itertools
import pickle
from time import time
import os
import sys
import json

import nsga2


CXMETHOD = ['mate_aligned']
CXPB = [0.6]
INDPB = [0.01]
MU = [200]
NGEN = [2500]
#SEEDS = [37, 80, 84, 87, 101, 122, 125, 130, 139, 149, 167, 174, 186, 197, 289, 299, 303, 324, 347, 372, 403, 451, 453, 457, 491, 504, 544, 545, 556, 558]
SEEDS = [37, 80, 84, 87, 101, 122, 125, 130, 139, 149, 167, 174, 186, 197, 289, 299, 303, 324, 347, 372, 403, 451, 453, 457, 491, 504, 544, 545, 556, 558, 594, 595, 632, 641, 685, 723, 777, 800, 805, 807, 821, 836, 872, 899, 946, 963, 967, 992, 993, 994]


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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage:  ae.py <INSTANCE> <DESTINATION_DIR>')
        exit(1)
    file = sys.argv[1]
    dest = sys.argv[2]

    sources, targets = load_inst_file(file)

    # Preprocesamos los datos para acelerar las cuentas
    # Transformamos el tiempo de realizado el pedido en el tiempo de espera de ese pedido en relación al úlitmo ingresado
    # Por ejemplo:
    #     pedido1: 100 -> (100-120) = 20
    #     pedido2: 120 -> (120-120) =  0
    #     pedido3:  90 -> (120- 90) = 30
    # Representa:
    #     el pedido1 tiene 20 segundos más de espera que el ultimo en ingresar
    #     el pedido2 tiene  0 segundos más de espera que el ultimo en ingresar
    #     el pedido3 tiene 30 segundos más de espera que el ultimo en ingresar 
    last_order_time = max(targets, key=lambda t: t[0])[0]
    targets = [(last_order_time-t[0],t[1],t[2]) for t in targets]


    params = list(itertools.product(CXMETHOD, CXPB, INDPB, MU, NGEN, SEEDS))
    for cxmethod, cxpb, indpb, mu, ngen, seed in params:
        timestamp = int(time())
        print(f'timestamp: {timestamp} -> cxmethod {cxmethod}, cxpb {cxpb}, indpb {indpb}, mu {mu}, ngen {ngen}, seed {seed}')

        pop, logbook = nsga2.nsga2(sources, targets, cxmethod=getattr(nsga2, cxmethod), cxpb=cxpb, indpb=indpb, mu=mu, ngen=ngen, seed=seed)

        runtime = time()-timestamp
        rundata = {
            'instance': os.path.basename(file),
            'timestamp': timestamp,
            'runtime': runtime,
            'cxmethod': cxmethod,
            'cxpb': cxpb,
            'indpb': indpb,
            'mu': mu,
            'ngen': ngen,
            'seed': seed,
            'logbook': logbook,
            'pop': pop,
        }
        runfile = f"{dest}/{timestamp}.p"
        with open(runfile, 'wb') as f:
            try:
                pickle.dump(rundata, f)
            except:
                print(f'Unable to dump stats to {runfile}')
        
        print(f'runtime {runtime}')
        print(f'stats in {runfile}')
