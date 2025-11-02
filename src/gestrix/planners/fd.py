from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class FastDownwardError(RuntimeError):
    """Raised when Fast Downward cannot be run or fails."""

    pass


def _fd_home() -> Path:
    env = os.getenv("FASTDOWNWARD_HOME")
    if not env:
        raise FastDownwardError(
            "FASTDOWNWARD_HOME is not set. Run scripts/setup_fastdownward.sh or set the env var."
        )
    home = Path(env).expanduser().resolve()
    if not (home / "fast-downward.py").exists():
        raise FastDownwardError(f"fast-downward.py not found under {home}")
    return home


def run_fd(
    domain_pddl: Path,
    problem_pddl: Path,
    timeout_sec: int = 60,
    search: Optional[str] = None,
) -> Tuple[Path, str]:
    """
    Run Fast Downward on given domain/problem.
    Returns: (plan_path, plan_text)
    Raises: FastDownwardError on failure/timeout.
    """
    domain_pddl = Path(domain_pddl).resolve()
    problem_pddl = Path(problem_pddl).resolve()
    if not domain_pddl.exists() or not problem_pddl.exists():
        raise FastDownwardError("Domain or problem PDDL does not exist.")

    fd = _fd_home() / "fast-downward.py"
    search = search or "astar(blind())"

    with tempfile.TemporaryDirectory(prefix="gestrix-fd-") as tmpdir:
        tmp = Path(tmpdir)
        plan_out = tmp / "sas_plan"

        cmd = [
            "python",
            str(fd),
            f"--plan-file={plan_out}",
            str(domain_pddl),
            str(problem_pddl),
            "--search",
            search,
        ]

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise FastDownwardError(f"FD subprocess timeout ({timeout_sec}s)") from e

        if proc.returncode != 0 or not plan_out.exists():
            msg = (
                f"FD failed (code={proc.returncode}). out:\n"
                f"{proc.stdout[-500:]}\nerr:\n{proc.stderr[-500:]}"
            )
            raise FastDownwardError(msg)

        plan_text = plan_out.read_text(encoding="utf-8", errors="ignore")

        # keep a copy outside the temp dir
        keep_dir = Path(tempfile.mkdtemp(prefix="gestrix-fd-plan-"))
        final_plan = keep_dir / "sas_plan"
        shutil.copy(plan_out, final_plan)

        return final_plan, plan_text
