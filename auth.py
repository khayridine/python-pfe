from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr  # Importation de EmailStr pour validation des emails
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from models import User
from database import SessionLocal




router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Sécurité
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


# Pydantic Models
class CreateUserRequest(BaseModel):
    nom: str
    prenom: str
    email: EmailStr  # Utilisation d'EmailStr pour valider le format de l'email
    mot_de_passe: str
    num_tel: str


class Token(BaseModel):
    access_token: str
    token_type: str


# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

def hash_password(password: str) -> str:
    """Retourne un mot de passe haché"""
    return bcrypt_context.hash(password)


# Routes
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    
    existing_user = db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = User(
        nom=create_user_request.nom,
        prenom=create_user_request.prenom,
        email=create_user_request.email,
        mot_de_passe=bcrypt_context.hash(create_user_request.mot_de_passe),
        num_tel=create_user_request.num_tel
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur créé avec succès"}


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user.email, user.id, timedelta(minutes=20))  # Utilisation de l'email
    return {
    'access_token': token,
    'token_type': 'bearer',
    'user': {
        'id': user.id,
        'nom': user.nom,
        'prenom': user.prenom,
        'email': user.email,
        'num_tel': user.num_tel
    }
    }





def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.email == username).first()  # Vérifie par email
    if not user:
        return False
    if not bcrypt_context.verify(password, user.mot_de_passe):  # Vérification avec bcrypt
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # Décodage du token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user.'
            )
        
        return {'username': username, 'id': user_id}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.'
        )
