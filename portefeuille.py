# portefeuille.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 
from sqlalchemy import func
from fastapi.responses import JSONResponse
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

@router.get("/portefeuilles/nb-actifs")
def get_nombre_actifs_par_portefeuille(db: Session = Depends(get_db)):
    result = db.query(
        Portefeuille.id.label("portefeuille_id"),
        func.count(Actif.id).label("nombre_actifs")
    ).join(Actif).group_by(Portefeuille.id).all()

    
    data = [{"portefeuille_id": row.portefeuille_id, "nombre_actifs": row.nombre_actifs} for row in result]
    return JSONResponse(content=data)


@router.get("/portefeuilles")
def get_portefeuilles_complets(db: Session = Depends(get_db)):
    portefeuilles = db.query(Portefeuille).all()
    data = []
    for pf in portefeuilles:
        actifs = [
            {
                "nom": a.nom,
                "categorie": a.categorie,
                "type": a.type,
                "pourcentage": a.pourcentage,
                "rendement": a.rendement,
                "volatilite": a.volatilite
            }
            for a in pf.actifs
        ]
        
       
        rendement = sum(a.rendement * a.pourcentage / 100 for a in pf.actifs)
        risque = sum(a.volatilite * a.pourcentage / 100 for a in pf.actifs)  
        sharpe = rendement / risque if risque != 0 else 0
        
        data.append({
            "id": pf.id,
            "montant_total": pf.montant_total,
            "actifs": actifs,
            "rendement": rendement,
            "risque": risque,
            "sharpe": sharpe
        })
    return JSONResponse(content=data)