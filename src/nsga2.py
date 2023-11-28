import random
import multiprocessing

from deap import base
from deap import creator
from deap import tools

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
