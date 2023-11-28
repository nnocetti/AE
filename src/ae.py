import itertools
import json
import pickle
from time import time
import os
import sys

from nsga2 import nsga2

#CXPB = [0.6, 0.7, 0.8]
#INDPB = [0.1, 0.01, 0.001]
#MU = [100, 200, 300]
#SEEDS = [11, 53, 71, 127, 643]
#NGEN = [250]

CXPB = [0.8]
INDPB = [0.001]
MU = [100]
SEEDS = [71]
NGEN = [250]

if __name__ == "__main__":
    start = time()
    
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
        pop, logbook = nsga2(sources, targets, ngen=ngen, cxpb=cxpb, indpb=indpb, mu=mu, seed=seed)

        rundata = {
            'instance': os.path.basename(file),
            'timestamp': int(start),
            'runtime': time()-start,
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

        print(f'Stats in {runfile}')
