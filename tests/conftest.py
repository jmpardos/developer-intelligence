import pytest

from developer_intelligence.app import create_app


@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test.db"

    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": database_path,
        }
    )
    
    return app.test_client()