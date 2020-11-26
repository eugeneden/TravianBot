from collections import namedtuple

Unit = namedtuple('Unit', ('name', 'movement_speed'))

units = {
    1: Unit('', ''),
    2: Unit('', ''),
    3: Unit('', ''),
    4: Unit('', ''),

    5: Unit('Паладин', 20/3600),
    6: Unit('Тевтонская конница', 18/3600),

    7: Unit('Стенобитное орудие', 8/3600),
    8: Unit('Катапульта', 6/3600),

    9: Unit('', ''),
    10: Unit('', ''),
    11: Unit('', ''),
    12: Unit('', ''),
}
