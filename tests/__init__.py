import logging

logging.disable(logging.CRITICAL)
from . import (test_battle, test_battle_mechanics, test_battle_modifiers, test_damage_calculator,
               test_decide,test_helpers, test_initialize_battler, test_instruction_generator,
               test_items, test_move_special_effects, test_parse_smogon_stats, test_select_best_move,
               test_state, test_state_mutator, test_team_converter, test_team_datasets)