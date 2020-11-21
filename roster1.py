"""Mini roster 1."""
import logging
from ortools.sat.python import cp_model


class SolutionNotFeasible(Exception):
    """Exception for when there is no feasible solution."""

    pass


log = logging.getLogger("treasury")

staff = {
    "LaurenC": [1, 6],
    "Alex": [1, 6],
    "Belinda": [2, 6],
    "Greg": [2, 6],
    "Angela": [2, 6],
    "Naomi": [2, 6],
    "Mike": [3],
    "Mia": [3],
    "LaurenF": [3],
    "Mandy": [4],
    "Sonya": [4],
    "Melinda": [5],
    "Katrina": [5],
}
num_shifts = 5
max_staff = 6
min_staff = 5

model = cp_model.CpModel()


shift_vars = {}
shift_vars = {
    (staff_member, group, shift): model.NewBoolVar(
        f"{staff_member}_group{group}_shift{shift}"
    )
    for staff_member in staff
    for group in staff[staff_member]
    for shift in range(num_shifts)
}


#  Maximum and minimum staff per shift
for shift in range(num_shifts):
    shifts = [
        shift_vars[(staff_member, group, shift)]
        for staff_member in staff
        for group in staff[staff_member]
    ]
    model.Add(sum(shifts) <= max_staff)
    model.Add(sum(shifts) >= min_staff)


# Maximum one shift per person per day
for staff_member in staff:
    for shift in range(num_shifts):
        shifts = [
            shift_vars[(staff_member, group, shift)]
            for group in staff[staff_member]
        ]
        model.Add(sum(shifts) <= 1)


def enforce_days_per_roster(group, days_per_roster):
    for staff_member in staff:
        if group in staff[staff_member]:
            shifts = [
                shift_vars[(staff_member, group, shift)]
                for shift in range(num_shifts)
                for group in staff[staff_member]
            ]
            model.Add(sum(shifts) == days_per_roster)


# Days per roster
enforce_days_per_roster(group=1, days_per_roster=3)
enforce_days_per_roster(group=2, days_per_roster=2)
enforce_days_per_roster(group=3, days_per_roster=2)
enforce_days_per_roster(group=4, days_per_roster=2)
enforce_days_per_roster(group=5, days_per_roster=1)


def enforce_group_together(group, days_per_roster):
    intermediate_shift_vars = [
        model.NewBoolVar(f"shift{shift}") for shift in range(num_shifts)
    ]
    model.Add(sum(intermediate_shift_vars) >= days_per_roster)

    group_staff = []
    for staff_member in staff:
        if group in staff[staff_member]:
            group_staff.append(staff_member)

    for shift in range(num_shifts):
        shift_vars_for_this_shift = []
        for staff_member in group_staff:
            shift_vars_for_this_shift.append(
                shift_vars[(staff_member, group, shift)]
            )
        model.AddBoolAnd(shift_vars_for_this_shift).OnlyEnforceIf(
            intermediate_shift_vars[shift]
        )


# Schedule group 6 together for 1 day
enforce_group_together(group=6, days_per_roster=1)


def enforce_supervisor(group, supervisors):
    group_staff = []
    for staff_member in staff:
        if group in staff[staff_member]:
            group_staff.append(staff_member)

    for staff_member in group_staff:
        for shift in range(num_shifts):
            supervisor_shift_vars = []
            for supervisor in supervisors:
                for group in staff[supervisor]:
                    supervisor_shift_vars.append(
                        shift_vars[(supervisor, group, shift)]
                    )
            model.AddBoolOr(supervisor_shift_vars).OnlyEnforceIf(
                shift_vars[(staff_member, staff[staff_member][0], shift)]
            )


enforce_supervisor(group=3, supervisors=("Mike", "Belinda"))

# Solve
solver = cp_model.CpSolver()
solution_status = solver.Solve(model)
if solution_status == cp_model.INFEASIBLE:
    log.info("Solution is INFEASIBLE")
if solution_status == cp_model.MODEL_INVALID:
    log.info("Solution is MODEL_INVALID")
if solution_status == cp_model.UNKNOWN:
    log.info("Solution is UNKNOWN")
if (
    solution_status != cp_model.FEASIBLE
    and solution_status != cp_model.OPTIMAL
):
    log.info("No feasible solution, raising exception...")
    raise SolutionNotFeasible("No feasible solutions.")


# Display shifts
for shift in range(num_shifts):
    print(f"Day{shift + 1}: ", end="")
    for staff_member in staff:
        for group in staff[staff_member]:
            if solver.Value(shift_vars[(staff_member, group, shift)]) == 1:
                print(f"{staff_member} ", end="")
    print()
