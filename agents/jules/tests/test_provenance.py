import unittest
import os
import json
from agents.jules.provenance import record_execution, load_provenance

class TestProvenance(unittest.TestCase):

    def test_record_and_load_provenance(self):
        target = "test_target"
        actor = "test_actor"
        inputs = {"input1": "value1"}
        outputs = {"output1": "value1"}
        metadata = {"meta1": "value1"}

        provenance_id = record_execution(target, actor, inputs, outputs, metadata)

        # Check that the provenance file was created
        provenance_file = f".provenance/{provenance_id}.json"
        self.assertTrue(os.path.exists(provenance_file))

        # Check that the loaded provenance data matches the original data
        loaded_provenance = load_provenance(provenance_id)
        self.assertEqual(loaded_provenance["target"], target)
        self.assertEqual(loaded_provenance["actor"], actor)
        self.assertEqual(loaded_provenance["inputs"], inputs)
        self.assertEqual(loaded_provenance["outputs"], outputs)
        self.assertEqual(loaded_provenance["metadata"], metadata)

        # Clean up the created file
        os.remove(provenance_file)

if __name__ == '__main__':
    unittest.main()
