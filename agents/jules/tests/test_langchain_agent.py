import unittest
from agents.jules.agents.langchain_agent import create_agent

class TestLangchainAgent(unittest.TestCase):

    def test_create_agent_and_run(self):
        agent = create_agent({})
        self.assertIsNotNone(agent)

        # The FakeLLM will "respond" with the action to take, and the agent will execute it.
        result = agent.invoke({"input": "Summarize the document"})

        # We need to extract the actual result from the agent's output.
        # The structure of the output will depend on the agent's implementation.
        # For now, we'll just check that the output contains the keys we expect.
        self.assertIn("result", result["output"])
        self.assertIn("grounding", result["output"])
        self.assertIn("provenance_id", result["output"])

if __name__ == '__main__':
    unittest.main()
