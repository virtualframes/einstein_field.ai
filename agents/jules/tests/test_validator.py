import unittest
import os
import json
import nbformat
from agents.jules.validator import validate_notebook, extract_citations

class TestValidator(unittest.TestCase):

    def setUp(self):
        # Create a dummy notebook for testing
        self.notebook_path = "test_notebook.ipynb"
        nb = nbformat.v4.new_notebook()
        nb['cells'] = [nbformat.v4.new_code_cell('print("hello world")')]
        with open(self.notebook_path, 'w') as f:
            nbformat.write(nb, f)

        # Create a dummy baseline file
        self.baseline_path = "baseline.json"
        with open(self.baseline_path, 'w') as f:
            json.dump({"expected_outputs_hash": "different_hash"}, f)

    def tearDown(self):
        os.remove(self.notebook_path)
        os.remove(self.baseline_path)
        # Clean up any provenance files created
        for f in os.listdir(".provenance"):
            if f.endswith(".json"):
                os.remove(f".provenance/{f}")

    def test_validate_notebook_success(self):
        result = validate_notebook(self.notebook_path)
        self.assertEqual(result['status'], 'success')

    def test_validate_notebook_failure(self):
        result = validate_notebook(self.notebook_path, baseline_path=self.baseline_path)
        self.assertEqual(result['status'], 'failure')
        self.assertIn("outputs_hash mismatch", result['failures'])

    def test_extract_citations(self):
        # This is a placeholder test
        citations = extract_citations(self.notebook_path)
        self.assertEqual(citations, [])

if __name__ == '__main__':
    unittest.main()
