"""
Common command-line argument interfaces.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from logging import getLogger
from pathlib import Path as _Path
from shutil import which
from subprocess import run
from sys import executable
from typing import Any as _Any

# third-party
from rcmpy.watch import watch
from rcmpy.watch.params import WatchParams
from vcorelib.dict import MergeStrategy, merge_dicts
from vcorelib.io import ARBITER, DEFAULT_INCLUDES_KEY

# internal
from yambs import DESCRIPTION, PKG_NAME, VERSION
from yambs.config.common import DEFAULT_CONFIG

LOG = getLogger(__name__)


def log_package() -> None:
    """Log some basic package information."""
    LOG.info("%s-%s - %s", PKG_NAME, VERSION, DESCRIPTION)


def add_config_arg(parser: _ArgumentParser) -> None:
    """Add an argument for specifying a configuration file."""

    parser.add_argument(
        "-c",
        "--config",
        type=_Path,
        default=DEFAULT_CONFIG,
        help=(
            "the path to the top-level configuration "
            "file (default: '%(default)s')"
        ),
    )


def add_common_args(parser: _ArgumentParser) -> None:
    """Add common command-line arguments to a parser."""

    add_config_arg(parser)
    parser.add_argument(
        "-i",
        "--single-pass",
        action="store_true",
        help="only run a single watch iteration",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="whether or not to continue watching for source tree changes",
    )
    parser.add_argument(
        "-s",
        "--sources",
        action="store_true",
        help="whether or not to only re-generate source manifests",
    )
    parser.add_argument(
        "-n",
        "--no-build",
        action="store_true",
        help="whether or not to skip running 'ninja'",
    )


def run_watch(args: _Namespace, src_root: _Path, command: str) -> int:
    """Run the 'watch' command from rcmpy."""

    return (
        watch(
            WatchParams(
                args.dir,
                src_root,
                [
                    executable,
                    "-m",
                    PKG_NAME,
                    "-C",
                    str(args.dir),
                    command,
                    "-s",
                    "-c",
                    str(args.config),
                ],
                False,  # Don't check file contents.
                single_pass=args.single_pass,
            )
        )
        if args.watch
        else 0
    )


def handle_build(args: _Namespace) -> None:
    """Run 'ninja' if some conditions are met."""

    if not args.no_build and which("ninja"):
        run(["ninja"], check=False)


def merge_strat(args: _Namespace) -> MergeStrategy:
    """Get a merge strategy from parsed arguments."""

    strat = MergeStrategy.RECURSIVE
    if args.update:
        strat = MergeStrategy.UPDATE
    return strat


def load_data(args: _Namespace) -> tuple[dict[str, _Any], list[_Path]]:
    """Load data files based on parsed arguments."""

    files_loaded: list[_Path] = []

    strat = merge_strat(args)

    return (
        merge_dicts(
            [
                ARBITER.decode(
                    file,
                    require_success=True,
                    includes_key=args.includes_key,
                    expect_overwrite=args.expect_overwrite,
                    strategy=strat,
                    files_loaded=files_loaded,
                ).data
                for file in args.inputs
            ],
            expect_overwrite=args.expect_overwrite,
            strategy=strat,
        ),
        files_loaded,
    )


def add_config_load_args(parser: _ArgumentParser) -> None:
    """Add command-line arguments related to loading data files."""

    parser.add_argument(
        "-i",
        "--includes-key",
        default=DEFAULT_INCLUDES_KEY,
        help="top-level key to use for included files (default: %(default)s)",
    )

    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help=(
            "whether or not to use the 'update' merge strategy "
            "(instead of 'recursive')"
        ),
    )

    parser.add_argument(
        "-e",
        "--expect-overwrite",
        action="store_true",
        help="allow configuration files to overwrite data when loaded",
    )

    parser.add_argument("output", type=_Path, help="file to write")
    parser.add_argument("inputs", nargs="+", type=_Path, help="files to read")
