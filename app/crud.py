from sqlalchemy.orm import Session
from datetime import datetime, date
from app import models

# -------------------------
# USERS
# -------------------------

def create_user(db: Session, name: str):
    user = models.User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def update_user(db: Session, user_id: int, name: str = None):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    if name:
        user.name = name
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# -------------------------
# RESOURCES
# -------------------------

def create_resource(db: Session, name: str, type: models.ResourceType, link: str,
                    chapter_number: int = None, duration: int = None, details: str = None):
    resource = models.Resource(
        name=name,
        type=type,
        link=link,
        chapter_number=chapter_number,
        duration=duration,
        details=details,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def get_resource(db: Session, resource_id: int):
    return db.query(models.Resource).filter(models.Resource.id == resource_id).first()

def list_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).offset(skip).limit(limit).all()

# -------------------------
# RESOURCES
# -------------------------

def update_resource(db: Session, resource_id: int, name: str = None,
                    type: models.ResourceType = None, link: str = None,
                    chapter_number: int = None, duration: int = None,
                    details: str = None):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        return None
    if name:
        resource.name = name
    if type:
        resource.type = type
    if link:
        resource.link = link
    if chapter_number is not None:
        resource.chapter_number = chapter_number
    if duration is not None:
        resource.duration = duration
    if details:
        resource.details = details
    db.commit()
    db.refresh(resource)
    return resource

def delete_resource(db: Session, resource_id: int):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        return None
    db.delete(resource)
    db.commit()
    return resource


# -------------------------
# ACTIVITY LOGS
# -------------------------

def create_log(db: Session, user_id: int, resource_id: int, mode: models.Mode,
               goal: str = None, time_allocated: int = None, status: models.Status = models.Status.in_progress):
    log = models.ActivityLog(
        user_id=user_id,
        resource_id=resource_id,
        chapter_number=db.query(models.Resource).get(resource_id).chapter_number,
        mode=mode,
        goal=goal,
        time_allocated=time_allocated,
        start_time=datetime.now(),
        date=date.today(),
        status=status,
        completion_percent=0.0,
        outcome=None,
        xp_earned=0,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def complete_log(db: Session, log_id: int, completion_percent: float, outcome: models.Outcome, notes: str = None):
    log = db.query(models.ActivityLog).filter(models.ActivityLog.id == log_id).first()
    if not log:
        return None

    log.end_time = datetime.now()
    log.status = models.Status.completed
    log.completion_percent = completion_percent
    log.outcome = outcome
    log.notes = notes

    db.commit()
    db.refresh(log)
    return log


def list_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ActivityLog).offset(skip).limit(limit).all()


def update_log(db: Session, log_id: int, completion_percent: float = None,
               outcome: models.Outcome = None, notes: str = None):
    log = db.query(models.ActivityLog).filter(models.ActivityLog.id == log_id).first()
    if not log:
        return None
    if completion_percent is not None:
        log.completion_percent = completion_percent
    if outcome is not None:
        log.outcome = outcome
    if notes is not None:
        log.notes = notes
    db.commit()
    db.refresh(log)
    return log

def delete_log(db: Session, log_id: int):
    log = db.query(models.ActivityLog).filter(models.ActivityLog.id == log_id).first()
    if not log:
        return None
    db.delete(log)
    db.commit()
    return log


