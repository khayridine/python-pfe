from sqlalchemy.orm import Session
from database import SessionLocal
from models import Operation
from datetime import date

# Connexion à la base
session: Session = SessionLocal()

# Données de test
operations = [
    Operation(type="achat", date=date(2025, 4, 1), statut="terminé", montant=1000, taxe=20, frais=5),
    Operation(type="vente", date=date(2025, 4, 5), statut="terminé", montant=1500, taxe=25, frais=10),
    Operation(type="achat", date=date(2025, 4, 10), statut="en cours", montant=2000, taxe=30, frais=7),
]

# Insertion dans la base
session.add_all(operations)
session.commit()
session.close()

print("✅ Données de test insérées avec succès.")
