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
    Operation(type="achat", date=date(2025, 5, 3), statut="terminé", montant=2000, taxe=30, frais=5),
    Operation(type="vente", date=date(2025, 5, 8), statut="terminé", montant=1700, taxe=22, frais=8),
    Operation(type="achat", date=date(2025, 5, 12), statut="en cours", montant=2500, taxe=35, frais=6),
    Operation(type="vente", date=date(2025, 5, 15), statut="terminé", montant=2200, taxe=28, frais=9),
    Operation(type="achat", date=date(2025, 5, 20), statut="en cours", montant=3000, taxe=40, frais=10),
    Operation(type="vente", date=date(2025, 5, 25), statut="terminé", montant=2700, taxe=32, frais=12),
    Operation(type="achat", date=date(2025, 6, 1), statut="terminé", montant=3200, taxe=45, frais=11),
    Operation(type="vente", date=date(2025, 6, 5), statut="terminé", montant=2800, taxe=30, frais=10),
    Operation(type="achat", date=date(2025, 6, 10), statut="en cours", montant=3500, taxe=50, frais=15),
    Operation(type="vente", date=date(2025, 6, 15), statut="terminé", montant=3300, taxe=33, frais=13),
    Operation(type="achat", date=date(2025, 6, 20), statut="en cours", montant=3700, taxe=55, frais=14),
    Operation(type="vente", date=date(2025, 6, 25), statut="terminé", montant=3900, taxe=60, frais=16),
    Operation(type="achat", date=date(2025, 7, 1), statut="en cours", montant=4000, taxe=65, frais=17),
    Operation(type="vente", date=date(2025, 7, 5), statut="terminé", montant=4200, taxe=70, frais=18),
    Operation(type="achat", date=date(2025, 7, 10), statut="en cours", montant=4300, taxe=75, frais=19),
    Operation(type="vente", date=date(2025, 7, 15), statut="terminé", montant=4400, taxe=80, frais=20),
    
]

# Insertion dans la base
session.add_all(operations)
session.commit()
session.close()

print("✅ Données de test insérées avec succès.")
