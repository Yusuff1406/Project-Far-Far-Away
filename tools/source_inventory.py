"""Explicit publication allowlist; generated data is never a source archive input."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES={"README.md","LICENSE","LICENSE_STATUS.md","CONTRIBUTING.md","requirements.txt","requirements-audit.txt",".gitignore",".gitattributes"}
DOCS={"BUILD.md","AUDIT.md","audit_summary.json"}
def source_files(root=ROOT):
    for p in sorted(root.rglob("*")):
        if not p.is_file():continue
        rel=p.relative_to(root);parts=rel.parts
        if any(x in {"build","__pycache__",".git",".venv",".cxx",".gradle"} for x in parts):continue
        if len(parts)==1 and p.name in ROOT_FILES:yield p;continue
        if parts[0]=="docs" and len(parts)==2 and p.name in DOCS:yield p;continue
        if parts[0]==".github" and p.suffix in {".yml",".md"}:yield p;continue
        if parts[0]=="native" and p.suffix in {".cpp",".h",".inc",".sh"}:yield p;continue
        if parts[0]=="tools" and (p.suffix in {".py",".sh"} or p.name=="assets_expected.json"):yield p;continue
        if parts[0]=="tests" and p.suffix in {".py",".cpp",".h",".java",".fixture"}:yield p;continue
        if parts[0]=="android" and "assets" not in parts and (p.suffix in {".java",".cpp",".h",".xml",".gradle",".properties"} or p.name=="CMakeLists.txt"):yield p
