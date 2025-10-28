import sys
from pathlib import Path
import pytest

# Add the agents directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent / 'agents' / 'jules'))

from jules import run_sympy_check

def test_run_sympy_check_success():
    claim = {
        "fixtures": [
            {
                "Phiconst": 1e70,
                "V6": 1e60,
                "rhoinfl": 1e-30,
                "ti": 1e-36,
                "tf": 1e-34,
            }
        ]
    }
    result = run_sympy_check(claim)
    assert result["ok"] is True

def test_run_sympy_check_failure():
    claim = {
        "fixtures": [
            {
                "Phiconst": 1e-10,  # This value should cause the check to fail
                "V6": 1e60,
                "rhoinfl": 1e-30,
                "ti": 1e-36,
                "tf": 1e-34,
            }
        ]
    }
    result = run_sympy_check(claim)
    assert result["ok"] is False
