from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app import crud, models, database
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="/resources", tags=["resources"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# -----------------------
# UI ROUTE (HTML PAGE)
# -----------------------
@router.get("/", response_class=HTMLResponse)
def resources_page(request: Request, db: Session = Depends(database.get_db)):
    resources = crud.list_resources(db)
    return templates.TemplateResponse("resources.html", {
        "request": request,
        "resources": resources
    })

# -----------------------
# API ROUTES (JSON)
# -----------------------

@router.post("/api", response_model=dict)
def create_resource(name: str, type: models.ResourceType, link: str,
                    chapter_number: int | None = None, duration: int | None = None,
                    db: Session = Depends(database.get_db)):
    resource = crud.create_resource(db, name, type, link, chapter_number, duration)
    return {"id": resource.id, "name": resource.name, "type": resource.type, "link": resource.link}

@router.get("/api", response_model=list[dict])
def list_resources_api(db: Session = Depends(database.get_db)):
    resources = crud.list_resources(db)
    return [
        {"id": r.id, "name": r.name, "type": r.type, "link": r.link, "chapter_number": r.chapter_number}
        for r in resources
    ]

@router.put("/api/{resource_id}", response_model=dict)
def update_resource(resource_id: int,
                    name: str = None,
                    type: models.ResourceType = None,
                    link: str = None,
                    chapter_number: int = None,
                    duration: int = None,
                    details: str = None,
                    db: Session = Depends(database.get_db)):
    resource = crud.update_resource(db, resource_id, name, type, link, chapter_number, duration, details)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {
        "id": resource.id,
        "name": resource.name,
        "type": resource.type,
        "link": resource.link,
        "chapter_number": resource.chapter_number,
        "duration": resource.duration,
        "details": resource.details,
    }

@router.delete("/api/{resource_id}", response_model=dict)
def delete_resource(resource_id: int, db: Session = Depends(database.get_db)):
    resource = crud.delete_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": f"Resource {resource_id} deleted"}
