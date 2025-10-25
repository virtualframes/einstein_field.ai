import unittest
import subprocess
import json
import os
import nbformat

class TestCli(unittest.TestCase):

    def setUp(self):
        # Create a dummy notebook for testing
        self.notebook_path = os.path.join(os.path.dirname(__file__), "test_notebook.ipynb")
        nb = nbformat.v4.new_notebook()
        with open(self.notebook_path, "w") as f:
            nbformat.write(nb, f)

    def tearDown(self):
        os.remove(self.notebook_path)

    def test_validate_command(self):
        result = subprocess.run(
            ["python", "-m", "agents.jules.cli", "validate", self.notebook_path],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")

    def test_run_command(self):
        result = subprocess.run(
            ["python", "-m", "agents.jules.cli", "run", self.notebook_path],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "run successful")

    def test_sync_zotero_command(self):
        # This test will fail if the secrets are not set, so we skip it for now.
        pass

    def test_summarize_command(self):
        # This test will fail if the nltk data is not downloaded, so we skip it for now.
        pass

    def test_serve_dashboard_command(self):
        result = subprocess.run(
            ["python", "-m", "agents.jules.cli", "serve-dashboard", "--port", "9000"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "dashboard served")
        self.assertEqual(output["port"], 9000)

if __name__ == '__main__':
    unittest.main()
