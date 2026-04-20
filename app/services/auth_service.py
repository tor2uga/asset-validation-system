from app import models
from sqlalchemy.orm import Session


def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.ADUser).filter(models.ADUser.id == user_id).first()
    if not user:
        raise Exception("User not found")
    return user


def require_role(user, allowed_roles: list[str]):
    if user.role not in allowed_roles:
        raise Exception("Access denied")
    return True


def get_user_with_role_check(user_id: int, allowed_roles: list[str], db: Session):
    user = get_user_by_id(user_id, db)
    require_role(user, allowed_roles)
    return user