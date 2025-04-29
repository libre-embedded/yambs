"""
Test the 'commands.native' module.
"""

# built-in
from shutil import which
from subprocess import run
from sys import platform

# third-party
from vcorelib.paths.context import in_dir

# internal
from tests.resources import clean_scenario

# module under test
from yambs import PKG_NAME
from yambs.entry import main as yambs_main


def test_native_command_wasm():
    """Test the 'native' command with WASM variants."""

    with in_dir(clean_scenario("native3")):
        assert yambs_main([PKG_NAME, "native"]) == 0

        # Try to build (if we can).
        if platform == "linux" and which("ninja"):
            run(["ninja", "wasm"], check=True)


def test_native_command_basic():
    """Test the 'native' command."""

    path = str(clean_scenario("native"))

    # Ensure the directory dependency is cleaned as well.
    clean_scenario("native2")
    clean_scenario("native3")

    with in_dir(path):
        assert yambs_main([PKG_NAME, "native_manifest"]) == 0
        assert yambs_main([PKG_NAME, "native", "-w", "-i"]) == 0
        assert yambs_main([PKG_NAME, "native"]) == 0

        # Try to build (if we can).
        if platform == "linux" and which("ninja"):
            run(["ninja", "format"], check=True)
            run(["ninja", "all", "format-check"], check=True)
