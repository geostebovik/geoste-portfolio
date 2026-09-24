"""
build_package.py -- assemble the Function's deployment package.

Written by Claude, 2026-09-24. Run from anywhere:  python build_package.py

WHY A BUILD STEP AT ALL. The Function's code lives in two places in the repo:
function/ holds the adapter, and scripts/ holds the certified M7 modules. The
tools find the fact sheet as `<their folder>/../iip-docs/...`. So this copies
exactly the files the Function needs into function/.build/, in the SAME
relative layout as the repo, which means that path resolves with no change to
any certified module:

  .build/function_app.py, upload_handler.py, host.json, requirements.txt
  .build/scripts/<the M7 import chain>
  .build/iip-docs/m7-riverside-hardware/fact-sheet.md

It then zips .build/ CONTENTS (not the folder) to function/iip-function.zip,
which Microsoft's packaging rules require: host.json at the zip root. Deploy
with REMOTE build -- never install packages on Windows (python-build-options).

The module list is EXPLICIT on purpose. A glob would quietly ship probes and
testers, and would quietly miss a newly added dependency. Instead, the import
check at the end fails loudly if the list is incomplete.
"""

import ast
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AI103 = HERE.parent
BUILD = HERE / ".build"
ZIP_BASE = HERE / "iip-function"          # make_archive appends .zip

FUNCTION_FILES = ["function_app.py", "upload_handler.py", "host.json", "requirements.txt"]
SCRIPT_MODULES = [
    "m7_orchestrator.py", "m7_cv_audit_tool.py", "m7_evaluator_tool.py",
    "m7_fact_sheet_tool.py", "m7_legibility_check.py", "m7_vision_test.py",
    "m3_analyze.py", "provenance.py",
]
DATA_FILES = ["iip-docs/m7-riverside-hardware/fact-sheet.md"]


def local_imports_closed() -> list[str]:
    """Every bare-name import of a scripts/ module must itself be packaged.

    Parses (does not execute) each packaged module. It catches a missing
    sibling module at build time, rather than as a ModuleNotFoundError at the
    Function's first cold start.
    """
    available = {Path(m).stem for m in SCRIPT_MODULES}
    on_disk = {p.stem for p in (AI103 / "scripts").glob("*.py")}
    missing = []
    for name in SCRIPT_MODULES:
        tree = ast.parse((AI103 / "scripts" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                mods = [node.module.split(".")[0]]
            for m in mods:
                if m in on_disk and m not in available:
                    missing.append(f"{name} imports {m}.py, which is not packaged")
    return missing


def main() -> int:
    missing = local_imports_closed()
    if missing:
        print("BUILD REFUSED -- incomplete module list:")
        for line in missing:
            print(f"  {line}")
        return 1

    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "scripts").mkdir(parents=True)
    for name in FUNCTION_FILES:
        shutil.copy2(HERE / name, BUILD / name)
    for name in SCRIPT_MODULES:
        shutil.copy2(AI103 / "scripts" / name, BUILD / "scripts" / name)
    for rel in DATA_FILES:
        dest = BUILD / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(AI103 / rel, dest)

    archive = shutil.make_archive(str(ZIP_BASE), "zip", root_dir=BUILD)
    files = sorted(p.relative_to(BUILD).as_posix() for p in BUILD.rglob("*") if p.is_file())
    print(f"packaged {len(files)} files into {archive}:")
    for f in files:
        print(f"  {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
