import pytest
from core.container import DIContainer
from unittest.mock import Mock


@pytest.fixture
def mock_db_manager():
    return Mock()


@pytest.fixture
def container(mock_db_manager):
    return DIContainer(mock_db_manager)


@pytest.fixture
def mock_auth_service():
    auth = Mock()
    auth.db_manager = Mock()
    return auth
