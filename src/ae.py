import itertools
import json
import pickle
from time import time
import os
import sys

from nsga2 import nsga2

CXPB = [0.6, 0.7, 0.8]
INDPB = [0.1, 0.01, 0.001]
MU = [52, 128, 200]
SEEDS = [7, 9, 17, 39, 40, 43, 110, 121, 133, 149, 150, 157, 179, 189, 202, 232, 315, 322, 323, 340, 348, 365, 381, 397, 402, 409, 439, 441, 459, 480]
NGEN = [1500]

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print(f'Need one an only one file to load')
        exit(1)
    file = sys.argv[1]
    with open(file) as f:
        try:
            data = json.load(f)
            sources = data['sources']
            targets = data['targets']
        except:
            print(f'Unable to load file {file}')
            exit(1)

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


    params = list(itertools.product(CXPB, INDPB, MU, NGEN, SEEDS))
    for cxpb, indpb, mu, ngen, seed in params:
        timestamp = int(time())
        print(f'timestamp: {timestamp}: cxpb {cxpb}, indpb {indpb}, mu {mu}, ngen {ngen}, seed {seed}')

        pop, logbook = nsga2(sources, targets, ngen=ngen, cxpb=cxpb, indpb=indpb, mu=mu, seed=seed)

        runtime = time()-timestamp
        rundata = {
            'instance': os.path.basename(file),
            'timestamp': timestamp,
            'runtime': runtime,
            'cxpb': cxpb,
            'indpb': indpb,
            'mu': mu,
            'ngen': ngen,
            'seed': seed,
            'logbook': logbook,
            'pop': pop
        }
        runfile = f"../test/{rundata['timestamp']}.p"
        with open(runfile, 'wb') as f:
            try:
                pickle.dump(rundata, f)
            except:
                print(f'Unable to dump stats to {runfile}')
        
        print(f'runtime {runtime}')
        print(f'stats in {runfile}')
        print()
