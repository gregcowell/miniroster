"""Data for roster2."""


# First day must be Monday
num_days = 28
# all_days = [day for day in range(1, num_days + 1)]
week_days = [
    day
    for day in range(1, num_days + 1)
    if day % 7 != 0 and (day + 1) % 7 != 0
]
week_ends = [
    day for day in range(1, num_days + 1) if day % 7 == 0 or (day + 1) % 7 == 0
]

# print(week_days, week_ends)

staff = {
    "R1": ["R"],
    "R2": ["R"],
    "R3": ["R"],
    "R4": ["R"],
    "R5": ["R"],
    "R6": ["R"],
    "R7": ["R"],
    "R8": ["R"],
    "R9": ["R"],
}

shifts = ["L", "S", "N", "NW", "W"]

shift_days = {
    "L": week_days,
    "S": week_days,
    "N": week_days,
    "NW": week_ends,
    "W": week_ends,
}

skill_mix_rules = {
    "L": ({"R": 1},),
    "S": ({"R": 5}, {"R": 6}),
    "N": ({"R": 1},),
    "NW": ({"R": 1},),
    "W": ({"R": 1},),
}

# Valid Shift Sequences
# Can only have a maximum of one of each
# sequence per roster period at the moment
valid_shift_sequences = [
    ["L", "L", "L", "X", "N", "NW", "NW", "X", "X", "X", "L", "L", "X", "X"],
    ["S", "S", "S", "S", "X", "W", "W", "X", "S", "S", "S", "S", "X", "X"],
    ["S", "S", "S", "S", "S", "X", "X"],
    ["S", "S", "S", "S", "S", "X", "X", "S", "S", "S", "S", "S", "X", "X"],
    ["N", "N", "N", "N", "X", "X", "X"],
]

# Set previous shift variables to same as spread sheet
previous_shifts = {
    "R1": [
        "L",
        "L",
        "L",
        "X",
        "N",
        "NW",
        "NW",
        "X",
        "X",
        "X",
        "L",
        "L",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
    ],
    "R2": [
        "N",
        "N",
        "N",
        "N",
        "X",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "W",
        "W",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
    ],
    "R3": [
        "S",
        "S",
        "S",
        "S",
        "X",
        "W",
        "W",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "L",
        "L",
        "L",
        "X",
        "N",
        "NW",
        "NW",
    ],
    "R4": [
        "X",
        "X",
        "X",
        "L",
        "L",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "N",
        "N",
        "N",
        "N",
        "X",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
    ],
    "R5": [
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "L",
        "L",
        "L",
        "X",
        "N",
        "NW",
        "NW",
        "X",
        "X",
        "X",
        "L",
        "L",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
    ],
    "R6": [
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "W",
        "W",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "N",
        "N",
        "N",
        "N",
        "X",
        "X",
        "X",
    ],
    "R7": [
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "L",
        "L",
        "L",
        "X",
        "N",
        "NW",
        "NW",
        "X",
        "X",
        "X",
        "L",
        "L",
        "X",
        "X",
    ],
    "R8": [
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "N",
        "N",
        "N",
        "N",
        "X",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "X",
        "W",
        "W",
    ],
    "R9": [
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
        "S",
        "S",
        "S",
        "S",
        "S",
        "X",
        "X",
    ],
}
