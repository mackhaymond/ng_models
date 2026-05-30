from pathlib import Path

def find_repo_root(start: Path | None = None) -> Path:
    """Find the repository root by walking upward until pyproject.toml or data/ is found."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists() or (candidate / "data").exists():
            return candidate
    raise FileNotFoundError("Could not find repo root containing pyproject.toml or data/")

def data_dir(start: Path | None = None) -> Path:
    return find_repo_root(start) / "data"

def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
