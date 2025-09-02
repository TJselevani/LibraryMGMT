import pytest
from controllers.users_controller import UsersController


def test_get_all_users(mock_db_manager):
    controller = UsersController(mock_db_manager)
    # Test implementation
