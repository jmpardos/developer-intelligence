from unittest.mock import patch

import pytest
import requests


def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Developer Intelligence" in response.get_data(as_text=True)
    assert response.mimetype == "text/html"


def test_unknown_route(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


def test_homepage_contains_repository_form(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'action="/repositories"' in response.data
    assert b'name="owner"' in response.data
    assert b'name="repo"' in response.data


def test_analyze_repository(client):
    repository_data = {
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
    }
    
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200
        assert b"pallets/flask" in response.data
        assert b"Python" in response.data
        assert b"Stars: 100" in response.data
        assert b"Forks: 20" in response.data
        assert b"Open Issues: 5" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "pallets",
            "flask"
        )


def test_analyze_repository_not_found(client):
    mock_response = requests.Response()
    mock_response.status_code = 404

    http_error = requests.exceptions.HTTPError(
        "404 Client Error: Not Found",
        response=mock_response,
    )

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.side_effect = http_error

        response = client.post("/repositories", data={"owner": "unknown", "repo": "repository"})
        
        assert response.status_code == 404
        assert b"Repository not found" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "unknown",
            "repository"
        )


def test_analyze_repository_forbidden(client):
    mock_response = requests.Response()
    mock_response.status_code = 403

    http_error = requests.exceptions.HTTPError(
        "403 Client Error: Forbidden",
        response=mock_response,
    )

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.side_effect = http_error

        response = client.post("/repositories", data={"owner": "unknown", "repo": "repository"})
        
        assert response.status_code == 502
        assert b"Unable to access GitHub repository" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "unknown",
            "repository"
        )


def test_analyze_repository_timeout(client):
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.side_effect = requests.exceptions.Timeout("Connection timed out")

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})
        
        assert response.status_code == 504
        assert b"GitHub is taking too long to respond" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "pallets",
            "flask"
        )


@pytest.mark.parametrize(
    "owner, repo",
    [
        ("", "flask"),
        ("pallets", ""),
        ("", ""),
        ("   ", "flask"),
        ("pallets", "   "),
    ],
)
def test_analyze_repository_invalid_parameters(client, owner, repo):
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        response = client.post(
            "/repositories",
            data={"owner": owner, "repo": repo},
        )
        assert response.status_code == 400
        assert b"Owner and repository are required" in response.data

        mock_service.assert_not_called()


@pytest.mark.parametrize(
    "form_data",
    [
        {"owner": "pallets"},
        {"repo": "flask"},
        {},
    ],
)
def test_analyze_repository_missing_parameters(client, form_data):
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        response = client.post(
            "/repositories",
            data=form_data,
        )
        assert response.status_code == 400
        assert b"Owner and repository are required" in response.data

        mock_service.assert_not_called()


def test_analyze_repository_connection_error(client):
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.side_effect = requests.exceptions.ConnectionError("Connection refused")

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})
        
        assert response.status_code == 502
        assert b"Unable to connect to GitHub" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "pallets",
            "flask"
        )


def test_analyze_repository_github_server_error(client):
    mock_response = requests.Response()
    mock_response.status_code = 500

    http_error = requests.exceptions.HTTPError(
        "500 Client Error: Internal Server Error",
        response=mock_response,
    )

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.side_effect = http_error

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})
        
        assert response.status_code == 502
        assert b"GitHub returned an unexpected error" in response.data

        mock_service.return_value.get_repository.assert_called_once_with(
            "pallets",
            "flask"
        )
