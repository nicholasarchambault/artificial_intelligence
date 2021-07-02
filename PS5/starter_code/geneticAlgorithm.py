#!/usr/bin/env python3

# Please feel free to modify any part of the code or add any functions, or modify the argument of 
# the given functions. But please keep the name of the given functions

# Please feel free to import any libraries you need.

# You are required to finish the genetic_algorithm function, and you may need to complete crossover, 
# mutate and select.

import bisect
import matplotlib.pyplot as plt
import random

states = 10
digits = 3
elites = 5     # Number of elites to pick
mutation_prob = 0.5   # Mutation probability

def crossover(old_gen, probability_crossover):
    new_population = []

    father = old_gen[0]
    mother = old_gen[0]
    if random.random() < probability_crossover:
        # Three pt crossover
        position_one = random.randint(0, states * digits - 3)
        position_two = random.randint(position_one + 1, states * digits - 2)
        position_three = random.randint(position_two + 1, states * digits - 1)
        new_population.append(father[:position_one] + mother[position_one:position_two] + father[position_two:position_three] + mother[position_three:])
    else:
        # Random parent selection
        new_population.append(father if random.random() < 0.5 else mother)

    return new_population

def mutate(old_gen, probability_mutation):
    new_gen = old_gen
    if random.random() < probability_mutation:
        for i in range(states * digits):
            if random.random() < mutation_prob:
                x = random.randint(1, 4) if i % 3 == 0 else random.randint(0, 9)
                new_gen = new_gen[:i] + str(x) + new_gen[i+1:] 

    return new_gen

def select(old_gen):
    # Rank selection
    new_population = []

    values = generate_values(len(old_gen))
    # Get parents
    r = random.randint(1, len(old_gen) * (len(old_gen) + 1) / 2)   
    new_population.append(old_gen[bisect.bisect_left(values, r)])
    r = random.randint(1, len(old_gen) * (len(old_gen) + 1) / 2)
    new_population.append(old_gen[bisect.bisect_left(values, r)])

    return new_population

def generate_values(n):
    # Function generating sequence
    counter = 0
    values = []
    for i in range(n, 0, -1):
        counter += i
        values.append(counter)
    assert len(values) == n
    return values

def genetic_algorithm(population, food_map_file_name, max_generation, probability_crossover, probability_mutation):
    sum_stats = []   # Min, max, average
    max_fitness = -1
    max_individual = ""
    max_trial = ""
    
    food_map, map_size = get_map(food_map_file_name)

    for i in range(max_generation + 1):
        # Track stats
        fitness = []
        current_max = -1; current_min = 32*32; current_sum = 0
        
        # Evaluate fitness for each individual
        for j in range(len(population)):
            trial, current_fitness = ant_simulator(food_map, map_size, population[j])
            fitness.append(current_fitness)
            
            # Update stats
            if current_fitness > current_max:
                current_max = current_fitness
                max_fitness = current_fitness
                max_individual = population[j]
                max_trial = trial
            current_min = current_fitness if current_fitness < current_min else current_min
            current_sum = current_sum + current_fitness

        sum_stats.append([current_max, current_min, current_sum / len(population)])

        # Get new population when current is not last
        if i < max_generation:
            new_population = []
            
            # Sort by fitness score
            population = [ind for _, ind in sorted(zip(fitness, population), reverse=True)]
            # Elitism
            new_population.extend(population[:elites])
            # Others
            for j in range(len(population) - 1):
                new_population.append(mutate(crossover(select(population), probability_crossover)[0], probability_mutation))
            
            population = new_population

    return max_fitness, max_individual, max_trial, sum_stats, population


def initialize_population(num_population):
    population = []
    for i in range(num_population):
        individual = ""
        for j in range(states):
            individual = individual + str(random.randint(100, 499))
        population.append(individual)

    return population
    
def ant_simulator(food_map, map_size, ant_genes):
    """
    parameters:
        food_map: a list of list of strings, representing the map of the environment with food
            "1": there is a food at the position
            "0": there is no food at the position
            (0, 0) position: the top left corner of the map
            (x, y) position: x is the row, and y is the column
        map_size: a list of int, the dimension of the map. It is in the format of [row, column]
        ant_genes: a string with length 30. It encodes the ant's genes, for more information, please refer to the handout.
    
    return:
        trial: a list of list of strings, representing the trials
            1: there is food at that position, and the spot was not visited by the ant
            0: there is no food at that position, and the spot was not visited by the ant
            empty: the spot has been visited by the ant
    
    It takes in the food_map and its dimension of the map and the ant's gene information, and return the trial in the map
    """
    
    step_time = 200
    
    trial = []
    for i in food_map:
        line = []
        for j in i:
            line.append(j)
        trial.append(line)

    position_x, position_y = 0, 0
    orientation = [(1, 0), (0, -1), (-1, 0), (0, 1)] # face down, left, up, right
    fitness = 0
    state = 0
    orientation_state = 3
    gene_list = [ant_genes[i : i + 3] for i in range(0, len(ant_genes), 3)]
    
    for i in range(step_time):
        if trial[position_x][position_y] == "1":
            fitness += 1
        trial[position_x][position_y] = " "
        
        sensor_x = (position_x + orientation[orientation_state][0]) % map_size[0]
        sensor_y = (position_y + orientation[orientation_state][1]) % map_size[1]
        sensor_result = trial[sensor_x][sensor_y]
        
        if sensor_result == "1":
            state = int(gene_list[state][2])
        else:
            state = int(gene_list[state][1])
        
        action = gene_list[state][0]

        if action == "1":     # move forward
            position_x = (position_x + orientation[orientation_state][0]) % map_size[0]
            position_y = (position_y + orientation[orientation_state][1]) % map_size[1]
        elif action == "2":   # turn right
            orientation_state = (orientation_state + 1) % 4
        elif action == "3":   # turn left
            orientation_state = (orientation_state - 1) % 4
        elif action == "4":   # do nothing
            pass
        else:
            raise Exception("invalid action number!")
    
    return trial, fitness
        
def get_map(file_name):
    """
    parameters:
        file_name: a string, the name of the file which stored the map. The first line of the map is the dimension (row, column), the rest is the map
            1: there is a food at the position
            0: there is no food at the position
    
    return:
        food_map: a list of list of strings, representing the map of the environment with food
            "1": there is a food at the position
            "0": there is no food at the position
            (0, 0) position: the top left corner of the map
            (x, y) position: x is the row, and y is the column
        map_size: a list of int, the dimension of the map. It is in the format of [row, column]
    
    It takes in the file_name of the map, and return the food_map and the dimension map_size
    """
    food_map = []
    map_file = open(file_name, "r")
    first_line = True
    map_size = []
    
    for line in map_file:
        line = line.strip()
        if first_line:
            first_line = False
            map_size = line.split()
            continue
        if line:
            food_map.append(line.split())
    
    map_file.close()
    return food_map, [int(i) for i in map_size]

def display_trials(trials, target_file):
    """
    parameters:
        trials: a list of list of strings, representing the trials
            1: there is food at that position, and the spot was not visited by the ant
            0: there is no food at that position, and the spot was not visited by the ant
            empty: the spot has been visited by the ant
        taret_file: a string, the name the target_file to be saved
    
    It takes in the trials, and target_file, and saved the trials in the target_file. You can open the target_file to take a look at the ant's trial.
    """
    trial_file = open(target_file, "w")
    for line in trials:
        trial_file.write(" ".join(line))
        trial_file.write("\n")
    trial_file.close()

if __name__ == "__main__":
    population_size = 100
    population = initialize_population(population_size)
    food_map_file_name = "muir.txt"

    max_generation = 200
    probability_crossover = 0.3
    probability_mutation = 0.2
    max_fitness, max_individual, max_trial, sum_stats, population = genetic_algorithm(population, food_map_file_name, max_generation, probability_crossover, probability_mutation)

    display_trials(max_trial, "max_trial.txt")
    
    plt.figure(1)
    plt.plot([i for i in range(len(sum_stats))], [i[0] for i in sum_stats], marker = "o")
    plt.xlabel("Generation")
    plt.xlim((0, 200))
    plt.ylim((0, max(i[0] for i in sum_stats) + 10))
    plt.ylabel("Fittest Individual")
    plt.savefig("max_fitness_per_gen.png")
    
    plt.figure(2)
    muir_fitness = []
    santafe_fitness = []
    muir_food_map, muir_map_size = get_map("muir.txt")
    santafe_food_map, santafe_map_size = get_map("santafe.txt")

    for i in population:
        trial, individual_muir_fitness = ant_simulator(muir_food_map, muir_map_size, i)
        trial, individual_santafe_fitness = ant_simulator(santafe_food_map, santafe_map_size, i)
        muir_fitness.append(individual_muir_fitness)
        santafe_fitness.append(individual_santafe_fitness)

    plt.plot([i for i in range(len(muir_fitness))], muir_fitness, marker = "D", color = "indigo", label = "muir")
    plt.plot([i for i in range(len(santafe_fitness))], santafe_fitness, marker = "D", color = "darkorange", label = "santa fe")
    plt.xlabel("Individuals in Last Generation")
    plt.xlim((0, population_size))
    plt.ylim((0, max(muir_fitness + santafe_fitness) + 10))
    plt.ylabel("Fitness")
    plt.legend()
    plt.savefig("fitness_of_last_gen.png")
    
    '''
    # Example of how to use get_map, ant_simulator and display trials function
    food_map, map_size = get_map("muir.txt")
    ant_genes = "335149249494173115455311387263"
    trial, fitness = ant_simulator(food_map, map_size, ant_genes)
    display_trials(trial, "trial.txt")
    '''
