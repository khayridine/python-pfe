from database import Base
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON

from sqlalchemy.orm import relationship

class Portefeuille(Base):
    __tablename__ = "portefeuilles"
    id = Column(Integer, primary_key=True, index=True)
    montant_total = Column(Float, nullable=False)

    
    rendement = Column(Float, nullable=True)   # Rendement estimé du portefeuille
    volatilite = Column(Float, nullable=True)  # Volatilité / Risque du portefeuille


    actifs = relationship("Actif", back_populates="portefeuille", cascade="all, delete-orphan")

class Actif(Base):
    __tablename__ = "actifs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    categorie = Column(String, nullable=True)
    type = Column(String, nullable=True)
    pourcentage = Column(Float, nullable=False)
    rendement = Column(Float, nullable=False)
    volatilite = Column(Float, nullable=False)

    portefeuille_id = Column(Integer, ForeignKey("portefeuilles.id"))
    portefeuille = relationship("Portefeuille", back_populates="actifs")

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


