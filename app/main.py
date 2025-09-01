from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
from app.routers import users, resources, logs, dashboard
import os
from fastapi.staticfiles import StaticFiles
from app.services import session
from app.routers import analytics

# Create FastAPI app
app = FastAPI(title="Accountability App - MVP")

# Mount static directory
app.mount("/static", StaticFiles(directory="static/"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Templates setup (for HTML dashboard later)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include routers
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(logs.router)
app.include_router(dashboard.router)
app.include_router(session.router)
app.include_router(analytics.router)

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": "Welcome to the Accountability App MVP 🚀"}
    )

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "message": "App is running"}


# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

