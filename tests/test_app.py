# AI assistance: ChatGPT was used to discuss test cases,
# mocking strategies, and debugging of test failures.
# Tests were implemented, reviewed, and executed by the author.
import sqlite3
from unittest.mock import patch

import pytest
import requests

from developer_intelligence.app import create_app
from developer_intelligence.persistence.repository import RepositoryRepository


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
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": "2023-01-01T00:00:00+00:00",
        "github_updated_at": "2023-01-01T00:00+00:00",
    }
    
    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200
        assert b"pallets/flask" in response.data
        assert b"Python" in response.data
        assert b"Stars" in response.data
        assert b"100" in response.data
        assert b"Forks" in response.data
        assert b"20" in response.data
        assert b"Open Issues" in response.data
        assert b"5" in response.data

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


def test_app_initializes_database(tmp_path):
    database_path = tmp_path / "test.db"

    create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": database_path,
        }
    )

    assert database_path.exists()

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='repositories';"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "repositories"


def test_analyze_repository_saves_data(client):
    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": "2023-01-01T00:00:00+00:00",
        "github_updated_at": "2023-01-01T00:00+00:00",
    }

    with (
        patch("developer_intelligence.app.GitHubService") as mock_github,
        patch("developer_intelligence.app.RepositoryRepository") as mock_repository,
    ):
        mock_github.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200

        mock_repository.return_value.save.assert_called_once_with(
            repository_data
        )


def test_analyze_repository_persists_data(tmp_path):
    database_path = tmp_path / "test.db"

    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": database_path,
        }
    )

    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": "2023-01-01T00:00:00+00:00",
        "github_updated_at": "2023-01-01T00:00+00:00",
    }

    with patch("developer_intelligence.app.GitHubService") as mock_github:
        mock_github.return_value.get_repository.return_value = repository_data

        with app.test_client() as client:
            response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

            assert response.status_code == 200

            repository_repo = RepositoryRepository(database_path)

            saved_repository = repository_repo.find_by_github_id(12345)

            assert saved_repository is not None
            assert saved_repository["full_name"] == "pallets/flask"


def test_analyze_repository_database_error(client):
    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
    }

    with (
        patch("developer_intelligence.app.GitHubService") as mock_github,
        patch("developer_intelligence.app.RepositoryRepository") as mock_repository,
    ):
        # GitHub responds successfully.
        mock_github.return_value.get_repository.return_value = repository_data

        # SQLite fails while attempting to save.
        mock_repository.return_value.save.side_effect = (
            sqlite3.OperationalError("database is locked")
        )

        # Verify that Flask propagates the exception.
        response = client.post(
            "/repositories",
            data={"owner": "pallets", "repo": "flask"},
        )

        assert response.status_code == 500
        assert b"Unable to save repository data" in response.data

        # Verify that saving the repository was attempted.
        mock_repository.return_value.save.assert_called_once_with(
            repository_data
        )


def test_history_empty(client):
    response = client.get("/history")

    assert response.status_code == 200
    assert b"No repositories found." in response.data


def test_history_displays_repositories(tmp_path):
    database_path = tmp_path / "test.db"

    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": database_path,
    })

    client = app.test_client()

    repository_repo = RepositoryRepository(database_path)

    # 1. Create two dictionaries containing repository data.
    repository_data_1 = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
    }

    repository_data_2 = {
        "github_id": 67890,
        "name": "django",
        "full_name": "django/django",
        "description": "The Web framework for perfectionists with deadlines",
        "language": "Python",
        "stars": 200,
        "forks": 30,
        "open_issues": 10,
    }

    # 2. Save them using repository_repo.save().
    repository_repo.save(repository_data_1)
    repository_repo.save(repository_data_2)

    # 3. Execute GET /history.
    response = client.get("/history")

    # 4. Verify the HTTP 200 response.
    assert response.status_code == 200

    # 5. Verify that both repositories are displayed.
    assert b"pallets/flask" in response.data
    assert b"django/django" in response.data


def test_homepage_has_history_link(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/history"' in response.data


def test_repository_details_without_last_push(client):
    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": None,
        "github_updated_at": "2023-01-01T00:00:00+00:00",
    }

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200            
        assert b"Not available" in response.data


def test_analyze_repository_displays_analytics(client):
    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": "2023-01-01T00:00:00+00:00",
        "github_updated_at": "2023-01-01T00:00+00:00",
    }

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200
        assert b"Repository Analytics" in response.data
        assert b"Repository Age" in response.data
        assert b"Days Since Last Push" in response.data
        assert b"Average Stars per Year" in response.data


def test_analyze_repository_without_last_push(client):
    repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The Python micro framework",
        "language": "Python",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "github_created_at": "2020-01-01T00:00:00+00:00",
        "github_pushed_at": None,
        "github_updated_at": "2023-01-01T00:00:00+00:00",
    }

    with patch("developer_intelligence.app.GitHubService") as mock_service:
        mock_service.return_value.get_repository.return_value = repository_data

        response = client.post("/repositories", data={"owner": "pallets", "repo": "flask"})

        assert response.status_code == 200            
        assert b"Not available" in response.data


def test_homepage_contains_navigation(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Developer Intelligence" in response.data
    assert b'href="/history"' in response.data


def test_repository_history_database_error(client):
    with patch("developer_intelligence.app.RepositoryRepository") as mock_repository:
        mock_repository.return_value.find_all.side_effect = sqlite3.OperationalError("database is locked")

        response = client.get("/history")

        assert response.status_code == 500
        assert b"Unable to retrieve repository history" in response.data
