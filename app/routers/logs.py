from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import crud, models, database
from app.services import xp
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="/logs", tags=["logs"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# -----------------------
# UI ROUTE (HTML PAGE)
# -----------------------
@router.get("/", response_class=HTMLResponse)
def logs_page(request: Request, db: Session = Depends(database.get_db)):
    logs = db.query(models.ActivityLog).order_by(models.ActivityLog.date.desc()).all()
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs
    })

# -----------------------
# API ROUTES (JSON)
# -----------------------

@router.post("/", response_model=dict)
def create_log(user_id: int, resource_id: int, mode: models.Mode, goal: str = None,
               time_allocated: int = None, db: Session = Depends(database.get_db)):
    log = crud.create_log(db, user_id, resource_id, mode, goal, time_allocated)
    return {"id": log.id, "user_id": log.user_id, "resource_id": log.resource_id, "status": log.status}


@router.post("/{log_id}/complete", response_model=dict)
def complete_log(log_id: int, completion_percent: float, outcome: models.Outcome, notes: str = None,
                 db: Session = Depends(database.get_db)):
    log = crud.complete_log(db, log_id, completion_percent, outcome, notes)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # XP + User Progress
    user = db.query(models.User).filter(models.User.id == log.user_id).first()
    xp_total = xp.calculate_xp(log)
    log.xp_earned = xp_total
    xp.update_user_progress(user, xp_total)

    db.commit()
    db.refresh(log)

    return {
        "id": log.id,
        "completion_percent": log.completion_percent,
        "outcome": log.outcome,
        "xp": log.xp_earned,
        "user": {"id": user.id, "xp": user.xp, "level": user.level, "streak": user.current_streak}
    }


@router.get("/api", response_model=list[dict])  # <-- changed path to avoid clash with UI
def list_logs(db: Session = Depends(database.get_db)):
    logs = crud.list_logs(db)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "resource_id": l.resource_id,
            "goal": l.goal,
            "mode": l.mode,
            "status": l.status,
            "completion_percent": l.completion_percent,
            "outcome": l.outcome,
            "xp": l.xp_earned,
        }
        for l in logs
    ]


@router.put("/{log_id}", response_model=dict)
def update_log(log_id: int, completion_percent: float = None,
               outcome: models.Outcome = None, notes: str = None,
               db: Session = Depends(database.get_db)):
    log = crud.update_log(db, log_id, completion_percent, outcome, notes)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"id": log.id, "completion_percent": log.completion_percent,
            "outcome": log.outcome, "notes": log.notes}


@router.delete("/{log_id}", response_model=dict)
def delete_log(log_id: int, db: Session = Depends(database.get_db)):
    log = crud.delete_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"message": f"Log {log_id} deleted"}
