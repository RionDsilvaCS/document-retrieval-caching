from sqlalchemy.orm import Session
from sqlalchemy import update
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user_id: str):
    db_user = models.User(user_id=user_id, count=1)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_count(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    db_user.count += 1
    db.commit()
    db.refresh(db_user)
    return db_user
