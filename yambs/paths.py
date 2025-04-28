"""
A module implementing some file-system path utilities.
"""

# built-in
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Any, Iterator, TextIO

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import ARBITER
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


@contextmanager
def write_if_different(path: Path) -> Iterator[TextIO]:
    """
    Writes the contents of a string stream if it differs from output path
    data.
    """

    with StringIO() as stream:
        try:
            yield stream
        finally:
            do_write = False

            content = stream.getvalue()

            if path.is_file():
                with path.open("r", encoding=DEFAULT_ENCODING) as path_fd:
                    do_write = content != path_fd.read()
            else:
                do_write = True

            if do_write:
                with path.open("w", encoding=DEFAULT_ENCODING) as path_fd:
                    path_fd.write(content)


def encode_if_different(output: Path, data: dict[str, Any], **kwargs) -> bool:
    """Encode a data file if its contents are different."""

    if (
        output.is_file()
        and data == ARBITER.decode(output, require_success=True, **kwargs).data
    ):
        return True

    return ARBITER.encode(output, data)[0]
