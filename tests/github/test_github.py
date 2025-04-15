"""
Test the 'github' module.
"""

# internal
from tests.resources import OWNER, REPO

# module under test
from yambs.github import github_url, release_data, repo_release_api_url


def test_github_url_basic():
    """Test URL encoding."""

    assert github_url().geturl() == "https://github.com"
    assert github_url(netloc_prefix="api").geturl() == "https://api.github.com"
    assert (
        repo_release_api_url(OWNER, REPO) == "https://api.github.com/repos/"
        "libre-embedded/yambs-sample/releases/latest"
    )
    assert release_data(OWNER, REPO)
