from typing import Any, TypeVar, Dict  # , Type
from controllers.users_controller import UsersController
from controllers.patrons_controller import PatronsController
from controllers.books_controller import BooksController
from controllers.borrowed_books_controller import BorrowedBooksController
from controllers.payments_controller import PaymentController, PaymentItemController
from controllers.auth_controller import AuthenticationService


T = TypeVar("T")


class DIContainer:
    """Dependency Injection Container"""

    def __init__(self, db_manager):
        self._services = {}
        self._singletons = {}
        self.db_manager = db_manager
        self._register_services()

    def _register_services(self):
        """Register all services"""
        self._services["users"] = lambda: UsersController(self.db_manager)
        self._services["patrons"] = lambda: PatronsController(self.db_manager)
        self._services["books"] = lambda: BooksController(self.db_manager)
        self._services["b_books"] = lambda: BorrowedBooksController(self.db_manager)
        self._services["payment"] = lambda: PaymentController(self.db_manager)
        self._services["payment_item"] = lambda: PaymentItemController(self.db_manager)
        # ... register other controllers

    def get(self, service_name: str) -> Any:
        """Get service instance"""
        if service_name in self._singletons:
            return self._singletons[service_name]

        if service_name in self._services:
            instance = self._services[service_name]()
            self._singletons[service_name] = instance
            return instance

        raise ValueError(f"Service '{service_name}' not registered")

    def register(self, name: str, factory_func):
        """Register a new service"""
        self._services[name] = factory_func


# =====================================================================
# DEPENDENCY CONTAINER
# =====================================================================


class DependencyContainer:
    """Dependency injection container"""

    def __init__(self, auth_service):
        self.db_manager = auth_service.db_manager
        self.auth_service = auth_service
        self._controllers = {}
        self._initialize_controllers()

    def _initialize_controllers(self):
        """Initialize all controllers"""
        self._controllers = {
            "patrons": PatronsController(self.db_manager),
            "books": BooksController(self.db_manager),
            "borrowed_books": BorrowedBooksController(self.db_manager),
            "payments": PaymentController(self.db_manager),
            "payment_items": PaymentItemController(self.db_manager),
            "users": UsersController(self.db_manager),
            "auth": AuthenticationService(self.db_manager),
        }

    def get_controller(self, name: str):
        """Get controller by name"""
        return self._controllers.get(name)

    def get_all_controllers(self) -> Dict[str, Any]:
        """Get all controllers"""
        return self._controllers.copy()
