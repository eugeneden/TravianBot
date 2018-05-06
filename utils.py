import random
from math import sqrt
from datetime import datetime


def get_distance(coords_1, coords_2):
    return round(sqrt((coords_1[0] - coords_2[0]) ** 2 + (coords_1[1] - coords_2[1]) ** 2), 1)


def printl(*args):
    print(datetime.now().strftime('%d.%m.%Y %H:%M:%S'), ' | ', *args)


def shake_list(l):
    list_length = len(l)

    for i in range(list_length):
        random_index = random.randint(0, list_length - 1)
        l[i], l[random_index] = l[random_index], l[i]

    return l
