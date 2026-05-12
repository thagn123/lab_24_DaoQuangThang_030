import pytest
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase-c"))
from input_guard import InputGuard
from topic_guard import TopicGuard

@pytest.mark.asyncio
async def test_pii_guard():
    guard = InputGuard()
    res = await guard.check_pii("My phone is 0912345678")
    assert res.is_safe == False
    
@pytest.mark.asyncio
async def test_topic_guard():
    guard = TopicGuard()
    res = await guard.check_topic("What is algorithmic trading?")
    assert res.is_safe == True
