import requests
from flask import Flask, render_template, request

from developer_intelligence.services.github import GitHubService


def create_app():
    # Crear y configurar la aplicación Flask.
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route("/repositories", methods=["POST"])
    def analyze_repository():
        # 1. Recuperar owner y repo del formulario.
        owner = request.form.get("owner", "").strip()
        repo = request.form.get("repo", "").strip()

        if not owner or not repo:
            return render_template(
                "error.html",
                error="Owner and repository are required",
            ), 400

        # 2. Crear una instancia de GitHubService.
        github_service = GitHubService()

        # 3. Consultar el repositorio.    
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

        # 4. Renderizar una plantilla con los resultados.
        return render_template("repository.html", repository=repository_data)

    return app