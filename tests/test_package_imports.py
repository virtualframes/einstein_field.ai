import unittest
import importlib

class TestPackageImports(unittest.TestCase):

    def test_imports(self):
        mod = importlib.import_module("agents.jules.validator")
        self.assertTrue(hasattr(mod, "validate_notebook"))
