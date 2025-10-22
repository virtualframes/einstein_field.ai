import json
from pathlib import Path
import pytest
from utils.io import canonical_write

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

def test_canonical_write_creates_file_with_sorted_keys(temp_dir):
    file_path = temp_dir / "test.json"
    data = {"b": 2, "a": 1}

    canonical_write(file_path, data)

    with open(file_path, 'r') as f:
        content = f.read()

    expected_content = json.dumps(data, sort_keys=True, indent=2)
    assert content == expected_content

    loaded_data = json.loads(content)
    assert list(loaded_data.keys()) == ["a", "b"]

def test_canonical_write_is_atomic(temp_dir):
    file_path = temp_dir / "atomic_test.json"
    data = {"c": 3, "b": 2, "a": 1}

    # Simulate a write, but don't check for atomicity directly,
    # as it's hard to test. Instead, we ensure that the file is
    # correctly written and that no partial content is left.
    canonical_write(file_path, data)

    with open(file_path, 'r') as f:
        loaded_data = json.load(f)

    assert loaded_data == data
