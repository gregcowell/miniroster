"""Mini roster 2."""
import logging
from ortools.sat.python import cp_model


class SolutionNotFeasible(Exception):
    """Exception for when there is no feasible solution."""

    pass


log = logging.getLogger("roster")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)5s: %(message)s"
)

# First day must be Monday
num_days = 28
all_days = [day for day in range(1, num_days + 1)]
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

model = cp_model.CpModel()


# Shift variables
shift_vars = {
    (staff_member, role, day, shift): model.NewBoolVar(
        f"staff:{staff_member}_role:{role}_day:{day}_shift:{shift}"
    )
    for staff_member in staff
    for role in staff[staff_member]
    for shift in shifts
    for day in shift_days[shift]
}

# Skill mix variables
skill_mix_vars = {
    (day, shift, rule_num): model.NewBoolVar(
        f"day:{day}_shift:{shift}_rule:{rule_num}"
    )
    for shift in shifts
    for day in shift_days[shift]
    for rule_num, rule in enumerate(skill_mix_rules[shift])
}

# Enforce at least one skill mix rule per shift on a particular day
for shift in shifts:
    for day in shift_days[shift]:
        skill_mix_vars_for_shift_day = [
            skill_mix_vars[(day, shift, rule_num)]
            for rule_num, rule in enumerate(skill_mix_rules[shift])
        ]
        model.Add(sum(skill_mix_vars_for_shift_day) >= 1)

# Enforce skill mix rules
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


# Solve
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

# Display shifts
for day in range(1, num_days + 1):
    print(f"Day {day}: ", end="")
    for shift in shifts:
        if day in shift_days[shift]:
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


# for staff_member in staff:
#     for role in staff[staff_member]:
#         for day in range(1, num_days + 1):
#             for shift in shifts:
#                 if day in shift_days[shift]:
#                     print(shift_vars[(staff_member, role, day, shift)])
