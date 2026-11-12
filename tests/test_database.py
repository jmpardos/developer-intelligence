# AI assistance: ChatGPT was used to discuss test cases,
# mocking strategies, and debugging of test failures.
# Tests were implemented, reviewed, and executed by the author.
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from unittest.mock import patch

from developer_intelligence.persistence.database import initialize_database
from developer_intelligence.persistence.repository import RepositoryRepository


def test_initialize_database(tmp_path):
    database_path = tmp_path / "test.db"

    initialize_database(database_path)

    assert database_path.exists()

    with closing(sqlite3.connect(database_path)) as connection:
        cursor = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'repositories'
            """
        )

        result = cursor.fetchone()

    assert result is not None
    assert result[0] == "repositories"


def test_initialize_database_twice(tmp_path):
    database_path = tmp_path / "test.db"

    initialize_database(database_path)
    initialize_database(database_path)

    assert database_path.exists()

    with closing(sqlite3.connect(database_path)) as connection:
        cursor = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'repositories'
            """
        )

        result = cursor.fetchone()

    assert result is not None
    assert result[0] == "repositories"


def test_find_repository_not_found(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    repository_repo = RepositoryRepository(database_path)
    result = repository_repo.find_by_github_id(12345)

    assert result is None


def test_save_repository(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    repository_repo = RepositoryRepository(database_path)
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
    repository_repo.save(repository_data)

    result = repository_repo.find_by_github_id(12345)

    assert result is not None
    assert result["github_id"] == 12345
    assert result["full_name"] == "pallets/flask"    
    assert result["stars"] == 100
    assert result["created_at"] is not None
    assert result["updated_at"] is not None


def test_update_existing_repository(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    repository_repo = RepositoryRepository(database_path)

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

    updated_repository_data = {
        "github_id": 12345,
        "name": "flask",
        "full_name": "pallets/flask",
        "description": "The updated Python micro framework",
        "language": "Python",
        "stars": 150,
        "forks": 20,
        "open_issues": 5,
    }

    # 1. Define two different dates.
    first_timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    second_timestamp = datetime(2026, 1, 2, tzinfo=UTC)

    # 2. First insertion.
    with patch(
        "developer_intelligence.persistence.repository.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = first_timestamp
        repository_repo.save(repository_data)

    # 3. Retrieve the original record.
    original_repository = repository_repo.find_by_github_id(12345)

    assert original_repository is not None
    assert original_repository["created_at"] == first_timestamp.isoformat()
    assert original_repository["updated_at"] == first_timestamp.isoformat()

    # 4. Second insertion: it should update the existing record.
    with patch(
        "developer_intelligence.persistence.repository.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = second_timestamp
        repository_repo.save(updated_repository_data)

    # 5. Retrieve the updated record.
    result = repository_repo.find_by_github_id(12345)

    assert result is not None

    # 6. Verify the updated data.
    assert result["github_id"] == 12345
    assert result["name"] == "flask"
    assert result["full_name"] == "pallets/flask"
    assert result["description"] == "The updated Python micro framework"
    assert result["stars"] == 150
    assert result["forks"] == 20
    assert result["open_issues"] == 5

    # 7. Verify that there are no duplicate records.
    repositories = repository_repo.find_all()
    assert len(repositories) == 1

    # 8. Verify the dates.
    assert result["created_at"] == first_timestamp.isoformat()
    assert result["updated_at"] == second_timestamp.isoformat()


def test_find_all_empty(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    repository_repo = RepositoryRepository(database_path)
    result = repository_repo.find_all()

    assert result == []


def test_find_all_repositories(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    repository_repo = RepositoryRepository(database_path)
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
        "description": "The Web framework for perfectionists with deadlines.",
        "language": "Python",
        "stars": 200,
        "forks": 50,
        "open_issues": 10,
    }
    repository_repo.save(repository_data_1)
    repository_repo.save(repository_data_2)

    result = repository_repo.find_all()

    assert len(result) == 2
