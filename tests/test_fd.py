import os
from pathlib import Path
import pytest

from gestrix.planners.fd import run_fd

BW_DOMAIN = Path("data/raw/pddl/blocksworld/domain.pddl")
BW_PROBLEM = Path("data/raw/pddl/blocksworld/problem-01.pddl")


@pytest.mark.skipif(
    not os.getenv("FASTDOWNWARD_HOME"),
    reason="FASTDOWNWARD_HOME not set; run scripts/setup_fastdownward.sh first.",
)
def test_fd_blocks_world_plan_smoke(tmp_path: Path):
    assert BW_DOMAIN.exists() and BW_PROBLEM.exists(), "PDDL seeds missing"
    plan_path, plan_text = run_fd(BW_DOMAIN, BW_PROBLEM, timeout_sec=30)
    assert plan_path.exists(), "Plan file not created"
    assert isinstance(plan_text, str) and len(plan_text.strip()) > 0, "Plan text empty"
