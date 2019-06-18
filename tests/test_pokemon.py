import unittest

from showdown.state.pokemon import Pokemon


class TestPokemonInit(unittest.TestCase):

    def test_alternate_pokemon_name_initializes(self):
        name = 'florgeswhite'
        Pokemon(name, 100)
