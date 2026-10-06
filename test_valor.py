import unittest

from valor import VALOR


class TestValor(unittest.TestCase):
    def test_valor_aceptado(self):
        self.assertEqual(VALOR, 1)
