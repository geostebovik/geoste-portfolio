"""Run provenance -- the record of what a measurement was measured against.

EXTRACTED FROM m7_orchestrator.py 2026-09-11. Nothing here is new; `_git()`
and the core of `run_provenance()` are moved verbatim, and
`m7_orchestrator.run_provenance()` still exists with its original signature
and produces a byte-identical dict. The extraction was forced by
probe_fixture_stability.py, which needs provenance and must NOT import
m7_orchestrator to get it, for two reasons:

  1. `m7_orchestrator` imports `m7_evaluator_tool`, which calls
     `build_judge_config()` at module level -- so the import makes Azure
     round-trips. An audit-side probe that never uses a judge would then
     fail to start whenever the judge config is broken. A probe should not
     depend on a service it does not call.
  2. `m7_orchestrator.run_provenance()` records `judge_deployment`
     unconditionally. The fixture probe has no judge. A results file
     asserting a deployment that never ran is the same confidently-wrong
     record that `include_agent` was added to prevent -- see that
     parameter's note in m7_orchestrator.py.

THIS MODULE IMPORTS STDLIB ONLY, and that is a constraint, not an accident.
It is the one piece every probe needs and the one piece that must never be
the reason a probe cannot start.

WHAT BELONGS HERE vs IN THE CALLER. Here: facts true of any run in this repo
-- when it ran, which script, which commit, whether the tree was dirty.
There: anything describing a configuration the caller alone knows it used --
an agent, a judge, a deployment, a prompt. `extra` is the seam. The rule that
produces the split is the one `include_agent` already encodes: a provenance
record may omit a field, but must never assert one that did not apply.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def _git(*args: str) -> str:
    """Read-only git from the script's directory; empty string on any failure.

    Provenance is worth recording and never worth failing a run over, so every
    error path here returns "" rather than raising. --no-optional-locks matches
    the standing rule for reading git out of a non-interactive shell.
    """
    try:
        done = subprocess.run(
            ["git", "--no-optional-locks", *args],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        return done.stdout.strip() if done.returncode == 0 else ""
    except Exception:
        return ""


def core_provenance(script: str | None = None, extra: dict | None = None) -> dict:
    """The repo-level facts about a run, plus whatever the caller adds.

    `git_dirty` is the field that earns this function. A number measured
    against an undocumented working-tree diff is not attributable to any commit
    and cannot be re-derived later -- the failure that poisoned the 2026-08-31
    data point.

    `script` -- this function lives in provenance.py, so `Path(__file__).name`
    here would evaluate to "provenance.py" for every caller, which is the exact
    bug the `script` parameter was added to m7_orchestrator.py to fix on
    2026-09-09. Callers pass their own name. It stays optional, and stays
    wrong-by-default in the same way, only so that the m7_orchestrator wrapper
    keeps its original signature; every new caller should pass it.

    `extra` -- caller-specific configuration fields, merged last so they appear
    after the repo-level ones in the recorded dict. Pass only what actually
    applied to the run.
    """
    # `git status --porcelain` reports STAT differences, not content ones, and
    # _git() hard-codes --no-optional-locks so a refreshed index is never
    # persisted -- which means a file whose mtime moved without its bytes
    # changing is reported dirty on every run, forever. That fired 2026-09-08:
    # q_a_pairs_sample.txt was byte-identical to HEAD by every check that reads
    # bytes, and still flagged the run dirty. A warning that cries wolf is worse
    # than none, so dirtiness is now measured by content.
    # --full-name ADDED 2026-09-11, and it is a correctness fix, not a tidy-up.
    # `git diff --name-only` reports paths from the REPO ROOT; `git ls-files
    # --others` reports them from the CWD, which is SCRIPT_DIR. So before this,
    # git_dirty_files mixed two path conventions in one list, and nobody saw it
    # because the field had never yet held an untracked file. The first run
    # after provenance.py was created printed exactly that:
    #     ['ai-103/scripts/m7_cv_audit_tool.py', ..., 'provenance.py']
    # -- three repo-relative paths and one cwd-relative one, for four files
    # sitting in the same directory. A provenance field whose paths cannot be
    # resolved against a single root is not evidence of anything.
    tracked = _git("diff", "--name-only", "HEAD")
    untracked = _git("ls-files", "--others", "--exclude-standard", "--full-name")
    status = "\n".join(x for x in (tracked, untracked) if x)
    provenance = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "script": script or Path(__file__).name,
        "git_head": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(status),
        "git_dirty_files": status.splitlines(),
    }
    if extra:
        provenance.update(extra)
    return provenance
