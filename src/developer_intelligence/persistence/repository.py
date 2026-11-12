# AI assistance: ChatGPT provided guidance on SQLite persistence,
# UPSERT operations, timestamp handling, and test design.
# The implementation was developed and validated by the author.
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path


class RepositoryRepository:

    def __init__(self, database_path: str | Path):
        self.database_path = database_path

    def find_by_github_id(self, github_id: int) -> dict | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row

            cursor = connection.execute(
                """
                SELECT *
                FROM repositories
                WHERE github_id = ?
                """,
                (github_id,),
            )

            result = cursor.fetchone()

        if result is None:
            return None

        return dict(result)

    def save(self, repository_data: dict) -> None:
        now = datetime.now(UTC).isoformat()
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                """
                INSERT INTO repositories (github_id, name, full_name, description, language, stars, forks, open_issues, github_created_at, github_pushed_at, github_updated_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(github_id)
                DO UPDATE SET
                    name = excluded.name,
                    full_name = excluded.full_name,
                    description = excluded.description,
                    language = excluded.language,
                    stars = excluded.stars,
                    forks = excluded.forks,
                    open_issues = excluded.open_issues,
                    github_created_at = excluded.github_created_at,
                    github_pushed_at = excluded.github_pushed_at,
                    github_updated_at = excluded.github_updated_at,
                    updated_at = excluded.updated_at
                """,
                (
                    repository_data["github_id"],
                    repository_data["name"],
                    repository_data["full_name"],
                    repository_data.get("description"),
                    repository_data.get("language"),
                    repository_data["stars"],
                    repository_data["forks"],
                    repository_data["open_issues"],
                    repository_data.get("github_created_at"),
                    repository_data.get("github_pushed_at"),
                    repository_data.get("github_updated_at"),
                    now,
                    now,
                ),
            )
            connection.commit()

    def find_all(self) -> list[dict]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row

            cursor = connection.execute(
                """
                SELECT *
                FROM repositories
                ORDER BY updated_at DESC, id DESC
                """
            )

            results = cursor.fetchall()

        return [dict(row) for row in results]