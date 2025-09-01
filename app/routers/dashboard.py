from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app import database, models
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["dashboard"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(database.get_db)):
    # Assume single user for now (id=1)
    user = db.query(models.User).first()
    print(user)
    logs = db.query(models.ActivityLog).order_by(models.ActivityLog.date.desc()).limit(10).all()
    resources = db.query(models.Resource).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "logs": logs,
        "resources": resources
    })
