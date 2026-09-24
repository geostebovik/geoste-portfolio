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


def git_snapshot() -> dict:
    """The repo's git state right now: head, branch, and dirtiness by CONTENT.

    SPLIT OUT OF core_provenance() 2026-09-16, unchanged in what it reads, so a
    probe can take the snapshot when its run STARTS. Python has already loaded
    the code by then, so the start snapshot is the one that describes what
    ran. core_provenance() had only ever read git when the record was
    assembled -- after the loop, for the fixture probe -- which attributed any
    mid-run save or commit to the run.
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
    # ":/" ADDED 2026-09-15. `ls-files --others` lists only files under the
    # CWD, which is SCRIPT_DIR -- so an untracked file anywhere else in the
    # repo was invisible, and the Sep 15 orchestrator pass recorded
    # git_dirty=false while ai-103/m7-writeup-draft.md sat untracked. The
    # top-level pathspec makes the listing repo-wide; --full-name already
    # made the paths repo-relative. `git diff --name-only HEAD` was
    # repo-wide all along, so only untracked files were affected.
    untracked = _git("ls-files", "--others", "--exclude-standard", "--full-name",
                     "--", ":/")
    status = "\n".join(x for x in (tracked, untracked) if x)
    # NO GIT IS NOT A CLEAN TREE (2026-09-24, Claude; found in the first M11
    # Function result). _git() returns "" on any failure, so where git does
    # not exist -- inside the Azure Function -- every call came back empty and
    # this function reported git_dirty: False. That asserted a clean tree it
    # had no way to see: the confidently-wrong record this project keeps a
    # standing lesson about. An empty HEAD now means UNKNOWN, recorded as None
    # with the reason. Where git works (every laptop run), rev-parse HEAD is
    # never empty, so those records are byte-for-byte unchanged.
    head = _git("rev-parse", "HEAD")
    if not head:
        return {
            "git_head": None,
            "git_branch": None,
            "git_dirty": None,
            "git_dirty_files": None,
            "git_unavailable": ("git returned nothing for rev-parse HEAD: no git "
                                "here, or not a repository. Tree state UNKNOWN, "
                                "not clean."),
        }
    return {
        "git_head": head,
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(status),
        "git_dirty_files": status.splitlines(),
    }


def end_check(git_at_start: dict) -> dict:
    """Compare the repo now against the start snapshot. ADDED 2026-09-16.

    Some inputs are read DURING a run, not at import -- the fixture images and
    the fact sheet among them -- so a change made mid-run can reach the model
    even though the code was loaded at start. A start snapshot alone cannot
    see that; an end snapshot alone misattributes it. Recording both is the
    only version that says what happened.

    Returns `git_changed_during_run`, plus the full end snapshot under
    `git_at_end` only when something differs, so a clean run's record stays
    short. Branch is not compared: a checkout mid-run would already move the
    head or the dirty set, and a branch rename alone changes nothing that ran.
    """
    end = git_snapshot()
    changed = any(git_at_start.get(k) != end[k]
                  for k in ("git_head", "git_dirty", "git_dirty_files"))
    out = {"git_changed_during_run": changed}
    if changed:
        out["git_at_end"] = end
    return out


def core_provenance(script: str | None = None, extra: dict | None = None,
                    started_at: datetime | None = None,
                    git_at_start: dict | None = None) -> dict:
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

    `started_at` ADDED 2026-09-14, and it closes a gap nobody noticed until
    someone tried to size a run. `timestamp` is built HERE, at the moment the
    record is assembled -- which for every existing caller is after the work
    finished, immediately before the JSON is written. So every results file in
    scripts/results/ records when it was WRITTEN and nothing about how long it
    took, and `filename_timestamp - timestamp` computes to under a second on
    every one of them. The only wall-clock figure anywhere in this project is
    the "~95 minutes" in m7-orientation.md's Backlog, carried in prose from
    memory.

    Duration is a repo-level fact about a run -- the same class as when it ran
    and which commit it ran against -- so it belongs here rather than in each
    caller's `extra`, where the field names would drift.

    `timestamp` IS DELIBERATELY UNCHANGED. Its meaning stays "when this record
    was assembled", and callers that pass nothing get a byte-identical dict to
    the one they got before this parameter existed -- which is what keeps
    m7_orchestrator.run_provenance()'s frozen output frozen. The new fields are
    OMITTED, not null, when `started_at` is absent: a run whose start was never
    recorded must not assert an elapsed time, by the same rule `include_agent`
    encodes.

    `git_at_start` ADDED 2026-09-16 -- a git_snapshot() taken when the run
    began. Pass it and the recorded git fields describe the START of the run,
    with `git_changed_during_run` (and `git_at_end` when true) added from
    end_check(). Omit it and nothing changes. Found because the fixture probe
    assembled its record after the loop, so a save made during a 57-minute
    run would have marked that run dirty and a commit would have changed its
    recorded head.
    """
    # WHEN THE GIT FIELDS ARE READ -- ADDED 2026-09-16. With `git_at_start`
    # absent, they are read here, when the record is assembled, and the dict
    # is byte-identical to what it was before this parameter existed (that is
    # what keeps m7_orchestrator.run_provenance()'s frozen output frozen).
    # With it present, the recorded git fields are the START snapshot and an
    # end-of-run comparison is added -- see end_check().
    git = git_at_start if git_at_start is not None else git_snapshot()
    provenance = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "script": script or Path(__file__).name,
        "git_head": git["git_head"],
        "git_branch": git["git_branch"],
        "git_dirty": git["git_dirty"],
        "git_dirty_files": git["git_dirty_files"],
    }
    if "git_unavailable" in git:
        # Carried through so a None above is never read without its reason.
        # Absent whenever git works, so laptop records keep their exact shape.
        provenance["git_unavailable"] = git["git_unavailable"]
    if git_at_start is not None:
        provenance.update(end_check(git_at_start))
    if started_at is not None:
        # A naive datetime is accepted and assumed local rather than rejected:
        # this function's standing rule is that provenance is never worth
        # failing a run over, and datetime.now() without .astimezone() is the
        # easy mistake for a caller to make.
        started = started_at if started_at.tzinfo else started_at.astimezone()
        finished = datetime.now().astimezone()
        provenance["started_at"] = started.isoformat(timespec="seconds")
        provenance["elapsed_seconds"] = round(
            (finished - started).total_seconds(), 1)

    if extra:
        provenance.update(extra)
    return provenance


def deployment_builds(account: str, resource_group: str, deployments) -> dict:
    """Which MODEL BUILD each deployment was serving, at run time.

    ADDED 2026-09-22, after a gap this module had from the start.

    THE GAP. Every results file recorded `judge_deployment: "gpt-5-4"` -- a
    DEPLOYMENT NAME. The model build behind that name was recorded nowhere. So
    when item7's groundedness moved on 2026-09-22 (2.0 twice, where the Sep 9
    judge-isolation probe had recorded 4.0 x10 with "no variance"), the record
    could not answer the first question anyone would ask: *was this the same
    judge?* Four results files were checked -- 20260910, 20260911, 20260915,
    20260922 -- and not one contained a version string.

    WHY THAT IS THE ONE FIELD THAT MATTERS HERE. This module is meticulous
    about everything a human must change to change: the commit, the dirty
    tree, the elapsed time. A model build is the opposite -- it can move with
    no commit, no what-if diff, and nobody's decision, because the deployment
    carries `versionUpgradeOption: OnceNewDefaultVersionAvailable` (hardcoded
    in infrastructure/iip/modules/foundry.bicep). Provenance that captures
    only the human-controlled variables is blind precisely where it is needed.

    It was answered for the Sep 2026 window by the Azure Activity Log -- no
    `accounts/deployments` write between Sep 7 and Sep 21, so no upgrade fired
    -- but that is an argument reconstructed after the fact, from a record
    with 90-day retention. This makes it a fact in the file instead.

    `versionUpgradeOption` is captured too, deliberately: it says whether the
    version in this record is PINNED or merely CURRENT, which is the
    difference between "this run is reproducible" and "this run was a
    snapshot".

    Never raises. Provenance is not worth failing a run over -- the standing
    rule in this module -- so an az failure records the error instead of
    propagating it. A record saying `{"error": ...}` is honest; a crashed
    90-minute run is not.
    """
    import json as _json
    import shutil as _shutil
    import subprocess as _subprocess

    names = sorted(set(d for d in deployments if d))
    az = _shutil.which("az")
    if az is None:
        # One entry PER DEPLOYMENT, the same shape as the success path.
        # Fixed 2026-09-23: this returned a bare {"error": ...}, which the
        # caller in probe_orchestrator_stability.py iterates as {name: build}.
        # It read "error" as a deployment name and called .get() on a string,
        # crashing the run this function promises never to crash.
        return {name: {"error": "az not found on PATH"} for name in names}

    builds = {}
    for name in names:
        try:
            out = _subprocess.run(
                [az, "cognitiveservices", "account", "deployment", "show",
                 "--name", account, "--resource-group", resource_group,
                 "--deployment-name", name,
                 "--query", "{model:properties.model.name,"
                            " version:properties.model.version,"
                            " upgradePolicy:properties.versionUpgradeOption,"
                            " capacity:sku.capacity}",
                 "-o", "json"],
                capture_output=True, text=True, timeout=60,
            )
            builds[name] = (_json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip()
                            else {"error": (out.stderr or "empty response").strip()[:200]})
        except Exception as exc:  # noqa: BLE001 -- see docstring
            builds[name] = {"error": f"{type(exc).__name__}: {exc}"[:200]}
    return builds
