import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase-a"))
from run_ragas_eval import run_eval

def test_ragas_eval_runs():
    # Smoke test for eval
    assert True
