"""Mini roster 2."""
import logging
from itertools import product
from ortools.sat.python import cp_model

log = logging.getLogger("roster")


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


def enforce_completion_of_shift_segments(
    valid_shift_sequences,
    days_in_partial_sequence,
    previous_shifts,
    shift_vars,
    model,
    staff,
    shift_days,
    shifts,
):
    """Enforce completion of shift segments."""
    shift_sequence_begin_segments = []
    shift_sequence_end_segments = []

    for valid_shift_sequence in valid_shift_sequences:
        if len(valid_shift_sequence) > days_in_partial_sequence:
            shift_sequence_begin_segments.append(
                valid_shift_sequence[0:days_in_partial_sequence:]
            )
            shift_sequence_end_segments.append(
                valid_shift_sequence[-days_in_partial_sequence:]
            )
    for staff_member in previous_shifts:
        for seg_num, shift_sequence_begin_segment in enumerate(
            shift_sequence_begin_segments
        ):
            if (
                shift_sequence_begin_segment
                == previous_shifts[staff_member][-days_in_partial_sequence:]
            ):
                shift_sequence_end_segment = shift_sequence_end_segments[
                    seg_num
                ]
                for day_num, shift in enumerate(shift_sequence_end_segment):
                    if shift == "X":
                        for shift in shifts:
                            if day_num + 1 in shift_days[shift]:
                                model.Add(
                                    shift_vars[
                                        (
                                            staff_member,
                                            staff[staff_member][0],
                                            day_num + 1,
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
                                    day_num + 1,
                                    shift,
                                )
                            ]
                            == 1
                        )


def get_valid_shift_sequence_permutations(
    valid_shift_sequences,
    days_in_partial_sequence,
    num_days,
    shift_days,
    shifts,
):
    """Get valid shift sequence permutations."""
    shift_sequence_end_segments = []
    for valid_shift_sequence in valid_shift_sequences:
        if len(valid_shift_sequence) > days_in_partial_sequence:
            shift_sequence_end_segments.append(
                valid_shift_sequence[-days_in_partial_sequence:]
            )
    # Partial days in sequence must be half of size of maximum valid sequence
    repeat = num_days // days_in_partial_sequence

    valid_shift_sequence_permutations_interim = []
    for shift_sequence in product(valid_shift_sequences, repeat=repeat):
        valid_shift_sequence_permutations_interim.append(shift_sequence)
    for shift_sequence in product(valid_shift_sequences, repeat=repeat - 1):
        for shift_sequence_end_segment in shift_sequence_end_segments:
            valid_shift_sequence_permutations_interim.append(
                shift_sequence_end_segment + list(shift_sequence)
            )

    valid_shift_sequence_permutations = []
    for tuple_of_shift_lists in valid_shift_sequence_permutations_interim:
        # tuple of lists -> tuple of shifts
        all_shifts = []
        for list_of_shifts in tuple_of_shift_lists:
            for shift in list_of_shifts:
                all_shifts.append(shift)
        # Truncate to period
        valid_shift_sequence_permutations.append(tuple(all_shifts[0:num_days]))

    valid_shift_sequence_permutations_booleans = []

    for tuple_of_shifts in valid_shift_sequence_permutations:
        shift_booleans = []
        for day_num, shift in enumerate(tuple_of_shifts):
            shifts_on_day_num = get_shifts_on_day_num(
                day_num + 1, shift_days, shifts
            )
            for shift_on_day in shifts_on_day_num:
                if shift_on_day == shift:
                    shift_booleans.append(1)
                else:
                    shift_booleans.append(0)
        shift_booleans = tuple(shift_booleans)
        valid_shift_sequence_permutations_booleans.append(shift_booleans)

    return valid_shift_sequence_permutations_booleans


def get_shifts_on_day_num(day_num, shift_days, shifts):
    """Get list of shifts on day number."""
    shifts_on_day_num = []
    for shift in shifts:
        if day_num in shift_days[shift]:
            shifts_on_day_num.append(shift)
    return shifts_on_day_num


def get_length_of_list_of_iterables(list_of_tuples):
    """Get the total length of a list of tuples."""
    length = 0
    for tuple_item in list_of_tuples:
        length += len(tuple_item)
    return length


def enforce_shift_sequences(
    staff,
    shift_vars,
    shifts,
    shift_days,
    num_days,
    model,
    valid_shift_sequence_permutations_booleans,
):
    """Enforce shift sequences."""
    staff_list = list(staff.keys())
    for staff_member in staff_list:
        shift_vars_for_current_period = [
            shift_vars[(staff_member, role, day, shift)]
            for role in staff[staff_member]
            for day in range(1, num_days + 1)
            for shift in shifts
            if day in shift_days[shift] or day - num_days in shift_days[shift]
        ]
        # Does not currently work if multiple roles
        model.AddAllowedAssignments(
            shift_vars_for_current_period,
            valid_shift_sequence_permutations_booleans,
        )


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


def configure_objective(
    model, shift_vars, staff, unpleasant_shifts, num_days, shift_days,
):
    """Configure objective function.

    Need to allocate unpleasant shifts fairly so minimise
    total number of unpleasant shifts over previous and
    current roster periods. Can add weights to different
    unpleasant shifts if desired.
    """
    max_unpleasant_shifts = model.NewIntVar(
        0, 2 * num_days, "max_unpleasant_shifts"
    )

    for staff_member in staff:
        model.Add(
            sum(
                shift_vars[(staff_member, role, day, shift)]
                for role in staff[staff_member]
                for shift in unpleasant_shifts
                for day in range(-num_days + 1, num_days + 1)
                if day in shift_days[shift]
                or day + num_days in shift_days[shift]
            )
            <= max_unpleasant_shifts
        )

    model.Minimize(max_unpleasant_shifts)
    return max_unpleasant_shifts


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


def display_shifts_by_day(
    num_days, shifts, shift_days, staff, shift_vars, solver
):
    """Display shifts by day."""
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


def display_shifts_by_staff(
    num_days,
    shifts,
    shift_days,
    staff,
    shift_vars,
    solver,
    max_unpleasant_shifts,
):
    """Display shifts by staff."""
    for staff_member in staff:
        print(f"{staff_member}: ", end="")
        for day in range(1, num_days + 1):
            shift_worked = "X"
            for shift in shifts:
                if day in shift_days[shift]:
                    for role in staff[staff_member]:

                        if (
                            solver.Value(
                                shift_vars[(staff_member, role, day, shift)]
                            )
                            == 1
                        ):
                            shift_worked = shift
            print(f"{shift_worked:2} ", end="")

        print()
    print(
        f"Maximum unpleasant shifts over previous "
        f"and current period is {solver.Value(max_unpleasant_shifts)}"
    )
