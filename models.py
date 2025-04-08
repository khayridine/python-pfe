from sqlalchemy import Column, Integer, String
from database import Base  # Assure-toi que Base est bien importé

class User(Base):
    __tablename__ = "User"  # Nom de la table dans PostgreSQL (respecte la casse)
    
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    mot_de_passe = Column(String, nullable=False)
    num_tel = Column(String, nullable=False, unique=True)
