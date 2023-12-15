import random
import multiprocessing

from deap import base
from deap import creator
from deap import tools

from evaluation import Evaluation
from greedy import greedy

def minimum(pop):
    return f"[{min(pop, key=lambda ind: ind.fitness.values[0]).fitness.values[0]:.2f}, {min(pop, key=lambda ind: ind.fitness.values[1]).fitness.values[1]:.2f}]"

def average(pop):
    return f"[{sum([ind.fitness.values[0] for ind in pop])/len(pop):.2f}, {sum([ind.fitness.values[1] for ind in pop])/len(pop):.2f}]"

def maximum(pop):
    return f"[{max(pop, key=lambda ind: ind.fitness.values[0]).fitness.values[0]:.2f}, {max(pop, key=lambda ind: ind.fitness.values[1]).fitness.values[1]:.2f}]"

def equal(ind1, ind2):
    return ind1[0]==ind2[0] and ind1[1]==ind2[1]

def unique(pop):
    unique = []
    for idx, i in enumerate(pop):
        for j in pop[idx+1:]:
            if equal(i, j):
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

def mate_aligned(ind1, ind2):
    origins1 = ind1[0]
    origins2 = ind2[0]
    targets1 = ind1[1]
    targets2 = ind2[1]

    size = min(len(targets1), len(targets2))
    # Choose crossover points
    cxpoint1 = random.randint(0, size)
    cxpoint2 = random.randint(0, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    # Initialize the position of each indices in the individuals
    p1, p2 = [0] * size, [0] * size
    for i in range(size):
        p1[targets1[i]] = i
        p2[targets2[i]] = i

    # Apply crossover between cx points
    for i in range(cxpoint1, cxpoint2):
        # Keep track of the selected values
        temp1 = targets1[i]
        temp2 = targets2[i]
        # Swap the matched value
        targets1[i], targets1[p1[temp2]] = temp2, temp1
        targets2[i], targets2[p2[temp1]] = temp1, temp2
        # Position bookkeeping
        p1[temp1], p1[temp2] = p1[temp2], p1[temp1]
        p2[temp1], p2[temp2] = p2[temp2], p2[temp1]

    origins1[cxpoint1:cxpoint2], origins2[cxpoint1:cxpoint2] \
        = origins2[cxpoint1:cxpoint2], origins1[cxpoint1:cxpoint2]

def mutate(ind, low, up, indpb):
    tools.mutUniformInt(ind[0], low, up, indpb)
    tools.mutShuffleIndexes(ind[1], indpb)


creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", tuple, fitness=creator.FitnessMin)

def nsga2(sources, targets, *, cxmethod, cxpb, indpb, mu, ngen, seed=None):
    random.seed(seed)

    eval = Evaluation(sources, targets)

    toolbox = base.Toolbox()
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    toolbox.register("individual", initIndividual, creator.Individual, len(sources), len(targets))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval.evaluate)
    toolbox.register("mate", cxmethod)
    toolbox.register("mutate", mutate, low=0, up=len(sources)-1, indpb=indpb)
    toolbox.register("select", tools.selNSGA2)

    stats = tools.Statistics()
    stats.register("min", minimum)
    stats.register("avg", average)
    stats.register("max", maximum)
    stats.register("unique", lambda pop: len(unique(pop)))

    logbook = tools.Logbook()
    logbook.header = "gen", "unique", "min", "avg", "max"

    gind=greedy(eval)
    pop = toolbox.population(n=mu-1)
    pop.append(creator.Individual(gind))

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

    record = stats.compile(pop)
    logbook.record(gen=0, **record)
    print(logbook.stream, end='')

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

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, mu)

        record = stats.compile(pop)
        logbook.record(gen=gen, **record)
        print('\r' + logbook.stream, end='')

    print()
    return pop, logbook
