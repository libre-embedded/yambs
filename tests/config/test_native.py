"""
Test the 'config.native' module.
"""

# internal
from tests.resources import resource

# module under test
from yambs.config.common import DEFAULT_CONFIG
from yambs.config.native import load_native


def test_native_config_basic():
    """Test basic interactions with a native configuration."""

    config = load_native(
        path=resource("scenarios", "native").joinpath(DEFAULT_CONFIG)
    )

    assert config.project.repo == "yambs"
    assert config.project.owner == "libre-embedded"
