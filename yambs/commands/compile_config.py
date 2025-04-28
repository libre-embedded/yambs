"""
An entry-point for the 'compile_config' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.io import ARBITER
from vcorelib.paths import Pathlike, rel

# internal
from yambs.commands.common import (
    add_config_load_args,
    load_data,
    log_package,
    merge_strat,
)


def write_if_necessary(output: Path, data: str) -> bool:
    """Write output if contents are changed."""

    write_contents = False

    if output.is_file():
        with output.open("r", encoding=DEFAULT_ENCODING) as path_fd:
            write_contents = path_fd.read() != data
    else:
        write_contents = True

    if write_contents:
        with output.open("w", encoding=DEFAULT_ENCODING) as path_fd:
            path_fd.write(data)

    return write_contents


def write_dyndeps(path: Path, deps: list[Path], base: Pathlike = None) -> bool:
    """
    Write dynamic dependencies file for ninja.

    https://ninja-build.org/manual.html#ref_dyndep
    """

    return write_if_necessary(
        path.with_suffix(path.suffix + ".d"),
        f"{rel(path, base=base)}: "
        + " ".join([str(rel(x, base=base)) for x in deps]),
    )


def compile_config_cmd(args: _Namespace) -> int:
    """Execute the compile_config command."""

    log_package()

    data, files_loaded = load_data(args)

    # Write dynamic-dependencies file.
    write_dyndeps(
        args.output,
        [x for x in files_loaded if x not in args.inputs],
        base=args.dir,
    )

    # Return early without doing anything if data already matches.
    if args.output.is_file():
        if (
            data
            == ARBITER.decode(
                args.output,
                require_success=True,
                includes_key=args.includes_key,
                expect_overwrite=args.expect_overwrite,
                strategy=merge_strat(args),
            ).data
        ):
            return 0

    return 0 if ARBITER.encode(args.output, data)[0] else 1


def add_compile_config_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add compile_config-command arguments to its parser."""

    add_config_load_args(parser)

    return compile_config_cmd
