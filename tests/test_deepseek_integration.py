import unittest
import os
import vcr
from agents.jules.clients import deepseek_client

class TestDeepSeekIntegration(unittest.TestCase):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/deepseek_summarize.yaml')
    def test_summarize(self):
        # The API key needs to be present for vcrpy to record, but it can be a dummy value for playback.
        os.environ["DEEPSEEK_API_KEY"] = "dummy_key"
        result = deepseek_client.summarize("This is a test.", 10)
        self.assertEqual(result["status"], "error")
