"""Mini roster 2."""
import logging
from ortools.sat.python import cp_model

from data import (
    num_days,
    shifts,
    staff,
    shift_days,
    previous_shifts,
    valid_shift_sequences,
    skill_mix_rules,
    unpleasant_shifts,
)

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
    enforce_completion_of_shift_segments,
    configure_objective,
)

log = logging.getLogger("roster")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)5s: %(message)s"
)


def main():
    """Run main program."""
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
    valid_shift_sequence_permutations = get_valid_shift_sequence_permutations(
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
        valid_shift_sequence_permutations,
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
    enforce_completion_of_shift_segments(
        valid_shift_sequences,
        days_in_partial_sequence,
        previous_shifts,
        shift_vars,
        model,
        staff,
        shift_days,
        shifts,
    )
    max_unpleasant_shifts = configure_objective(
        model, shift_vars, staff, unpleasant_shifts, num_days, shift_days,
    )
    log.info("Starting solver....")
    solver = solve(model)
    display_shifts_by_staff(
        num_days,
        shifts,
        shift_days,
        staff,
        shift_vars,
        solver,
        max_unpleasant_shifts,
    )


main()
