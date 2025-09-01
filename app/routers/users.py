from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, database

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=dict)
def create_user(name: str, db: Session = Depends(database.get_db)):
    user = crud.create_user(db, name)
    return {"id": user.id, "name": user.name}

@router.get("/", response_model=list[dict])
def list_users(db: Session = Depends(database.get_db)):
    users = crud.list_users(db)
    return [{"id": u.id, "name": u.name, "xp": u.xp, "level": u.level} for u in users]

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "xp": user.xp, "level": user.level}

@router.put("/{user_id}", response_model=dict)
def update_user(user_id: int, name: str, db: Session = Depends(database.get_db)):
    user = crud.update_user(db, user_id, name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "xp": user.xp, "level": user.level}

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted"}
