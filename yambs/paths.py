"""
A module implementing some file-system path utilities.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.paths import Pathlike, normalize

# internal
from yambs.translation import BUILD_DIR_PATH


def resolve_build_dir(build_root: Path, variant: str, path: Path) -> Path:
    """Resolve the build-directory variable in a path."""
    return build_root.joinpath(variant, path.relative_to(BUILD_DIR_PATH))


def combine_if_not_absolute(root: Path, candidate: Pathlike) -> Path:
    """https://github.com/libre-embedded/ifgen/blob/master/ifgen/paths.py"""

    candidate = normalize(candidate)
    return candidate if candidate.is_absolute() else root.joinpath(candidate)
