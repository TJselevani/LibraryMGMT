
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False


class Validator(ABC):
    """Abstract validator interface"""
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data and return result"""
        pass


class FormValidator(Validator):
    """Generic form validator"""
    
    def __init__(self, rules: Dict[str, List[callable]]):
        self.rules = rules
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate form data against rules"""
        result = ValidationResult(True)
        
        for field, validators in self.rules.items():
            field_value = data.get(field)
            
            for validator_func in validators:
                try:
                    if not validator_func(field_value):
                        result.add_error(f"Validation failed for field '{field}'")
                except Exception as e:
                    result.add_error(f"Validation error for field '{field}': {str(e)}")
        
        return result


# Common validation functions
def required(value: Any) -> bool:
    """Check if value is not None and not empty"""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def min_length(min_len: int):
    """Create minimum length validator"""
    def validator(value: str) -> bool:
        return len(value) >= min_len if value else False
    return validator


def email_format(value: str) -> bool:
    """Basic email format validation"""
    import re
    if not value:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return bool(re.match(pattern, value))