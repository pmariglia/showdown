import unittest

import constants
from showdown.engine.objects import State
from showdown.battle import Pokemon as StatePokemon
from showdown.engine.objects import Pokemon


class TestPokemonInit(unittest.TestCase):

    def test_state_serialization_and_loading_results_in_the_same_state(self):
        state_json = {
          'self': {
            'active': {
              'id': 'tornadustherian',
              'level': 100,
              'hp': 0,
              'maxhp': 0,
              'ability': 'regenerator',
              'item': 'fightiniumz',
              'baseStats': {
                'hp': 79,
                'attack': 100,
                'defense': 80,
                'special-attack': 110,
                'special-defense': 90,
                'speed': 121
              },
              'attack': 212,
              'defense': 197,
              'special-attack': 319,
              'special-defense': 216,
              'speed': 375,
              'attack_boost': -1,
              'defense_boost': 0,
              'special_attack_boost': 0,
              'special_defense_boost': 0,
              'speed_boost': 0,
              'accuracy_boost': 1,
              'evasion_boost': 1,
              'status': None,
              'volatileStatus': [

              ],
              'moves': [
                {
                  'id': 'taunt',
                  'disabled': False,
                  'current_pp': 32
                },
                {
                  'id': 'hurricane',
                  'disabled': False,
                  'current_pp': 16
                },
                {
                  'id': 'focusblast',
                  'disabled': False,
                  'current_pp': 8
                },
                {
                  'id': 'defog',
                  'disabled': False,
                  'current_pp': 24
                }
              ],
              'types': [
                'flying'
              ],
              'canMegaEvo': False
            },
            'reserve': {
              'greninja': {
                'id': 'greninja',
                'level': 100,
                'hp': 285,
                'maxhp': 285,
                'ability': 'battlebond',
                'item': 'choicespecs',
                'baseStats': {
                  'hp': 72,
                  'attack': 95,
                  'defense': 67,
                  'special-attack': 103,
                  'special-defense': 71,
                  'speed': 122
                },
                'attack': 203,
                'defense': 171,
                'special-attack': 305,
                'special-defense': 178,
                'speed': 377,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'surf',
                    'disabled': False,
                    'current_pp': 24
                  },
                  {
                    'id': 'darkpulse',
                    'disabled': False,
                    'current_pp': 24
                  },
                  {
                    'id': 'icebeam',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'watershuriken',
                    'disabled': False,
                    'current_pp': 32
                  }
                ],
                'types': [
                  'water',
                  'dark'
                ],
                'canMegaEvo': False
              },
              'mawile': {
                'id': 'mawile',
                'level': 100,
                'hp': 261.0,
                'maxhp': 261,
                'ability': 'intimidate',
                'item': 'mawilite',
                'baseStats': {
                  'hp': 50,
                  'attack': 85,
                  'defense': 85,
                  'special-attack': 55,
                  'special-defense': 55,
                  'speed': 50
                },
                'attack': 295,
                'defense': 206,
                'special-attack': 131,
                'special-defense': 146,
                'speed': 180,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'suckerpunch',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'playrough',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'thunderpunch',
                    'disabled': False,
                    'current_pp': 24
                  },
                  {
                    'id': 'firefang',
                    'disabled': False,
                    'current_pp': 24
                  }
                ],
                'types': [
                  'steel',
                  'fairy'
                ],
                'canMegaEvo': False
              },
              'ferrothorn': {
                'id': 'ferrothorn',
                'level': 100,
                'hp': 352.0,
                'maxhp': 352,
                'ability': 'ironbarbs',
                'item': 'leftovers',
                'baseStats': {
                  'hp': 74,
                  'attack': 94,
                  'defense': 131,
                  'special-attack': 54,
                  'special-defense': 116,
                  'speed': 20
                },
                'attack': 224,
                'defense': 299,
                'special-attack': 144,
                'special-defense': 364,
                'speed': 68,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'spikes',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'leechseed',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'knockoff',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'gyroball',
                    'disabled': False,
                    'current_pp': 8
                  }
                ],
                'types': [
                  'grass',
                  'steel'
                ],
                'canMegaEvo': False
              },
              'heatran': {
                'id': 'heatran',
                'level': 100,
                'hp': 385,
                'maxhp': 385,
                'ability': 'flashfire',
                'item': 'leftovers',
                'baseStats': {
                  'hp': 91,
                  'attack': 90,
                  'defense': 106,
                  'special-attack': 130,
                  'special-defense': 106,
                  'speed': 77
                },
                'attack': 194,
                'defense': 248,
                'special-attack': 296,
                'special-defense': 332,
                'speed': 201,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'taunt',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'magmastorm',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'earthpower',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'toxic',
                    'disabled': False,
                    'current_pp': 16
                  }
                ],
                'types': [
                  'fire',
                  'steel'
                ],
                'canMegaEvo': False
              },
              'garchomp': {
                'id': 'garchomp',
                'level': 100,
                'hp': 379,
                'maxhp': 379,
                'ability': 'roughskin',
                'item': 'rockyhelmet',
                'baseStats': {
                  'hp': 108,
                  'attack': 130,
                  'defense': 95,
                  'special-attack': 80,
                  'special-defense': 85,
                  'speed': 102
                },
                'attack': 296,
                'defense': 317,
                'special-attack': 176,
                'special-defense': 206,
                'speed': 282,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'stealthrock',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'earthquake',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'toxic',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'roar',
                    'disabled': False,
                    'current_pp': 32
                  }
                ],
                'types': [
                  'dragon',
                  'ground'
                ],
                'canMegaEvo': False
              }
            },
            'side_conditions': {
              'toxic_count': 0,
              'tailwind': 0,
              'stealthrock': 0,
              'spikes': 0,
              'stickyweb': 0,
              'toxicspikes': 0,
              'reflect': 0,
              'lightscreen': 0,
              'auroraveil': 0
            }
          },
          'opponent': {
            'active': {
              'id': 'landorustherian',
              'level': 100,
              'hp': 319.0,
              'maxhp': 319,
              'ability': 'intimidate',
              'item': 'choicescarf',
              'baseStats': {
                'hp': 89,
                'attack': 145,
                'defense': 90,
                'special-attack': 105,
                'special-defense': 80,
                'speed': 91
              },
              'attack': 389,
              'defense': 216,
              'special-attack': 223.63636363636363,
              'special-defense': 197,
              'speed': 309.1,
              'attack_boost': 0,
              'defense_boost': 0,
              'special_attack_boost': 0,
              'special_defense_boost': 0,
              'speed_boost': 0,
              'accuracy_boost': 1,
              'evasion_boost': 1,
              'status': None,
              'volatileStatus': [

              ],
              'moves': [
                {
                  'id': 'earthquake',
                  'disabled': False,
                  'current_pp': 16
                },
                {
                  'id': 'uturn',
                  'disabled': False,
                  'current_pp': 32
                },
                {
                  'id': 'stealthrock',
                  'disabled': False,
                  'current_pp': 32
                },
                {
                  'id': 'defog',
                  'disabled': False,
                  'current_pp': 24
                },
                {
                  'id': 'stoneedge',
                  'disabled': False,
                  'current_pp': 8
                }
              ],
              'types': [
                'ground',
                'flying'
              ],
              'canMegaEvo': False
            },
            'reserve': {
              'ferrothorn': {
                'id': 'ferrothorn',
                'level': 100,
                'hp': 352.0,
                'maxhp': 352,
                'ability': 'ironbarbs',
                'item': 'leftovers',
                'baseStats': {
                  'hp': 74,
                  'attack': 94,
                  'defense': 131,
                  'special-attack': 54,
                  'special-defense': 116,
                  'speed': 20
                },
                'attack': 224,
                'defense': 304,
                'special-attack': 158.4,
                'special-defense': 326,
                'speed': 69.09090909090908,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'leechseed',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'gyroball',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'stealthrock',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'powerwhip',
                    'disabled': False,
                    'current_pp': 16
                  }
                ],
                'types': [
                  'grass',
                  'steel'
                ],
                'canMegaEvo': False
              },
              'rotomwash': {
                'id': 'rotomwash',
                'level': 100,
                'hp': 304.0,
                'maxhp': 304,
                'ability': 'levitate',
                'item': 'leftovers',
                'baseStats': {
                  'hp': 50,
                  'attack': 65,
                  'defense': 107,
                  'special-attack': 105,
                  'special-defense': 107,
                  'speed': 86
                },
                'attack': 150.9090909090909,
                'defense': 330.0,
                'special-attack': 246,
                'special-defense': 250,
                'speed': 222,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'hydropump',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'voltswitch',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'willowisp',
                    'disabled': False,
                    'current_pp': 24
                  },
                  {
                    'id': 'defog',
                    'disabled': False,
                    'current_pp': 24
                  }
                ],
                'types': [
                  'electric',
                  'water'
                ],
                'canMegaEvo': False
              },
              'mawile': {
                'id': 'mawile',
                'level': 100,
                'hp': 303.0,
                'maxhp': 303,
                'ability': 'intimidate',
                'item': 'leftovers',
                'baseStats': {
                  'hp': 50,
                  'attack': 85,
                  'defense': 85,
                  'special-attack': 55,
                  'special-defense': 55,
                  'speed': 50
                },
                'attack': 295.90000000000003,
                'defense': 206,
                'special-attack': 132.72727272727272,
                'special-defense': 148,
                'speed': 136,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'playrough',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'ironhead',
                    'disabled': False,
                    'current_pp': 24
                  },
                  {
                    'id': 'suckerpunch',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'swordsdance',
                    'disabled': False,
                    'current_pp': 32
                  }
                ],
                'types': [
                  'steel',
                  'fairy'
                ],
                'canMegaEvo': False
              },
              'greninja': {
                'id': 'greninja',
                'level': 100,
                'hp': 285.0,
                'maxhp': 285,
                'ability': 'protean',
                'item': 'choicescarf',
                'baseStats': {
                  'hp': 72,
                  'attack': 95,
                  'defense': 67,
                  'special-attack': 103,
                  'special-defense': 71,
                  'speed': 122
                },
                'attack': 205.45454545454544,
                'defense': 170,
                'special-attack': 305,
                'special-defense': 179,
                'speed': 377.3,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'icebeam',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'gunkshot',
                    'disabled': False,
                    'current_pp': 8
                  },
                  {
                    'id': 'uturn',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'hydropump',
                    'disabled': False,
                    'current_pp': 8
                  }
                ],
                'types': [
                  'water',
                  'dark'
                ],
                'canMegaEvo': False
              },
              'scolipede': {
                'id': 'scolipede',
                'level': 100,
                'hp': 261.0,
                'maxhp': 261,
                'ability': 'speedboost',
                'item': 'wateriumz',
                'baseStats': {
                  'hp': 60,
                  'attack': 100,
                  'defense': 89,
                  'special-attack': 55,
                  'special-defense': 69,
                  'speed': 112
                },
                'attack': 328.90000000000003,
                'defense': 214,
                'special-attack': 132.72727272727272,
                'special-defense': 175,
                'speed': 323,
                'attack_boost': 0,
                'defense_boost': 0,
                'special_attack_boost': 0,
                'special_defense_boost': 0,
                'speed_boost': 0,
                'accuracy_boost': 1,
                'evasion_boost': 1,
                'status': None,
                'volatileStatus': [

                ],
                'moves': [
                  {
                    'id': 'swordsdance',
                    'disabled': False,
                    'current_pp': 32
                  },
                  {
                    'id': 'earthquake',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'megahorn',
                    'disabled': False,
                    'current_pp': 16
                  },
                  {
                    'id': 'poisonjab',
                    'disabled': False,
                    'current_pp': 32
                  }
                ],
                'types': [
                  'bug',
                  'poison'
                ],
                'canMegaEvo': False
              }
            },
            'side_conditions': {
              'toxic_count': 0,
              'tailwind': 0,
              'reflect': 0,
              'lightscreen': 0,
              'auroraveil': 0,
              'stealthrock': 0,
              'spikes': 0,
              'stickyweb': 0,
              'toxicspikes': 0
            }
          },
          'weather': 1,
          'field': 2,
          'trickroom': 3
        }

        state = State.from_dict(state_json)

        # str(state) gives a string representing the state-dict
        new_state_dict = eval(str(state))

        self.assertEqual(state_json, new_state_dict)

    def test_pokemon_init_gives_correct_number_of_physical_moves(self):
        # 2 moves that are physical
        moves = [
          {constants.ID: 'flamethrower'},
          {constants.ID: 'flareblitz'},
          {constants.ID: 'flamewheel'},
          {constants.ID: 'reflect'},
        ]

        state_pkmn_dict = StatePokemon('charizardmegax', 100).to_dict()
        state_pkmn_dict[constants.MOVES] = moves
        pkmn = Pokemon.from_state_pokemon_dict(state_pkmn_dict)

        self.assertEqual(2, pkmn.burn_multiplier)
