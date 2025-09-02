from abc import ABC, abstractmethod
from typing import List, Any


class Observer(ABC):
    """Observer interface"""

    @abstractmethod
    def update(self, subject: "Subject", data: Any = None):
        """Called when subject state changes"""
        pass


class Subject(ABC):
    """Subject interface for observer pattern"""

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, data: Any = None):
        """Notify all observers of state change"""
        for observer in self._observers:
            observer.update(self, data)
