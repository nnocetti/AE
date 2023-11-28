import random
import multiprocessing

import requests
from requests.exceptions import ConnectionError

from deap import base
from deap import creator
from deap import tools


OSRM_HOST = 'localhost:5000'
session = requests.Session()


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


def initIndividual(icls, sources_count, targets_count):
    return icls((
        [random.randint(0,sources_count-1) for _ in range(targets_count)],
        random.sample(range(targets_count), targets_count)
    ))

def mate(ind1, ind2):
    tools.cxTwoPoint(ind1[0], ind2[0])
    tools.cxPartialyMatched(ind1[1], ind2[1])

def mutate(ind, low, up, indpb):
    tools.mutUniformInt(ind[0], low, up, indpb)
    tools.mutShuffleIndexes(ind[1], indpb)

class Evaluation:
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets

    def evaluate(self, ind):
        duration_max = 0
        query = ['' for _ in range(len(self.sources))]
        query_order = [[] for _ in range(len(self.sources))]
        deliver_time = [None for _ in range(len(self.targets))]

        # Construyo las urls para realizar las consultas
        # tengo que guardar el orden en que se recorren los destinos para cada origen, para poder calcular el tiempo de entrega a cada destino
        # recorro la codificacion del individuo
        for src, tgt in zip(ind[0], ind[1]):
            query[src] += f";{self.targets[tgt][1]},{self.targets[tgt][2]}"
            query_order[src].append(tgt)
        # para cada origen
        for i in range(len(self.sources)):
            # Si hay algun envio desde ese origen armo la url, consulto y proceso la respuesta
            if query[i]:
                query[i] = f"http://{OSRM_HOST}/route/v1/driving/{self.sources[i][0]},{self.sources[i][1]}{query[i]}"

                for j in range(3):
                    try:
                        data = session.get(query[i]).json()
                    except ConnectionError as error:
                        if j < 2:
                            continue
                        raise error
                    else:
                        break

                # Calculo la duracion del recorrido
                duration = 0
                for j, partial_durations in enumerate(data['routes'][0]['legs']):
                    duration += partial_durations['duration'] + 180
                    # Guardo el tiempo de llegada al destino sumando el tiempo desde que se realizo el pedidio y la duracion del viaje
                    deliver_time[query_order[i][j]] = self.targets[query_order[i][j]][0] + duration

                # Me quedo con la duracion maxima
                if duration > duration_max:
                    duration_max = duration

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return duration_max, deliver_aad


def nsga2(sources, targets, *, ngen, mu, cxpb, indpb, seed=None):
    random.seed(seed)

    eval = Evaluation(sources, targets)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", tuple, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    toolbox.register("individual", initIndividual, creator.Individual, len(sources), len(targets))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval.evaluate)
    toolbox.register("mate", mate)
    toolbox.register("mutate", mutate, low=0, up=len(sources)-1, indpb=indpb)
    toolbox.register("select", tools.selNSGA2)

    stats = tools.Statistics()
    stats.register("min", minimum)
    stats.register("max", maximum)
    stats.register("unique", lambda pop: len(unique(pop)))

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "unique", "min", "max"

    pop = toolbox.population(n=mu)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen):
        # Vary the population
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= cxpb:
                toolbox.mate(ind1, ind2)

                toolbox.mutate(ind1)
                toolbox.mutate(ind2)
                del ind1.fitness.values, ind2.fitness.values
            else:
                for ind in [ind1, ind2]:
                    cp = toolbox.clone(ind)
                    toolbox.mutate(ind)
                    if ind != cp:
                        del ind.fitness.values


        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, mu)

        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)
    
    return pop, logbook
