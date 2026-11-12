from datetime import UTC, datetime
from pathlib import Path

import requests
from flask import Flask, render_template, request

from developer_intelligence.persistence.database import initialize_database
from developer_intelligence.persistence.repository import RepositoryRepository
from developer_intelligence.services.analytics import RepositoryAnalyticsService
from developer_intelligence.services.github import GitHubService


def create_app(test_config=None):
    app = Flask(__name__)

    database_path = Path(app.instance_path) / "developer_intelligence.db"
    app.config["DATABASE_PATH"] = database_path

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    initialize_database(app.config["DATABASE_PATH"])

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route("/repositories", methods=["POST"])
    def analyze_repository():
        owner = request.form.get("owner", "").strip()
        repo = request.form.get("repo", "").strip()

        if not owner or not repo:
            return render_template(
                "error.html",
                error="Owner and repository are required",
            ), 400

        github_service = GitHubService()

        try:
            repository_data = github_service.get_repository(owner, repo)
        except requests.exceptions.Timeout:
            return render_template(
                "error.html",
                error="GitHub is taking too long to respond",
            ), 504
        except requests.exceptions.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            if status_code == 404:
                return render_template(
                    "error.html",
                    error="Repository not found",
                ), 404

            if status_code == 403:
                return render_template(
                    "error.html",
                    error="Unable to access GitHub repository",
                ), 502

            return render_template(
                "error.html",
                error="GitHub returned an unexpected error",
            ), 502
        except requests.exceptions.RequestException:
            return render_template(
                "error.html",
                error="Unable to connect to GitHub",
            ), 502

        repository_repo = RepositoryRepository(
            app.config["DATABASE_PATH"]
        )
        repository_repo.save(repository_data)

        analytics_service = RepositoryAnalyticsService(datetime.now(UTC))
        analytics = {
            "repository_age_days": analytics_service.repository_age_days(repository_data["github_created_at"]),
            "days_since_last_push": analytics_service.days_since_last_push(repository_data["github_pushed_at"]),
            "stars_per_year": analytics_service.stars_per_year(repository_data["stars"], repository_data["github_created_at"]),
        }
        
        return render_template("repository.html", repository=repository_data, analytics=analytics)

    @app.route("/history", methods=["GET"])
    def repository_history():
        repository_repo = RepositoryRepository(
            app.config["DATABASE_PATH"]
        )
        repositories = repository_repo.find_all()

        return render_template("history.html", repositories=repositories)

    return app