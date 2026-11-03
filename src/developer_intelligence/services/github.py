import requests


class GitHubService:
    BASE_URL = "https://api.github.com"
    TIMEOUT = 10

    def __init__(self, session: None):
        self.session = session if session is not None else requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json"})        

    def get_repository(self, owner: str, repo: str) -> dict:
        if not owner or not repo:
            raise ValueError("Owner and repository name must be provided.")

        url = f"{self.BASE_URL}/repos/{owner}/{repo}"

        response = self.session.get(url, timeout=self.TIMEOUT)

        response.raise_for_status()

        data = response.json()

        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data["description"],
            "language": data["language"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
        }
    