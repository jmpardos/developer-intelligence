from unittest.mock import MagicMock

import pytest
import requests

from developer_intelligence.services.github import GitHubService


def test_get_repository():

    github_response = {
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
    }

    mock_response = MagicMock()
    mock_response.json.return_value = github_response

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    
    github_service = GitHubService(session=mock_session)

    result = github_service.get_repository("pallets", "flask")

    mock_response.raise_for_status.assert_called_once()

    assert result == {
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
    }

    mock_session.get.assert_called_once_with(
        "https://api.github.com/repos/pallets/flask",
        timeout=10,
    )


def test_get_repository_not_found():

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found")

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    
    github_service = GitHubService(session=mock_session)

    with pytest.raises(requests.exceptions.HTTPError):
        github_service.get_repository("unknown", "repository")

    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_not_called()


def test_get_repository_forbidden():
    
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Client Error: Forbidden")

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    
    github_service = GitHubService(session=mock_session)

    with pytest.raises(requests.exceptions.HTTPError):
        github_service.get_repository("pallets", "flask")

    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_not_called()


def test_get_repository_timeout():
    
    mock_session = MagicMock()
    mock_session.get.side_effect = requests.exceptions.Timeout("Connection timed out")
    
    github_service = GitHubService(session=mock_session)

    with pytest.raises(requests.exceptions.Timeout):
        github_service.get_repository("pallets", "flask")

    mock_session.get.assert_called_once_with(
        "https://api.github.com/repos/pallets/flask",
        timeout=10,
    )


def test_get_repository_empty_owner():

    mock_session = MagicMock()
    
    github_service = GitHubService(session=mock_session)

    with pytest.raises(ValueError):
        github_service.get_repository("", "flask")

    mock_session.get.assert_not_called()


def test_get_repository_empty_repo():

    mock_session = MagicMock()
    
    github_service = GitHubService(session=mock_session)

    with pytest.raises(ValueError):
        github_service.get_repository("pallets", "")

    mock_session.get.assert_not_called()