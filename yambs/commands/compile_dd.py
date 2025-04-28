"""
An entry-point for the 'compile_dd' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.paths import Pathlike, rel

# internal
from yambs.commands.common import add_config_load_args, load_data, log_package


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


def write_dyndeps(
    suffix: str, path: Path, deps: list[Path], base: Pathlike = None
) -> bool:
    """
    Write dynamic dependencies file for ninja.

    https://ninja-build.org/manual.html#ref_dyndep
    """

    with IndentedFileWriter.string() as writer:
        writer.write("ninja_dyndep_version = 1")
        imp_ins = " ".join([str(rel(x, base=base)) for x in deps])

        line = f"build {rel(path.with_suffix(suffix), base=base)}: dyndep"

        if imp_ins:
            line += " | " + imp_ins
        writer.write(line)

        return write_if_necessary(
            path,
            writer.stream.getvalue(),  # type: ignore
        )


def compile_dd_cmd(args: _Namespace) -> int:
    """Execute the compile_dd command."""

    log_package()

    _, files_loaded = load_data(args)

    # Write dynamic-dependencies file.
    write_dyndeps(f".{args.suffix}", args.output, files_loaded, base=args.dir)

    return 0


def add_compile_dd_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add compile_dd-command arguments to its parser."""

    add_config_load_args(parser)

    parser.add_argument(
        "-s",
        "--suffix",
        default="json",
        help="suffix for compiled-output file",
    )

    return compile_dd_cmd
