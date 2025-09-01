import csv
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app import models



def reset_tables(db):
    db.query(models.User).delete()
    db.query(models.Resource).delete()
    db.query(models.ActivityLog).delete()
    db.commit()


def seed_users(db: Session, filepath: str):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = models.User(name=row["name"])
            db.add(user)
    db.commit()

def seed_resources(db: Session, filepath: str):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            resource = models.Resource(
                name=row["name"],
                type=models.ResourceType(row["type"]),
                link=row["link"],
                chapter_number=int(row["chapter_number"]) if row["chapter_number"] else None,
                duration=int(row["duration"]) if row["duration"] else None,
                details=row["details"],
            )
            db.add(resource)
    db.commit()

def seed_logs(db: Session, filepath: str):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            log = models.ActivityLog(
                user_id=int(row["user_id"]),
                resource_id=int(row["resource_id"]),
                mode=models.Mode(row["mode"]),
                goal=row["goal"],
                time_allocated=int(row["time_allocated"]),
                completion_percent=float(row["completion_percent"]),
                outcome=models.Outcome(row["outcome"]),
                notes=row["notes"],
                xp_earned=int(row["xp_earned"]),
                status=models.Status.completed,
            )
            db.add(log)
    db.commit()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)  # ensure tables exist
    db = SessionLocal()
    reset_tables(db) 
    print("🌱 Seeding database...")
    seed_users(db, "data/users.csv")
    seed_resources(db, "data/resources.csv")
    seed_logs(db, "data/logs.csv")
    print("✅ Database seeded with CSV data")

    db.close()
