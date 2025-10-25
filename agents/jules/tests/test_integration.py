import unittest
from agents.jules.validator import validate_notebook

class TestIntegration(unittest.TestCase):

    def test_validate_example_notebook(self):
        result = validate_notebook("notebooks/research/example_reproducible.ipynb")
        self.assertEqual(result["status"], "success")

if __name__ == '__main__':
    unittest.main()
