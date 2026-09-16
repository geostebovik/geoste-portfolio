"""
Fail loudly if a results file the docs or code cite is not in git.

ADDED 2026-09-16 (Claude wrote it). Offline, stdlib only, read-only git.

WHY. `.gitignore` excludes `ai-103/scripts/results/*` and allow-lists the
files that are evidence, one line each. That allow-list is kept up by memory,
and memory has failed on schedule: it lapsed after Sep 7 and again after
Sep 10, which left the Sep 11 certification pass itself out of the public
repo, and on Sep 16 a new results file was cited before it was listed. A
citation to a file no reader can open is a citation to nothing. This turns
the reminder into a check.

WHAT IT DOES. Finds every `YYYYMMDD-HHMMSS_<name>.json|.txt` named in the
current docs (STATUS.md, m7-orientation.md, m7-writeup-draft.md) and in
ai-103/scripts/*.py, then reports each one that is not in the git index:
  - UNTRACKED: the file exists. It prints the allow-list line to add (only if
    .gitignore is what hides it) and the `git add` to run.
  - MISSING: cited, but not on disk and not in git.
Staged files count as tracked, so the check passes as soon as the `git add`
is done and can be run again before the commit.

WHAT IT DOES NOT DO. It does not scan STATUS-archive-phase1.md, whose early
citations predate the allow-list. Pass --all to include it.

Exit code 0 when clean, 1 when anything is reported: part of the
end-of-session checklist in m7-orientation.md.

Usage (from anywhere inside the repo):
    python check_cited_results_tracked.py [--all]
"""

import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CITATION = re.compile(r"\b(\d{8}-\d{6}_[A-Za-z0-9_]+\.(?:json|txt))\b")
DOCS = ["ai-103/STATUS.md", "ai-103/m7-orientation.md",
        "ai-103/m7-writeup-draft.md"]
ARCHIVE = ["ai-103/STATUS-archive-phase1.md"]
RESULTS = "ai-103/scripts/results/"


def git(*args: str, cwd: Path = SCRIPT_DIR) -> subprocess.CompletedProcess:
    # Read-only, and --no-optional-locks: this may run through a shell that
    # cannot delete a stranded index.lock (Sep 15 and Sep 16). Every call after
    # the first runs from the repo root, because git reads pathspecs relative
    # to the working directory and RESULTS is written from the root.
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=cwd,
                          capture_output=True, text=True,
                          env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})


def main() -> int:
    root = Path(git("rev-parse", "--show-toplevel").stdout.strip())
    if not root.is_dir():
        print("not inside a git repository")
        return 1
    tracked = set(git("ls-files", "--", RESULTS, cwd=root).stdout.splitlines())

    sources = DOCS + (ARCHIVE if "--all" in sys.argv[1:] else [])
    sources += sorted(p.relative_to(root).as_posix()
                      for p in (root / "ai-103/scripts").glob("*.py")
                      if p.name != Path(__file__).name)

    cited: dict[str, list[str]] = {}
    for rel in sources:
        path = root / rel
        if not path.is_file():
            continue
        for name in CITATION.findall(path.read_text(encoding="utf-8", errors="replace")):
            cited.setdefault(RESULTS + name, []).append(rel)

    problems = 0
    for results_path in sorted(cited):
        if results_path in tracked:
            continue
        problems += 1
        where = ", ".join(sorted(set(cited[results_path])))
        if (root / results_path).is_file():
            print(f"UNTRACKED  {results_path}\n  cited in: {where}")
            if git("check-ignore", "-q", "--", results_path, cwd=root).returncode == 0:
                print(f"  add to .gitignore:  !{results_path}")
            print(f"  then:               git add {results_path}")
        else:
            print(f"MISSING    {results_path}\n  cited in: {where}\n"
                  f"  not on disk and not in git -- fix the citation or find the file")

    print(f"\n{len(cited)} cited results file(s), {problems} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
