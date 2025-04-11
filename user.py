from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from database import SessionLocal
from models import User
from auth import get_current_user, create_access_token
from datetime import timedelta

router = APIRouter()

# Dépendances
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Schemas Pydantic
class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    num_tel: str
    mot_de_passe: str

class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str

# Inscription
@router.post("/signup/")
def add_user(user: UserCreate, db: db_dependency):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    nouvel_utilisateur = User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        mot_de_passe=user.mot_de_passe,
        num_tel=user.num_tel
    )

    db.add(nouvel_utilisateur)
    db.commit()
    db.refresh(nouvel_utilisateur)

    return {"email": nouvel_utilisateur.email}

# Connexion
@router.post("/login/")
def login(user_data: LoginRequest, db: db_dependency):
    utilisateur = db.query(User).filter(User.email == user_data.email).first()
    if not utilisateur or utilisateur.mot_de_passe != user_data.mot_de_passe:
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    token = create_access_token(utilisateur.email, utilisateur.id, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

# Récupération d'utilisateur
@router.get("/user/{user_id}")
def get_user(user_id: int, db: db_dependency, current_user: user_dependency):
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    utilisateur = db.query(User).filter(User.id == user_id).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return utilisateur

# Suppression d'utilisateur
@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: db_dependency):
    utilisateur = db.query(User).filter(User.id == user_id).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(utilisateur)
    db.commit()

    return {"message": f"L'utilisateur avec l'ID {user_id} a été supprimé avec succès"}
