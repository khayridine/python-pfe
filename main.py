from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import User
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import auth
from auth import get_current_user, create_access_token, authenticate_user

app = FastAPI()
app.include_router(auth.router)

# Autoriser les requêtes de ton frontend Angular
origins = [
    "http://localhost:4200"  # L'URL de ton frontend Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines (changer pour la production)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

# Créer une session pour interagir avec la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session , Depends(get_db)]      
user_dependency = Annotated[dict , Depends(get_current_user)]  

# Modèle pour la création d'un utilisateur
class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    num_tel: str
    mot_de_passe: str

# Modèle pour la connexion
class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str

# Route POST pour l'inscription (signup)
@app.post("/signup/")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    # Vérification si l'email existe déjà dans la base de données
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Créer un nouvel utilisateur
    nouvel_utilisateur = User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        mot_de_passe=user.mot_de_passe,  # Il faudrait ici hacher le mot de passe
        num_tel=user.num_tel
    )

    db.add(nouvel_utilisateur)
    db.commit()  # Sauvegarder l'utilisateur dans la base
    db.refresh(nouvel_utilisateur)  # Rafraîchir l'objet avec les données mises à jour

    return {"email": nouvel_utilisateur.email}

# Route POST pour la connexion (login)
@app.post("/login/")
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    utilisateur = db.query(User).filter(User.email == user_data.email).first()

    if not utilisateur:
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    # Vérification du mot de passe (vérification du hash ici)
    if utilisateur.mot_de_passe != user_data.mot_de_passe:  # Tu devrais hacher le mot de passe avant de comparer
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    # Générer un token JWT
    token = create_access_token(utilisateur.email, utilisateur.id, timedelta(minutes=30))  # Token expirant après 30 minutes
    return {"access_token": token, "token_type": "bearer"}

# Route GET pour récupérer un utilisateur par ID (protégé par JWT)
@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Vérifier si l'utilisateur actuel correspond à celui demandé
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à accéder à cette ressource")
    
    utilisateur = db.query(User).filter(User.id == user_id).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return utilisateur
@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Chercher l'utilisateur par son ID
    utilisateur = db.query(User).filter(User.id == user_id).first()

    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Supprimer l'utilisateur de la base de données
    db.delete(utilisateur)
    db.commit()

    return {"message": f"L'utilisateur avec l'ID {user_id} a été supprimé avec succès"}    

# Fermer la session lors de l'arrêt de l'application
@app.on_event("shutdown")
def shutdown():
    db.close()

