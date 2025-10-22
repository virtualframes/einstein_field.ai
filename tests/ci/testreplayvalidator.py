from cirecoveryengine.validate_trace import validate_replay
from pathlib import Path

def test_validate_replay_fixture(tmp_path):
    p = tmp_path / "pc.json"
    p.write_text('{"planner_checkpoint_id":"pc:v1","seed":1,"dependency_manifest_hash":null,"timestamp":1}')
    assert validate_replay(str(p)) is True
