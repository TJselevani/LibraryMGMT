from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseController(ABC):
    """Base controller with common functionality"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all records"""
        pass

    def get_by_id(self, id: int) -> Optional[Any]:
        """Get record by ID - override if needed"""
        raise NotImplementedError

    def create(self, data: Dict) -> Dict:
        """Create new record - override if needed"""
        raise NotImplementedError

    def update(self, id: int, data: Dict) -> Dict:
        """Update record - override if needed"""
        raise NotImplementedError

    def delete(self, id: int) -> Dict:
        """Delete record - override if needed"""
        raise NotImplementedError
