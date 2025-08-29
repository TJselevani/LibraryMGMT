import hashlib
import secrets
from passlib.hash import bcrypt
from db.models import UserRole


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)


def set_password(self, password):
    """Hash and set password with salt"""
    self.salt = secrets.token_hex(16)
    password_salt = password + self.salt
    self.password_hash = hashlib.sha256(password_salt.encode()).hexdigest()


def verify_password_2(self, password):
    """Verify password against stored hash"""
    password_salt = password + self.salt
    return hashlib.sha256(password_salt.encode()).hexdigest() == self.password_hash


def has_permission(self, required_role):
    """Check if user has required permission level"""
    role_hierarchy = {
        UserRole.ASSISTANT: 1,
        UserRole.LIBRARIAN: 2,
        UserRole.ADMIN: 3,
    }
    return role_hierarchy[self.role] >= role_hierarchy[required_role]
