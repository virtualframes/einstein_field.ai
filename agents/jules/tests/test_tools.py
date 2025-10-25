import unittest
import vcr
from agents.jules.agents.tools import summarize_documents, verify_citation, contradiction_check, extract_claims
import os

class TestTools(unittest.TestCase):

    def setUp(self):
        # Create a dummy document for testing summarization
        self.doc_path = "test_doc.txt"
        with open(self.doc_path, "w") as f:
            f.write("This is the first sentence. This is the second sentence. This is the third sentence.")

    def tearDown(self):
        os.remove(self.doc_path)

    def test_summarize_documents(self):
        result = summarize_documents("test query", [self.doc_path], {})
        self.assertIn("result", result)
        self.assertIn("grounding", result)
        self.assertIn("provenance_id", result)
        self.assertNotEqual(result["result"]["extractive_summary"], "")

    @vcr.use_cassette('agents/jules/tests/fixtures/vcr_cassettes/verify_citation.yaml')
    def test_verify_citation(self):
        result = verify_citation("10.1126/science.169.3946.635")
        self.assertEqual(result["normalized"], "10.1126/science.169.3946.635")
        self.assertGreater(result["grounding_score"], 0)
        self.assertIsNotNone(result["provenance_id"])

    def test_extract_claims(self):
        result = extract_claims(["doc1.pdf"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["claim"], "This is a claim.")

    def test_contradiction_check(self):
        result = contradiction_check("test claim", ["doc1.pdf"])
        self.assertTrue(result["contradiction"])
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["edges"]), 1)

if __name__ == '__main__':
    unittest.main()
