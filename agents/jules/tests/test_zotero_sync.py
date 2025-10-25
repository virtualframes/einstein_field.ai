import unittest
from unittest.mock import patch
from agents.jules.zotero_sync import sync, diff
import json
import os

class TestZoteroSync(unittest.TestCase):

    def setUp(self):
        # Create dummy snapshot files
        self.snapshot_a_path = "snapshot_a.json"
        self.snapshot_b_path = "snapshot_b.json"
        with open(self.snapshot_a_path, "w") as f:
            json.dump([{"id": 1, "data": "a"}], f)
        with open(self.snapshot_b_path, "w") as f:
            json.dump([{"id": 1, "data": "b"}], f)

    def tearDown(self):
        os.remove(self.snapshot_a_path)
        os.remove(self.snapshot_b_path)

    @patch('pyzotero.zotero.Zotero')
    def test_sync(self, mock_zotero):
        # Configure the mock to return a specific value
        mock_zotero.return_value.collection_items.return_value = [{"id": 1, "data": "a"}]

        # Call the function
        result = sync("test_api_key", "test_user_id", ["test_collection"])

        # Assert the result
        self.assertEqual(result['item_count'], 1)

    def test_diff(self):
        result = diff(self.snapshot_a_path, self.snapshot_b_path)
        self.assertEqual(result, {"added": [], "removed": [], "changed": []})

if __name__ == '__main__':
    unittest.main()
