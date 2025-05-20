# portefeuille.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Portefeuille, Actif
from schemas import PortefeuilleCreate



router = APIRouter()

@router.post("/save-portefeuille")
def save_portefeuille(portefeuille_data: PortefeuilleCreate, db: Session = Depends(get_db)):
    
    portefeuille = Portefeuille(montant_total=portefeuille_data.montant_total)
    db.add(portefeuille)
    db.commit()
    db.refresh(portefeuille)

    # Création des actifs associés
    for actif_data in portefeuille_data.actifs:
        actif = Actif(
            nom=actif_data.nom,
            categorie=actif_data.categorie,
            type=actif_data.type,
            pourcentage=actif_data.pourcentage,
            rendement=actif_data.rendement,
            volatilite=actif_data.volatilite,
            portefeuille_id=portefeuille.id
        )
        db.add(actif)

    db.commit()
    return {"message": "Portefeuille sauvegardé avec succès", "id": portefeuille.id}
print(">>> portefeuille.py chargé")
