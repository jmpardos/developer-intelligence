# AI assistance: ChatGPT was used to discuss analytics calculations,
# timezone handling, edge cases, and automated testing.
# The implementation was developed and validated by the author.
from datetime import datetime


class RepositoryAnalyticsService:

    def __init__(self, reference_date: datetime):
        if (
            reference_date.tzinfo is None
            or reference_date.utcoffset() is None
        ):
            raise ValueError("Reference date must be timezone-aware")

        self.reference_date = reference_date

    def repository_age_days(self, github_created_at: str) -> int:
        return self._days_since(github_created_at)

    def days_since_last_push(self, github_pushed_at: str | None) -> int | None:
        if github_pushed_at is None:
            return None

        return self._days_since(github_pushed_at)

    def _days_since(self, date: str) -> int:
        parsed_date = datetime.fromisoformat(date)
        return max(0, (self.reference_date - parsed_date).days)

    def stars_per_year(self, stars: int, github_created_at: str) -> float:
        age_days = self.repository_age_days(github_created_at)
        age_years = max(1, age_days / 365.25)
        return round(stars / age_years, 2)