
from pwdlib import PasswordHash
from fastapi import Request, HTTPException, status

password_hash = PasswordHash.recommended()

VALID_ROLES = {"admin", "moderator", "writer"}


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def normalize_role(role: str) -> str:
    # Convert old accounts to the new Writer role
    if role == "user" or not role:
        return "writer"

    return role if role in VALID_ROLES else "writer"


def get_current_user(request: Request):
    user = request.session.get("user")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first"
        )

    user["role"] = normalize_role(user.get("role", "writer"))
    return user


def has_role(request: Request, *roles: str) -> bool:
    user = request.session.get("user")

    if not user:
        return False

    return normalize_role(user.get("role", "writer")) in roles


def require_roles(*roles: str):
    def role_checker(request: Request):
        user = get_current_user(request)

        if normalize_role(user.get("role")) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return user

    return role_checker


def require_admin(request: Request):
    return require_roles("admin")(request)


def require_writer_or_admin(request: Request):
    return require_roles("writer", "admin")(request)


def require_content_manager(request: Request):
    return require_roles("admin", "moderator")(request)
