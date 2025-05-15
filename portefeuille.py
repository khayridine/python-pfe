from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Portefeuille, Actif
from schemas import PortefeuilleCreate


router = APIRouter()

@router.post("/save-portefeuille")  

def create_portefeuille(data: PortefeuilleCreate, db: Session = Depends(get_db)):
    portefeuille = Portefeuille(montant_total=data.montant_total)
    db.add(portefeuille)
    db.flush()  # Pour récupérer l'id

    for actif in data.actifs:
        actif = Actif(
            nom=actif.nom,
            categorie=actif.categorie,
            type=actif.type,
            pourcentage=actif.pourcentage,
            rendement=actif.rendement,
            volatilite=actif.volatilite,
            portefeuille_id=portefeuille.id
        )
        db.add(actif)

    db.commit()
    return {"message": "Portefeuille créé avec succès", "id": portefeuille.id}

