import unittest
import subprocess
import json

class TestCli(unittest.TestCase):

    def test_validate_command(self):
        result = subprocess.run(
            ["python", "agents/jules/cli.py", "validate", "test.ipynb"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "validation successful")
        self.assertEqual(output["notebook"], "test.ipynb")

    def test_run_command(self):
        result = subprocess.run(
            ["python", "agents/jules/cli.py", "run", "test.ipynb"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "run successful")
        self.assertEqual(output["notebook"], "test.ipynb")

    def test_sync_zotero_command(self):
        result = subprocess.run(
            ["python", "agents/jules/cli.py", "sync-zotero", "--api-key", "key", "--user", "user", "--collections", "collection"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "zotero sync successful")

    def test_summarize_command(self):
        result = subprocess.run(
            ["python", "agents/jules/cli.py", "summarize", "--docs", "doc1.pdf", "doc2.pdf", "--prompt", "prompt"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "summarization successful")
        self.assertEqual(output["docs"], ["doc1.pdf", "doc2.pdf"])

    def test_serve_dashboard_command(self):
        result = subprocess.run(
            ["python", "agents/jules/cli.py", "serve-dashboard", "--port", "9000"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "dashboard served")
        self.assertEqual(output["port"], 9000)

if __name__ == '__main__':
    unittest.main()
