import random
from math import sqrt


def get_distance(coords_1, coords_2):
    return round(sqrt((coords_1[0] - coords_2[0]) ** 2 + (coords_1[1] - coords_2[1]) ** 2), 1)


def shake_list(l_):
    list_length = len(l_)
    for i in range(list_length):
        random_index = random.randint(0, list_length - 1)
        l_[i], l_[random_index] = l_[random_index], l_[i]
    return l_
