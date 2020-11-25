"""Mini roster 2."""
import logging
from ortools.sat.python import cp_model


class SolutionNotFeasible(Exception):
    """Exception for when there is no feasible solution."""

    pass


def create_previous_shift_vars(num_days, model, shifts, staff, shift_days):
    """Shift variables for previous roster period."""
    prev_shift_vars = {
        (staff_member, role, day - num_days, shift): model.NewBoolVar(
            f"staff:{staff_member}"
            f"_role:{role}"
            f"_day:{day - num_days}"
            f"_shift:{shift}"
        )
        for staff_member in staff
        for role in staff[staff_member]
        for shift in shifts
        for day in shift_days[shift]
    }
    return prev_shift_vars


def create_shift_vars(prev_shift_vars, model, staff, shifts, shift_days):
    """Shift variables for current roster period."""
    shift_vars = {
        (staff_member, role, day, shift): model.NewBoolVar(
            f"staff:{staff_member}_role:{role}_day:{day}_shift:{shift}"
        )
        for staff_member in staff
        for role in staff[staff_member]
        for shift in shifts
        for day in shift_days[shift]
    }
    # Combine previous and current shift variables
    shift_vars = {**prev_shift_vars, **shift_vars}
    return shift_vars


def enforce_shifts_already_worked(
    staff, previous_shifts, shifts, shift_days, model, shift_vars, num_days
):
    """Enforce shifts already worked."""
    for staff_member in staff:
        for day, shift in enumerate(previous_shifts[staff_member]):
            if shift == "X":
                for shift in shifts:
                    if day + 1 in shift_days[shift]:
                        model.Add(
                            shift_vars[
                                (
                                    staff_member,
                                    staff[staff_member][0],
                                    day + 1 - num_days,
                                    shift,
                                )
                            ]
                            == 0
                        )
            else:
                model.Add(
                    shift_vars[
                        (
                            staff_member,
                            staff[staff_member][0],
                            day + 1 - num_days,
                            shift,
                        )
                    ]
                    == 1
                )


def get_valid_shift_sequence_permutations(
    valid_shift_sequences, days_in_partial_sequence
):
    """Get valid shift sequence permutations."""
    valid_shift_sequence_permutations = []
    num_shift_sequences = len(valid_shift_sequences)
    for shift_sequence in valid_shift_sequences:
        pass
    # Split into atomic units
    # Partials can only be first
    # Only include previous roster if current
    return valid_shift_sequence_permutations


def enforce_shift_sequences(
    staff,
    shift_vars,
    shifts,
    shift_days,
    num_days,
    model,
    valid_shift_sequences,
):
    """Enforce shift sequences."""
    for staff_member in staff:
        shift_vars_for_both_periods = [
            shift_vars[(staff_member, role, day, shift)]
            for role in staff[staff_member]
            for day in range(-num_days + 1, num_days + 1)
            for shift in shifts
            if day in shift_days[shift] or day - num_days in shift_days[shift]
        ]
    # What to add to model ?


def create_skill_mix_vars(model, shifts, shift_days, skill_mix_rules):
    """Create skill mix variables."""
    skill_mix_vars = {
        (day, shift, rule_num): model.NewBoolVar(
            f"day:{day}_shift:{shift}_rule:{rule_num}"
        )
        for shift in shifts
        for day in shift_days[shift]
        for rule_num, rule in enumerate(skill_mix_rules[shift])
    }
    return skill_mix_vars


def enforce_one_skill_mix_rule_per_shift(
    shifts, shift_days, skill_mix_vars, skill_mix_rules, model
):
    """Enforce at least one skill mix rule per shift on a particular day."""
    for shift in shifts:
        for day in shift_days[shift]:
            skill_mix_vars_for_shift_day = [
                skill_mix_vars[(day, shift, rule_num)]
                for rule_num, rule in enumerate(skill_mix_rules[shift])
            ]
            model.Add(sum(skill_mix_vars_for_shift_day) >= 1)


def enforce_skill_mix_rules(
    shifts,
    skill_mix_rules,
    shift_days,
    model,
    shift_vars,
    staff,
    skill_mix_vars,
):
    """Enforce skill mix rules."""
    for shift in shifts:
        for rule_num, rule in enumerate(skill_mix_rules[shift]):
            for role in rule:
                for day in shift_days[shift]:
                    role_count = rule[role]
                    model.Add(
                        sum(
                            shift_vars[(staff_member, role, day, shift)]
                            for staff_member in staff
                            if role in staff[staff_member]
                        )
                        == role_count
                    ).OnlyEnforceIf(skill_mix_vars[(day, shift, rule_num)])


def solve(model):
    """Solve model."""
    solver = cp_model.CpSolver()
    solution_status = solver.Solve(model)
    if solution_status == cp_model.INFEASIBLE:
        log.info("Solution is INFEASIBLE")
    if solution_status == cp_model.MODEL_INVALID:
        log.info("Solution is MODEL_INVALID")
    if solution_status == cp_model.UNKNOWN:
        log.info("Solution is UNKNOWN")
    if solution_status == cp_model.FEASIBLE:
        log.info("Solution is FEASIBLE")
    if solution_status == cp_model.OPTIMAL:
        log.info("Solution is OPTIMAL")
    if (
        solution_status != cp_model.FEASIBLE
        and solution_status != cp_model.OPTIMAL
    ):
        log.info("No feasible solution, raising exception...")
        raise SolutionNotFeasible("No feasible solutions.")
    return solver


def display_shifts(num_days, shifts, shift_days, staff, shift_vars, solver):
    """Display shifts."""
    for day in range(1 - num_days, num_days + 1):
        print(f"Day {day}: ", end="")
        for shift in shifts:
            if day in shift_days[shift] or day + num_days in shift_days[shift]:
                print(f"{shift}: ", end="")
            for staff_member in staff:
                for role in staff[staff_member]:
                    if (staff_member, role, day, shift) in shift_vars:
                        if (
                            solver.Value(
                                shift_vars[(staff_member, role, day, shift)]
                            )
                            == 1
                        ):
                            print(f"{staff_member} ", end="")
        print()


# Main
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
    get_valid_shift_sequence_permutations(
        valid_shift_sequences, days_in_partial_sequence
    )
    enforce_shift_sequences(
        staff,
        shift_vars,
        shifts,
        shift_days,
        num_days,
        model,
        valid_shift_sequences,
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
    solver = solve(model)
    display_shifts(num_days, shifts, shift_days, staff, shift_vars, solver)

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
