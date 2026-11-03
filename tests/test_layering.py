"""Enforces the one-way dependency rule between layers.

api -> application -> domain, and infrastructure -> domain.
The composition root in src/api is the only place allowed to see both sides.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module)
    return modules


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def test_domain_depends_on_nothing_else():
    offenders = {}
    for path in _python_files(SRC / "domain"):
        bad = {
            module
            for module in _imported_modules(path)
            if module.startswith(("src.application", "src.infrastructure", "src.api"))
        }
        if bad:
            offenders[str(path.relative_to(SRC))] = sorted(bad)
    assert offenders == {}, f"domain must not import other layers: {offenders}"


def test_application_does_not_import_infrastructure():
    """Services depend on ports, not adapters.

    LLM prompt text and response contracts are the documented exception: they
    are data definitions the application composes but does not perform I/O with.
    """
    allowed_prefixes = (
        "src.infrastructure.llm.prompts",
        "src.infrastructure.llm.contracts",
        "src.infrastructure.config.logging",
    )
    offenders = {}
    for path in _python_files(SRC / "application"):
        bad = {
            module
            for module in _imported_modules(path)
            if module.startswith("src.infrastructure")
            and not module.startswith(allowed_prefixes)
        }
        if bad:
            offenders[str(path.relative_to(SRC))] = sorted(bad)
    assert offenders == {}, f"application must reach infrastructure via ports: {offenders}"


def test_infrastructure_does_not_import_application():
    offenders = {}
    for path in _python_files(SRC / "infrastructure"):
        bad = {
            module
            for module in _imported_modules(path)
            if module.startswith(("src.application", "src.api"))
        }
        if bad:
            offenders[str(path.relative_to(SRC))] = sorted(bad)
    assert offenders == {}, (
        "infrastructure must satisfy ports structurally, never import them: "
        f"{offenders}"
    )


def test_only_composition_root_imports_wiring():
    importers = [
        str(path.relative_to(SRC))
        for path in _python_files(SRC)
        if "src.infrastructure.wiring" in _imported_modules(path)
    ]
    assert importers == ["api/main.py"], (
        f"only the composition root may import wiring, found: {importers}"
    )
