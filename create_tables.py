# create_tables.py

from database import Base, engine
from models import User, Operation, Portefeuille, Actif  # Assure-toi d'importer tous les modèles

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)