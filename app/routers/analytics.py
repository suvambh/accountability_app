from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import database, models
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="/analytics", tags=["analytics"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/", response_class=HTMLResponse)
def analytics_dashboard(request: Request, db: Session = Depends(database.get_db)):
    # 1. Total time invested
    total_time = db.query(func.sum(models.ActivityLog.time_allocated)).scalar() or 0

    # 2. Time by resource type
    time_by_type = (
        db.query(models.Resource.type, func.sum(models.ActivityLog.time_allocated))
        .join(models.Resource, models.ActivityLog.resource_id == models.Resource.id)
        .group_by(models.Resource.type)
        .all()
    )
    time_by_type_data = {rtype: minutes for rtype, minutes in time_by_type}

    # 3. Average session length
    avg_session = db.query(func.avg(models.ActivityLog.time_allocated)).scalar() or 0

    # 4. All session lengths (for histogram)
    session_lengths = [
        row[0] for row in db.query(models.ActivityLog.time_allocated).all() if row[0] is not None
    ]

    # 5. XP growth over time (daily)
    xp_by_date = (
        db.query(models.ActivityLog.date, func.sum(models.ActivityLog.xp_earned))
        .group_by(models.ActivityLog.date)
        .order_by(models.ActivityLog.date)
        .all()
    )
    xp_by_date_labels = [str(row[0]) for row in xp_by_date]
    xp_by_date_values = [row[1] for row in xp_by_date]

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "total_time": total_time,
        "avg_session": avg_session,
        "time_by_type": time_by_type_data,
        "session_lengths": session_lengths,
        "xp_labels": xp_by_date_labels,
        "xp_values": xp_by_date_values,
    })
