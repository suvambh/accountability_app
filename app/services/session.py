from fastapi import APIRouter, Depends, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app import crud, models, database
from app.services import xp
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="/session", tags=["session"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Show the start session form
@router.get("/start", response_class=HTMLResponse)
def start_session_form(request: Request, db: Session = Depends(database.get_db)):
    resources = db.query(models.Resource).all()
    return templates.TemplateResponse("start_session.html", {"request": request, "resources": resources})


@router.post("/start", response_class=HTMLResponse)
def start_session(
    resource_id: str = Form(""),
    custom_name: str = Form(""),
    custom_link: str = Form(""),
    custom_type: models.ResourceType = Form("code"),   # ✅ new field
    mode: models.Mode = Form(...),
    goal: str = Form(...),
    time_allocated: int = Form(...),
    db: Session = Depends(database.get_db)
):
    # If a custom resource is provided, add it
    if not resource_id and custom_name:
        new_res = models.Resource(
            name=custom_name,
            type=custom_type,   # ✅ use user’s choice
            link=custom_link if custom_link else "",
            details="Ad-hoc"
        )
        db.add(new_res)
        db.commit()
        db.refresh(new_res)
        resource_id = new_res.id   # ✅ now it’s int after refresh()

    log = crud.create_log(
        db,
        user_id=1,
        resource_id=resource_id,
        mode=mode,
        goal=goal,
        time_allocated=time_allocated
    )
    return RedirectResponse(f"/session/active/{log.id}", status_code=303)




@router.get("/active/{log_id}", response_class=HTMLResponse)
def active_session(log_id: int, request: Request, db: Session = Depends(database.get_db)):
    log = db.query(models.ActivityLog).get(log_id)
    return templates.TemplateResponse("active_session.html", {"request": request, "log": log})



@router.get("/finish/{log_id}", response_class=HTMLResponse)
def finish_session_form(log_id: int, request: Request, db: Session = Depends(database.get_db)):
    log = db.query(models.ActivityLog).get(log_id)
    if not log:
        return HTMLResponse("Session not found", status_code=404)
    return templates.TemplateResponse("finish_session.html", {"request": request, "log": log})


@router.post("/finish/{log_id}", response_class=HTMLResponse)
def finish_session(
    log_id: int,
    completion_percent: int = Form(...),
    outcome: models.Outcome = Form(...),
    notes_file: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    log = db.query(models.ActivityLog).get(log_id)
    if not log:
        return HTMLResponse("Session not found", status_code=404)

    # Save file only if user uploaded one
    if notes_file and notes_file.filename:
        upload_dir = "accountability_app/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, notes_file.filename)

        with open(file_path, "wb") as f:
            f.write(notes_file.file.read())

        log.notes_file = file_path

    # Update other fields
    log.completion_percent = completion_percent
    log.outcome = outcome
    log.status = models.Status.completed

    db.commit()
    return RedirectResponse("/dashboard", status_code=303)

