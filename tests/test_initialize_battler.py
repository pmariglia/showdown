import unittest
from showdown.battle import Battler
from showdown.battle import Pokemon


class TestInitializeBattler(unittest.TestCase):
    def setUp(self):
        self.battler = Battler()

    def test_initialize_with_z_move_available(self):
        request_dict = {
          "active": [
            {
              "moves": [
                {
                  "move": "Swords Dance",
                  "id": "swordsdance",
                  "pp": 32,
                  "maxpp": 32,
                  "target": "self",
                  "disabled": False
                },
                {
                  "move": "Photon Geyser",
                  "id": "photongeyser",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                },
                {
                  "move": "Earthquake",
                  "id": "earthquake",
                  "pp": 16,
                  "maxpp": 16,
                  "target": "allAdjacent",
                  "disabled": False
                },
                {
                  "move": "Stone Edge",
                  "id": "stoneedge",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                }
              ],
              "canZMove": [
                None,
                {
                  "move": "Light That Burns the Sky",
                  "target": "normal"
                },
                None,
                None
              ]
            }
          ],
          "side": {
            "name": "BigBluePikachu",
            "id": "p2",
            "pokemon": [
              {
                "ident": "p2: Necrozma",
                "details": "Necrozma-Ultra",
                "condition": "152/335",
                "active": True,
                "stats": {
                  "atk": 433,
                  "def": 238,
                  "spa": 333,
                  "spd": 230,
                  "spe": 385
                },
                "moves": [
                  "swordsdance",
                  "photongeyser",
                  "earthquake",
                  "stoneedge"
                ],
                "baseAbility": "neuroforce",
                "item": "ultranecroziumz",
                "pokeball": "pokeball",
                "ability": "neuroforce"
              },
              {
                "ident": "p2: Groudon",
                "details": "Groudon",
                "condition": "386/386",
                "active": False,
                "stats": {
                  "atk": 336,
                  "def": 284,
                  "spa": 328,
                  "spd": 216,
                  "spe": 235
                },
                "moves": [
                  "overheat",
                  "stealthrock",
                  "precipiceblades",
                  "toxic"
                ],
                "baseAbility": "drought",
                "item": "redorb",
                "pokeball": "pokeball",
                "ability": "drought"
              },
              {
                "ident": "p2: Xerneas",
                "details": "Xerneas",
                "condition": "393/393",
                "active": False,
                "stats": {
                  "atk": 268,
                  "def": 226,
                  "spa": 397,
                  "spd": 233,
                  "spe": 297
                },
                "moves": [
                  "moonblast",
                  "focusblast",
                  "aromatherapy",
                  "thunder"
                ],
                "baseAbility": "fairyaura",
                "item": "choicescarf",
                "pokeball": "pokeball",
                "ability": "fairyaura"
              },
              {
                "ident": "p2: Darkrai",
                "details": "Darkrai",
                "condition": "281/281",
                "active": False,
                "stats": {
                  "atk": 194,
                  "def": 217,
                  "spa": 369,
                  "spd": 216,
                  "spe": 383
                },
                "moves": [
                  "nastyplot",
                  "darkpulse",
                  "hypnosis",
                  "thunder"
                ],
                "baseAbility": "baddreams",
                "item": "lifeorb",
                "pokeball": "pokeball",
                "ability": "baddreams"
              },
              {
                "ident": "p2: Arceus",
                "details": "Arceus-Dragon",
                "condition": "444/444",
                "active": False,
                "stats": {
                  "atk": 248,
                  "def": 292,
                  "spa": 276,
                  "spd": 276,
                  "spe": 356
                },
                "moves": [
                  "judgment",
                  "fireblast",
                  "defog",
                  "recover"
                ],
                "baseAbility": "multitype",
                "item": "dracoplate",
                "pokeball": "pokeball",
                "ability": "multitype"
              },
              {
                "ident": "p2: Celesteela",
                "details": "Celesteela",
                "condition": "397/397",
                "active": False,
                "stats": {
                  "atk": 238,
                  "def": 335,
                  "spa": 225,
                  "spd": 240,
                  "spe": 158
                },
                "moves": [
                  "leechseed",
                  "heavyslam",
                  "toxic",
                  "flamethrower"
                ],
                "baseAbility": "beastboost",
                "item": "leftovers",
                "pokeball": "pokeball",
                "ability": "beastboost"
              }
            ]
          },
          "rqid": 7
        }

        self.battler.active = Pokemon('pikachu', 100)
        self.battler.from_json(request_dict)
        
        # photongeyser is a z-move with the request dict given above
        photon_geyser = self.battler.active.get_move('photongeyser')

        self.assertTrue(photon_geyser.can_z)

    def test_initialize_with_hidden_power_produces_correct_hidden_power(self):
        request_dict = {
          "active": [
            {
              "moves": [
                {
                  "move": "Swords Dance",
                  "id": "swordsdance",
                  "pp": 32,
                  "maxpp": 32,
                  "target": "self",
                  "disabled": False
                },
                {
                  "move": "Photon Geyser",
                  "id": "photongeyser",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                },
                {
                  "move": "Earthquake",
                  "id": "earthquake",
                  "pp": 16,
                  "maxpp": 16,
                  "target": "allAdjacent",
                  "disabled": False
                },
                {
                  "move": "Hidden Power Fire",
                  "id": "hiddenpower",
                  "pp": 24,
                  "maxpp": 24,
                  "target": "normal",
                  "disabled": False
                },
              ]
            }
          ],
          "side": {
            "name": "BigBluePikachu",
            "id": "p2",
            "pokemon": [
              {
                "ident": "p2: Necrozma",
                "details": "Necrozma",
                "condition": "152/335",
                "active": True,
                "stats": {
                  "atk": 433,
                  "def": 238,
                  "spa": 333,
                  "spd": 230,
                  "spe": 385
                },
                "moves": [
                  "swordsdance",
                  "photongeyser",
                  "earthquake",
                  "stoneedge"
                ],
                "baseAbility": "neuroforce",
                "item": "ultranecroziumz",
                "pokeball": "pokeball",
                "ability": "neuroforce"
              },
              {
                "ident": "p2: Groudon",
                "details": "Groudon",
                "condition": "386/386",
                "active": False,
                "stats": {
                  "atk": 336,
                  "def": 284,
                  "spa": 328,
                  "spd": 216,
                  "spe": 235
                },
                "moves": [
                  "overheat",
                  "stealthrock",
                  "precipiceblades",
                  "toxic"
                ],
                "baseAbility": "drought",
                "item": "redorb",
                "pokeball": "pokeball",
                "ability": "drought"
              },
              {
                "ident": "p2: Xerneas",
                "details": "Xerneas",
                "condition": "393/393",
                "active": False,
                "stats": {
                  "atk": 268,
                  "def": 226,
                  "spa": 397,
                  "spd": 233,
                  "spe": 297
                },
                "moves": [
                  "moonblast",
                  "focusblast",
                  "aromatherapy",
                  "thunder"
                ],
                "baseAbility": "fairyaura",
                "item": "choicescarf",
                "pokeball": "pokeball",
                "ability": "fairyaura"
              },
              {
                "ident": "p2: Darkrai",
                "details": "Darkrai",
                "condition": "281/281",
                "active": False,
                "stats": {
                  "atk": 194,
                  "def": 217,
                  "spa": 369,
                  "spd": 216,
                  "spe": 383
                },
                "moves": [
                  "nastyplot",
                  "darkpulse",
                  "hypnosis",
                  "thunder"
                ],
                "baseAbility": "baddreams",
                "item": "lifeorb",
                "pokeball": "pokeball",
                "ability": "baddreams"
              },
              {
                "ident": "p2: Arceus",
                "details": "Arceus-Dragon",
                "condition": "444/444",
                "active": False,
                "stats": {
                  "atk": 248,
                  "def": 292,
                  "spa": 276,
                  "spd": 276,
                  "spe": 356
                },
                "moves": [
                  "judgment",
                  "fireblast",
                  "defog",
                  "recover"
                ],
                "baseAbility": "multitype",
                "item": "dracoplate",
                "pokeball": "pokeball",
                "ability": "multitype"
              },
              {
                "ident": "p2: Celesteela",
                "details": "Celesteela",
                "condition": "397/397",
                "active": False,
                "stats": {
                  "atk": 238,
                  "def": 335,
                  "spa": 225,
                  "spd": 240,
                  "spe": 158
                },
                "moves": [
                  "leechseed",
                  "heavyslam",
                  "toxic",
                  "flamethrower"
                ],
                "baseAbility": "beastboost",
                "item": "leftovers",
                "pokeball": "pokeball",
                "ability": "beastboost"
              }
            ]
          },
          "rqid": 7
        }

        self.battler.active = Pokemon('pikachu', 100)
        self.battler.from_json(request_dict)

        hiddenpowerfire = self.battler.active.get_move('hiddenpowerfire60')

        self.assertTrue(hiddenpowerfire)

    def test_initialize_pokemon_with_no_item(self):
        request_dict = {
          "active": [
            {
              "moves": [
                {
                  "move": "Swords Dance",
                  "id": "swordsdance",
                  "pp": 32,
                  "maxpp": 32,
                  "target": "self",
                  "disabled": False
                },
                {
                  "move": "Photon Geyser",
                  "id": "photongeyser",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                },
                {
                  "move": "Earthquake",
                  "id": "earthquake",
                  "pp": 16,
                  "maxpp": 16,
                  "target": "allAdjacent",
                  "disabled": False
                },
                {
                  "move": "Hidden Power Fire",
                  "id": "hiddenpower",
                  "pp": 24,
                  "maxpp": 24,
                  "target": "normal",
                  "disabled": False
                },
              ]
            }
          ],
          "side": {
            "name": "BigBluePikachu",
            "id": "p2",
            "pokemon": [
              {
                "ident": "p2: Necrozma",
                "details": "Necrozma",
                "condition": "152/335",
                "active": True,
                "stats": {
                  "atk": 433,
                  "def": 238,
                  "spa": 333,
                  "spd": 230,
                  "spe": 385
                },
                "moves": [
                  "swordsdance",
                  "photongeyser",
                  "earthquake",
                  "stoneedge"
                ],
                "baseAbility": "neuroforce",
                "item": "ultranecroziumz",
                "pokeball": "pokeball",
                "ability": "neuroforce"
              },
              {
                "ident": "p2: Groudon",
                "details": "Groudon",
                "condition": "386/386",
                "active": False,
                "stats": {
                  "atk": 336,
                  "def": 284,
                  "spa": 328,
                  "spd": 216,
                  "spe": 235
                },
                "moves": [
                  "overheat",
                  "stealthrock",
                  "precipiceblades",
                  "toxic"
                ],
                "baseAbility": "drought",
                "item": "",
                "pokeball": "pokeball",
                "ability": "drought"
              },
              {
                "ident": "p2: Xerneas",
                "details": "Xerneas",
                "condition": "393/393",
                "active": False,
                "stats": {
                  "atk": 268,
                  "def": 226,
                  "spa": 397,
                  "spd": 233,
                  "spe": 297
                },
                "moves": [
                  "moonblast",
                  "focusblast",
                  "aromatherapy",
                  "thunder"
                ],
                "baseAbility": "fairyaura",
                "item": "choicescarf",
                "pokeball": "pokeball",
                "ability": "fairyaura"
              },
              {
                "ident": "p2: Darkrai",
                "details": "Darkrai",
                "condition": "281/281",
                "active": False,
                "stats": {
                  "atk": 194,
                  "def": 217,
                  "spa": 369,
                  "spd": 216,
                  "spe": 383
                },
                "moves": [
                  "nastyplot",
                  "darkpulse",
                  "hypnosis",
                  "thunder"
                ],
                "baseAbility": "baddreams",
                "item": "lifeorb",
                "pokeball": "pokeball",
                "ability": "baddreams"
              },
              {
                "ident": "p2: Arceus",
                "details": "Arceus-Dragon",
                "condition": "444/444",
                "active": False,
                "stats": {
                  "atk": 248,
                  "def": 292,
                  "spa": 276,
                  "spd": 276,
                  "spe": 356
                },
                "moves": [
                  "judgment",
                  "fireblast",
                  "defog",
                  "recover"
                ],
                "baseAbility": "multitype",
                "item": "dracoplate",
                "pokeball": "pokeball",
                "ability": "multitype"
              },
              {
                "ident": "p2: Celesteela",
                "details": "Celesteela",
                "condition": "397/397",
                "active": False,
                "stats": {
                  "atk": 238,
                  "def": 335,
                  "spa": 225,
                  "spd": 240,
                  "spe": 158
                },
                "moves": [
                  "leechseed",
                  "heavyslam",
                  "toxic",
                  "flamethrower"
                ],
                "baseAbility": "beastboost",
                "item": "leftovers",
                "pokeball": "pokeball",
                "ability": "beastboost"
              }
            ]
          },
          "rqid": 7
        }

        self.battler.active = Pokemon('pikachu', 100)
        self.battler.from_json(request_dict)

        groudon = [p for p in self.battler.reserve if p.name == 'groudon'][0]

        self.assertEqual(None, groudon.item)
