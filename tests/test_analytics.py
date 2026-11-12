from datetime import UTC, datetime

from developer_intelligence.services.analytics import RepositoryAnalyticsService


def test_repository_age_days():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.repository_age_days(
        "2020-01-01T00:00:00Z"
    )

    assert result == 2192

def test_repository_less_24_hours():
    reference_date = datetime(2026, 1, 2, 8, 0, 0, 0,tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.repository_age_days(
        "2026-01-01T12:00:00Z"
    )

    assert result == 0

def test_repository_different_timezones():
    reference_date = datetime(2026, 1, 2, 0, 0, 0, 0,tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.repository_age_days(
        "2026-01-01T01:00:00 +01:00"
    )

    assert result == 1

def test_repository_future_date():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.repository_age_days(
        "2026-01-03T00:00:00Z"
    )

    assert result == 0

def test_days_since_last_push():
    reference_date = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.days_since_last_push(
        "2026-10-20T00:00:00Z"
    )

    assert result == 20

def test_days_since_last_push_rec():
    reference_date = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.days_since_last_push(
        "2026-11-09T08:00:00Z"
    )

    assert result == 0

def test_days_since_last_push_none():
    reference_date = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.days_since_last_push(
        None
    )

    assert result is None

def test_days_since_last_push_future():
    reference_date = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.days_since_last_push(
        "2026-11-10T00:00:00Z"
    )

    assert result == 0

def test_stars_5_years_repository():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.stars_per_year(
        stars=1000,
        github_created_at="2021-01-01T00:00:00Z"
    )

    assert result == 200.03

def test_stars_recent_repository():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.stars_per_year(
        stars=100,
        github_created_at="2026-10-31T00:00:00Z"
    )

    assert result == 100.0

def test_stars_no_stars_repository():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.stars_per_year(
        stars=0,
        github_created_at="2021-11-08T00:00:00Z"
    )

    assert result == 0.0

def test_stars_today_repository():
    reference_date = datetime(2026, 1, 1, tzinfo=UTC)

    analytics = RepositoryAnalyticsService(reference_date)

    result = analytics.stars_per_year(
        stars=50,
        github_created_at="2026-11-09T00:00:00Z"
    )

    assert result == 50.0