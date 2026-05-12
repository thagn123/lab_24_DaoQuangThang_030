import pytest
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase-b"))
from judge_pipeline import pairwise_judge

@pytest.mark.asyncio
async def test_pairwise_judge_mock():
    res = await pairwise_judge("Q", "A", "B")
    assert "winner" in res
