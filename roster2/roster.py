"""Mini roster 2."""
import logging
from ortools.sat.python import cp_model

from logic import (
    create_previous_shift_vars,
    create_shift_vars,
    create_skill_mix_vars,
    display_shifts_by_staff,
    enforce_shifts_already_worked,
    enforce_skill_mix_rules,
    enforce_one_skill_mix_rule_per_shift,
    enforce_shift_sequences,
    get_valid_shift_sequence_permutations,
    solve,
)

# from memory_profiler import profile


def main():
    """Run main program."""
    # First day must be Monday
    num_days = 28
    # all_days = [day for day in range(1, num_days + 1)]
    week_days = [
        day
        for day in range(1, num_days + 1)
        if day % 7 != 0 and (day + 1) % 7 != 0
    ]
    week_ends = [
        day
        for day in range(1, num_days + 1)
        if day % 7 == 0 or (day + 1) % 7 == 0
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
        [
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

    # print(previous_shifts)

    model = cp_model.CpModel()
    previous_shift_vars = create_previous_shift_vars(
        num_days, model, shifts, staff, shift_days
    )
    shift_vars = create_shift_vars(
        previous_shift_vars, model, staff, shifts, shift_days
    )
    enforce_shifts_already_worked(
        staff, previous_shifts, shifts, shift_days, model, shift_vars, num_days
    )
    days_in_partial_sequence = 7
    valid_shift_sequence_permutations_booleans = get_valid_shift_sequence_permutations(
        valid_shift_sequences,
        days_in_partial_sequence,
        num_days,
        shift_days,
        shifts,
    )
    enforce_shift_sequences(
        staff,
        shift_vars,
        shifts,
        shift_days,
        num_days,
        model,
        valid_shift_sequence_permutations_booleans,
    )
    skill_mix_vars = create_skill_mix_vars(
        model, shifts, shift_days, skill_mix_rules
    )

    enforce_one_skill_mix_rule_per_shift(
        shifts, shift_days, skill_mix_vars, skill_mix_rules, model
    )
    enforce_skill_mix_rules(
        shifts,
        skill_mix_rules,
        shift_days,
        model,
        shift_vars,
        staff,
        skill_mix_vars,
    )
    print("Starting solver....")
    solver = solve(model)
    # display_shifts_by_day(
    #     num_days, shifts, shift_days, staff, shift_vars, solver
    # )
    print()
    display_shifts_by_staff(
        num_days, shifts, shift_days, staff, shift_vars, solver
    )
    # for staff_member in staff:
    #     for role in staff[staff_member]:
    #         for day in range(1 - num_days, num_days + 1):
    #             for shift in shifts:
    #                 if (
    #                     day in shift_days[shift]
    #                     or day + num_days in shift_days[shift]
    #                 ):
    #                     print(shift_vars[(staff_member, role, day, shift)])


log = logging.getLogger("roster")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)5s: %(message)s"
)
main()


# Objective function, number of shifts equal
# Equal numbers of weekly sequences over time
