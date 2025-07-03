import math
import random


# Function to calculate fitness based on wasted space
# returns waste left after cutting
# cutting_pattern is one combination of quantities of small rectangles
def fitness(cutting_pattern, sheet):
    # if all small rectangles can't be cut from sheet return max waste
    if not is_cutting_valid(cutting_pattern, sheet):
        return sheet[0] * sheet[1]

    used_area = sum(count * rectangle[0] * rectangle[1] for rectangle, count in cutting_pattern.items())
    sheet_area = sheet[0] * sheet[1]
    wasted_space = sheet_area - used_area
    return wasted_space


# Function calls cut_rectangles function and returns its value after organizing rectangles in a list
def is_cutting_valid(rectangles, sheet):
    res = []
    rect_list = []
    for r in rectangles.items():
        width = r[0][0]
        height = r[0][1]
        quantity = r[1]
        # rotate element if the width is larger than height
        if width > height:
            rect_list.append(((height, width), quantity))
        else:
            rect_list.append(((width, height), quantity))
    # sort rectangles by their height
    sorted_rectangles = sorted(rect_list, key=lambda rect: rect[0][1], reverse=True)
    # put rectangles in a list
    for el in sorted_rectangles:
        for i in range(el[1]):
            res.append(el[0])
    fitable = cut_rectangles(res, sheet)
    return fitable


# Function checks if all small rectangles can be cut from sheet
# returns True if they can be cut and False if they can't
def cut_rectangles(rectangles, initial_sheet):
    i = 0
    in_row = []
    current_sheet = list(initial_sheet)
    while i < len(rectangles):
        current_rect = rectangles[i]
        vertical_cut = current_rect[0]
        # if it can not fit by height anymore, we have reached the end of sheet
        if current_rect[1] > current_sheet[1]:
            return False
        # if it can fit by width, put the rectangle in the row
        if current_rect[0] <= current_sheet[0]:
            in_row.append(current_rect)
            # cut vertically to width of placed rectangle
            current_sheet[0] -= vertical_cut
            i += 1
        # if it can not fit in the row, place in the next
        else:
            # find the highest rectangle in the row
            highest_rec = max(in_row, key=lambda x: x[1])
            # biggest height in the row
            horizontal_cut = highest_rec[1]
            in_row = []
            # cut horizontally to form a new row
            current_sheet[0] = initial_sheet[0]
            current_sheet[1] = current_sheet[1] - horizontal_cut
    # if all are placed (cut) return true
    return True


# Function for single-point crossover with non-overlapping rectangles
# returns two children from two parents
def crossover(parent1, parent2):
    # create children with the chosen rectangle from parent2
    child1 = {**parent1}
    child2 = {**parent2}

    # make list with all small rectangles
    rectangles = []
    for r in parent1.keys():
        rectangles.append(r)

    # choose randrom index from list representing from which rectangle crossing will be done between parents
    if len(rectangles) == 1:
        crossover_point = 0
    else:
        crossover_point = random.randint(1, (len(rectangles) - 1))
    # do cross over
    for rect in rectangles[crossover_point:]:
        tmp_count = child1[rect]
        child1[rect] = child2[rect]
        child2[rect] = tmp_count

    return child1, child2


# Function for mutation by changing the count of a single rectangle
# returns mutated individual
def mutate(individual):
    mutated_individual = individual.copy()
    rectangle_to_mutate = random.choice(list(mutated_individual.keys()))
    mutated_individual[rectangle_to_mutate] += 1
    return mutated_individual


# Genetic algorithm
def genetic_algorithm(sheet, smaller_rectangles, initial_percentage, population_size=150, generations=75):
    # generation of initial population
    # one dictionary is one possible outcome
    population = []
    for _ in range(population_size):
        individual = {}
        for rectangle in smaller_rectangles:
            individual[rectangle] = random.randint(1, math.ceil(1 / initial_percentage))
        population.append(individual)

    # going through generations
    for generation in range(generations):
        # sort population
        sorted_population = sorted(population, key=lambda x: fitness(x, sheet))
        # elitism - pass the best individuals (without mutation and crossover)
        top_best = math.ceil(population_size * 0.05)
        best_parents = sorted_population[:top_best]
        # parents that will be mutated and crossed over
        parents_end = math.ceil(population_size * 0.5)
        other_parents = sorted_population[top_best:parents_end]
        # perform crossover and mutation
        new_population = best_parents
        random.shuffle(other_parents)
        # making offspring
        i = 0
        while len(new_population) < population_size:
            parent1, parent2 = other_parents[i], other_parents[i + 1]
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.extend([child1, child2])
            i += 2
            # if all the parents have been crossed and the population size is not ideal, shuffle parents and cross again
            if i < len(other_parents):
                random.shuffle(other_parents)
                i = 0

        population = new_population

    # find the best outcome from the best generation
    best_cutting_pattern = min(population, key=lambda individual: fitness(individual, sheet))
    if fitness(best_cutting_pattern, sheet) == sheet[0] * sheet[1]:
        print("No solution found")
        for key in best_cutting_pattern.keys():
            best_cutting_pattern[key] = 0
    return best_cutting_pattern


if __name__ == '__main__':

    print("2D CUTTING")
    while True:
        sheet_width = input("Enter the width of your material: ")
        sheet_height = input("Enter the height of your material: ")
        try:
            if int(sheet_height) > 0 and int(sheet_width) > 0:
                break
            print("You have entered invalid dimension for your material, please try again.")
        except:
            print("Invalid input. Please enter a valid integer.")
    if int(sheet_width) > int(sheet_height):
        sheet = (int(sheet_height), int(sheet_width))
    else:
        sheet = (int(sheet_width), int(sheet_height))

    print("------------------------------------------------------------------")
    smaller_rectangles = []
    i = 1
    while True:
        print("Rectangle number ", i)
        rectangle_width = input("Enter the width of your rectangle: ")
        rectangle_height = input("Enter the height of your rectangle: ")
        try:
            if not (int(rectangle_height) > 0 and int(rectangle_width) > 0):
                print("You have entered invalid dimension for your rectangle, please try again.")
                continue
            rectangle = (int(rectangle_width), int(rectangle_height))
            smaller_rectangles.append(rectangle)
            choice = input("If you want to enter another rectangle, please input 1: ")
            if choice != "1":
                break
            i += 1
        except:
            print("Invalid input. Please enter a valid integer.")

    smaller_areas = 0
    for rect in smaller_rectangles:
        print()
        smaller_areas += rect[0] * rect[1]
    sheet_area = sheet[0] * sheet[1]
    initial_percentage = smaller_areas / sheet_area
    population_size = 80 + math.floor(1 / initial_percentage)
    generations = math.floor(0.75 * population_size)

    best_cutting_pattern = genetic_algorithm(sheet, smaller_rectangles, initial_percentage, population_size,
                                             generations)

    print("Material dimensions: ", sheet, end="")
    print("; Material area: ", sheet_area)
    print("List of inputed rectangles: ", smaller_rectangles)

    print("Waste: ", (fitness(best_cutting_pattern, sheet) / sheet_area)*100, end="")
    print("%")
    # Display results
    print("Best Cutting Pattern:", best_cutting_pattern)
