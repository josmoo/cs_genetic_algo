import numpy as np
from copy import deepcopy
import random

GENERATIONS_AMOUNT = 100
STARTING_POPULATION = 500

# structs
# ---------
class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity


class Course:
    def __init__(self, name, expected_enrollment, preferred_facilitators, other_facilitators):
        self.name = name
        self.expected_enrollment = expected_enrollment
        self.preferred_facilitators = preferred_facilitators
        self.other_facilitators = other_facilitators


class TimeSlot:
    def __init__(self, time):
        self.time = time


class Class:
    def __init__(self, room_index, course_index, facilitator_index, timeslot_index):
        self.room_index = room_index
        self.course_index = course_index
        self.facilitator_index = facilitator_index
        self.timeslot_index = timeslot_index

    def mutate(self):
        self.room_index = random.randint(0, 8)
        self.facilitator_index = random.randint(0, 9)
        self.timeslot_index = random.randint(0, 5)


class Schedule:
    def __init__(self, class_list, fitness):
        self.class_list = class_list
        self.fitness = fitness

    def __lt__(self, other):
        return self.fitness < other.fitness


# ----


# array of all available rooms, 0-8
room_array = np.array([Room("Slater 003", 45), Room("Roman 216", 30), Room("Loft 206", 75)
                          , Room("Roman 201", 50), Room("Loft 310", 108), Room("Beach 201", 60)
                          , Room("Beach 301", 75), Room("Logos 325", 325), Room("Frank 119", 60)]
                      , dtype=object)

# array of all available courses, courtesy of chatgpt, 11 courses
course_array = np.array([
    Course("SLA100A", 50, ("Glen", "Lock", "Banks", "Zeldin"), ("Numen", "Richards")),
    Course("SLA100B", 50, ("Glen", "Lock", "Banks", "Zeldin"), ("Numen", "Richards")),
    Course("SLA191A", 50, ("Glen", "Lock", "Banks", "Zeldin"), ("Numen", "Richards")),
    Course("SLA191B", 50, ("Glen", "Lock", "Banks", "Zeldin"), ("Numen", "Richards")),
    Course("SLA201", 50, ("Glen", "Banks", "Zeldin", "Shaw"), ("Numen", "Richards", "Singer")),
    Course("SLA291", 50, ("Lock", "Banks", "Zeldin", "Singer"), ("Numen", "Richards", "Shaw", "Tyler")),
    Course("SLA303", 60, ("Glen", "Zeldin", "Banks"), ("Numen", "Singer", "Shaw")),
    Course("SLA304", 25, ("Glen", "Banks", "Tyler"), ("Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin")),
    Course("SLA394", 20, ("Tyler", "Singer"), ("Richards", "Zeldin")),
    Course("SLA449", 60, ("Tyler", "Singer", "Shaw"), ("Zeldin", "Uther")),
    Course("SLA451", 100, ("Tyler", "Singer", "Shaw"), ("Zeldin", "Uther", "Richards", "Banks"))
], dtype=object)

# array of all facilitators
facilitator_array = np.array([
    "Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"
], dtype=object)

# array of all available times, 6 times
timeslot_array = np.array([
    10, 11, 12, 1, 2, 3
])


def make_generations(generations):
    number_of_schedules = STARTING_POPULATION
    schedules = generate_random_schedules_array(number_of_schedules)  # random init
    for schedule in schedules:
        fitness_function(schedule)
        schedules.sort()

    for generation in range(generations):

        #  cull
        half = number_of_schedules // 2
        schedules = schedules[half:]

        schedules_copy = deepcopy(schedules)  # this is the one to be propagated
        schedules_copy = propagate(schedules_copy, generation)
        for i in range(half):
            fitness_function(schedules_copy[i])  # rate each new schedule
            schedules = np.append(schedules, schedules_copy[i])  # then add them to the list of schedules

        schedules.sort()
        # print(generation, ' generations: \n')
        # for schedule in schedules:
        #     print(schedule.fitness)
        #
        # print('\n\n')

    return schedules



def generate_random_schedule():
    schedule = Schedule(np.array([Class(random.randint(0,8),0,random.randint(0,9),random.randint(0,5))], dtype=object),0)
    for x in range(1,11):
        schedule.class_list = np.append(schedule.class_list, [Class(random.randint(0,8),x,random.randint(0,9),random.randint(0,5))])
    return schedule


def generate_random_schedules_array(size):
    schedule_array = np.array(generate_random_schedule(),dtype=object)
    for x in range(size-1):
        schedule_array = np.append(schedule_array, generate_random_schedule())
    return schedule_array



# precond: array_of_schedules should be of even size lol
# this function returns an array of only the propagated schedules.
def propagate(array_of_schedules, mutation_rate):
    array_size = array_of_schedules.size
    unused_schedules = set(range(array_size))

    for i in range(array_size):  # for every schedule index i
        if i in unused_schedules:  # as long as it hasn't been used before
            unused_schedules.remove(i)  # use it

            if len(unused_schedules) != 0:  # empty set check
                j = random.choice(list(unused_schedules))  # find a random unused schedule with index j
                unused_schedules.remove(j)  # and use it
            else:
                j = i

            temp_schedule_i = deepcopy(array_of_schedules[i])  # prepare a temp for swap
            first_cut_off = random.randint(0, 8)  # find the first random cut-off point for propagation
            second_cut_off = random.randint(first_cut_off, 10)  # and second
            for k in range(11):  # for 0 till 10
                if k < first_cut_off:  # until first cut-off point

                    array_of_schedules[i].class_list[k] = array_of_schedules[j].class_list[k]  # swap class
                    array_of_schedules[j].class_list[k] = temp_schedule_i.class_list[k]

                    if random.randint(0, mutation_rate) == 0:  # check for mutation
                        array_of_schedules[i].class_list[random.randint(0,10)].mutate()
                    if random.randint(0, mutation_rate) == 0:  # check for mutation
                        array_of_schedules[j].class_list[random.randint(0,10)].mutate()

                elif k > second_cut_off:

                    array_of_schedules[i].class_list[k] = array_of_schedules[j].class_list[k]  # swap class
                    array_of_schedules[j].class_list[k] = temp_schedule_i.class_list[k]

                    if random.randint(0, mutation_rate) == 0:  # check for mutation
                        array_of_schedules[i].class_list[random.randint(0,10)].mutate()
                    if random.randint(0, mutation_rate) == 0:  # check for mutation
                        array_of_schedules[j].class_list[random.randint(0,10)].mutate()
    return array_of_schedules


def fitness_function(schedule):
    schedule.fitness = 0
    room_to_time_dict = {0: set(), 1: set(), 2: set(), 3: set(),  # room_index to time_index
                         4: set(), 5: set(), 6: set(), 7: set(), 8: set()}
    facilitator_to_time_dict = {0: set(), 1: set(), 2: set(), 3: set(), 4: set(),
                                5: set(), 6: set(), 7: set(), 8: set(), 9: set()}
    for class_ in schedule.class_list:  # for every class
        if class_.timeslot_index in room_to_time_dict.get(class_.room_index, {-1}):  # the class is already booked for given time
            schedule.fitness -= .5
        else:
            room_to_time_dict[class_.room_index].add(class_.timeslot_index)  # otherwise book it

        if room_array[class_.room_index].capacity < course_array[class_.course_index].expected_enrollment:  # room too small
            schedule.fitness -= .5
        elif room_array[class_.room_index].capacity > (course_array[class_.course_index].expected_enrollment * 6):  # room 6x too big
            schedule.fitness -= .4
        elif room_array[class_.room_index].capacity > (course_array[class_.course_index].expected_enrollment * 3):  # room 3x too big
            schedule.fitness -= .2
        else:
            schedule.fitness += .3  # room juuuuust right

        if facilitator_array[class_.facilitator_index] in course_array[class_.course_index].preferred_facilitators:
            schedule.fitness += .5  # taught by preferred facilitator
        elif facilitator_array[class_.facilitator_index] in course_array[class_.course_index].other_facilitators:
            schedule.fitness += .2  # taught by other facilitator
        else:
            schedule.fitness -= .1  # not taught by someone that is supposed to teach this course

        if facilitator_array[class_.facilitator_index] in facilitator_to_time_dict.get(class_.facilitator_index, {-1}):
            schedule.fitness -= .2  # if the instructor is already booked for the timeslot
        else:
            facilitator_to_time_dict[class_.facilitator_index].add(class_.timeslot_index)  # otherwise book them
            schedule.fitness += .2

        # activity specific adjustments
        if class_.course_index == 0:  # for SLA100A
            for prev_class_ in schedule.class_list:
                if prev_class_.course_index == 1:  # for SLA100B that have already been booked
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if timeslot_difference > 4:  # if they're >4 hours apart
                        schedule.fitness += .5
                    elif timeslot_difference == 0:  # if they're scheduled at the same time
                        schedule.fitness -= .5
                elif (prev_class_.course_index == 2) or (prev_class_.course_index == 3):  # for SLA191A and SLA191B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if abs(timeslot_difference) == 1:  # for consecutive time slots
                        schedule.fitness += .5
                        if (prev_class_.room_index == 1 or prev_class_.room_index == 3
                                or prev_class_.room_index == 5 or prev_class_.room_index == 6):
                            if (class_.room_index != 1 or class_.room_index != 3
                                    or class_.room_index != 5 or class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                        if (class_.room_index == 1 or class_.room_index == 3
                                or class_.room_index == 5 or class_.room_index == 6):
                            if (prev_class_.room_index != 1 or prev_class_.room_index != 3
                                    or prev_class_.room_index != 5 or prev_class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t

                    elif abs(timeslot_difference) == 2:  # 1 hour apart
                        schedule.fitness += .25
                    elif abs(timeslot_difference) == 0:  # same time slot
                        schedule.fitness -= .25

        if class_.course_index == 1:  # for SLA100B
            for prev_class_ in schedule.class_list:
                if prev_class_.course_index == 0:  # for SLA100B that have already been booked
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if timeslot_difference > 4:  # if they're >4 hours apart
                        schedule.fitness += .5
                    elif timeslot_difference == 0:  # if they're scheduled at the same time
                        schedule.fitness -= .5
                elif (prev_class_.course_index == 2) or (prev_class_.course_index == 3):  # for SLA191A and SLA191B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if abs(timeslot_difference) == 1:  # for consecutive time slots
                        schedule.fitness += .5
                        if (prev_class_.room_index == 1 or prev_class_.room_index == 3
                                or prev_class_.room_index == 5 or prev_class_.room_index == 6):
                            if (class_.room_index != 1 or class_.room_index != 3
                                    or class_.room_index != 5 or class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                        if (class_.room_index == 1 or class_.room_index == 3
                                or class_.room_index == 5 or class_.room_index == 6):
                            if (prev_class_.room_index != 1 or prev_class_.room_index != 3
                                    or prev_class_.room_index != 5 or prev_class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                    elif abs(timeslot_difference) == 2:  # 1 hour apart
                        schedule.fitness += .25
                    elif abs(timeslot_difference) == 0:  # same time slot
                        schedule.fitness -= .25

        if class_.course_index == 2:  # for 191A
            for prev_class_ in schedule.class_list:
                if prev_class_.course_index == 3:  # for 191B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if timeslot_difference > 4:  # if they're >4 hours apart
                        schedule.fitness += .5
                    elif timeslot_difference == 0:  # if they're scheduled at the same time
                        schedule.fitness -= .5
                elif (prev_class_.course_index == 0) or (prev_class_.course_index == 1):  # for 100A and 100B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if abs(timeslot_difference) == 1:  # for consecutive time slots
                        schedule.fitness += .5
                        if (prev_class_.room_index == 1 or prev_class_.room_index == 3
                                or prev_class_.room_index == 5 or prev_class_.room_index == 6):
                            if (class_.room_index != 1 or class_.room_index != 3
                                    or class_.room_index != 5 or class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                        if (class_.room_index == 1 or class_.room_index == 3
                                or class_.room_index == 5 or class_.room_index == 6):
                            if (prev_class_.room_index != 1 or prev_class_.room_index != 3
                                    or prev_class_.room_index != 5 or prev_class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                    elif abs(timeslot_difference) == 2:  # 1 hour apart
                        schedule.fitness += .25
                    elif abs(timeslot_difference) == 0:  # same time slot
                        schedule.fitness -= .25

        if class_.course_index == 3:  # for 191B
            for prev_class_ in schedule.class_list:
                if prev_class_.course_index == 2:  # for 191A
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if timeslot_difference > 4:  # if they're >4 hours apart
                        schedule.fitness += .5
                    elif timeslot_difference == 0:  # if they're scheduled at the same time
                        schedule.fitness -= .5
                elif (prev_class_.course_index == 0) or (prev_class_.course_index == 1):  # for 100A and 100B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if abs(timeslot_difference) == 1:  # for consecutive time slots
                        schedule.fitness += .5
                        if (prev_class_.room_index == 1 or prev_class_.room_index == 3
                                or prev_class_.room_index == 5 or prev_class_.room_index == 6):
                            if (class_.room_index != 1 or class_.room_index != 3
                                    or class_.room_index != 5 or class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                        if (class_.room_index == 1 or class_.room_index == 3
                                or class_.room_index == 5 or class_.room_index == 6):
                            if (prev_class_.room_index != 1 or prev_class_.room_index != 3
                                    or prev_class_.room_index != 5 or prev_class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                    elif abs(timeslot_difference) == 2:  # 1 hour apart
                        schedule.fitness += .25
                    elif abs(timeslot_difference) == 0:  # same time slot
                        schedule.fitness -= .25


        if class_.course_index == 2:  # for 191A
            for prev_class_ in schedule.class_list:
                if prev_class_.course_index == 3:  # for 191B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if timeslot_difference > 4:  # if they're >4 hours apart
                        schedule.fitness += .5
                    elif timeslot_difference == 0:  # if they're scheduled at the same time
                        schedule.fitness -= .5
                elif (prev_class_.course_index == 0) or (prev_class_.course_index == 1):  # for 100A and 100B
                    timeslot_difference = abs(class_.timeslot_index - prev_class_.timeslot_index)
                    if abs(timeslot_difference) == 1:  # for consecutive time slots
                        schedule.fitness += .5
                        if (prev_class_.room_index == 1 or prev_class_.room_index == 3
                                or prev_class_.room_index == 5 or prev_class_.room_index == 6):
                            if (class_.room_index != 1 or class_.room_index != 3
                                    or class_.room_index != 5 or class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                        if (class_.room_index == 1 or class_.room_index == 3
                                or class_.room_index == 5 or class_.room_index == 6):
                            if (prev_class_.room_index != 1 or prev_class_.room_index != 3
                                    or prev_class_.room_index != 5 or prev_class_.room_index != 6):
                                schedule.fitness -= .4  # one of the activities is in Roman or Beach, and the other isn’t
                    elif abs(timeslot_difference) == 2:  # 1 hour apart
                        schedule.fitness += .25
                    elif abs(timeslot_difference) == 0:  # same time slot
                        schedule.fitness -= .25

    #  facilitator load
    for facilitator in facilitator_to_time_dict:
        facilitator_load = len(facilitator_to_time_dict[facilitator])
        if facilitator_load > 4:
            schedule.fitness -= .5
        elif facilitator_load == 1 or facilitator_load == 2:
            schedule.fitness -= .4


if __name__ == '__main__':
    schedules = make_generations(GENERATIONS_AMOUNT)
    winning_schedule = schedules[STARTING_POPULATION-1]
    with open('output.txt', 'w') as file:
        file.write("After " + str(GENERATIONS_AMOUNT) + " generations,\n"
                   "the best schedule was found with a fitness of: " + str(winning_schedule.fitness) + ".\n"
)
        for x in winning_schedule.class_list:
            file.write(course_array[x.course_index].name +
                       ", taught by " + facilitator_array[x.facilitator_index] +
                       ", in room " + room_array[x.room_index].name +
                       " at " + str(timeslot_array[x.timeslot_index]) + "\n")

