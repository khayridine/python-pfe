from database import Base
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    mot_de_passe = Column(String, nullable=False)
    num_tel = Column(String, nullable=False, unique=True)
    
class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    statut = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    taxe = Column(Float)
    frais = Column(Float)

