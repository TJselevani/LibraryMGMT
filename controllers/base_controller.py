from core.base.controller import BaseController


# Make your existing controllers inherit from BaseController
class UsersController(BaseController):
    def __init__(self, db_manager):
        super().__init__(db_manager)
        # existing code...
