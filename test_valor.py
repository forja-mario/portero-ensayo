import ast
import unittest
from pathlib import Path


class TestValor(unittest.TestCase):
    def test_valor_aceptado(self):
        # El archivo del cambio se lee como dato: no se ejecuta al comprobarlo.
        code = ast.parse(Path("valor.py").read_text())
        self.assertEqual(len(code.body), 1)
        assign = code.body[0]
        self.assertIsInstance(assign, ast.Assign)
        self.assertEqual(len(assign.targets), 1)
        self.assertIsInstance(assign.targets[0], ast.Name)
        self.assertEqual(assign.targets[0].id, "VALOR")
        self.assertIsInstance(assign.value, ast.Constant)
        self.assertEqual(assign.value.value, 1)
