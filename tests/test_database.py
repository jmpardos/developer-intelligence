import sqlite3
from contextlib import closing

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
    repository_repo.save(repository_data)

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
    repository_repo.save(updated_repository_data)

    result = repository_repo.find_by_github_id(12345)

    assert result is not None
    assert result["github_id"] == 12345
    assert result["name"] == "flask"
    assert result["full_name"] == "pallets/flask"
    assert result["description"] == "The updated Python micro framework"
    assert result["stars"] == 150
    assert result["forks"] == 20
    assert result["open_issues"] == 5


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