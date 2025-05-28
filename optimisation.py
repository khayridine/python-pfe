from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from scipy.optimize import minimize
from fastapi import APIRouter
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Portefeuille, Actif
from fastapi import HTTPException

router = APIRouter()

class OptimisationRequest(BaseModel):
    portefeuille_id: int
    covariance_matrix: List[List[float]]  

class PointFrontiere(BaseModel):
    rendement: float
    risque: float

class OptimisationResponse(BaseModel):
    allocation_actuelle: List[float]
    allocation_optimisee: List[float]
    message: str
    frontiere: List[PointFrontiere]

def get_portefeuille_data(portefeuille_id: int):
    db: Session = SessionLocal()
    
    portefeuille = db.query(Portefeuille).filter(Portefeuille.id == portefeuille_id).first()
    if not portefeuille:
        db.close()
        raise HTTPException(status_code=404, detail="Portefeuille non trouvé")
    
    actifs = portefeuille.actifs
    if not actifs:
        db.close()
        raise HTTPException(status_code=404, detail="Aucun actif trouvé pour ce portefeuille")

    noms = [a.nom for a in actifs]
    rendements = [a.rendement for a in actifs]
    volatilites = [a.volatilite for a in actifs]
    allocation_actuelle = [a.pourcentage / 100 for a in actifs]  # conversion % → décimal

    db.close()
    return noms, rendements, volatilites, allocation_actuelle
def optimiser_markowitz(rendements, cov_matrix):
    n = len(rendements)
    def portefeuillerendement(w):
        return np.dot(w, rendements)
    def portefeuille_variance(w):
        return w.T @ cov_matrix @ w
    constraints = ({'type':'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0,1)] * n
    rendement_cible = np.mean(rendements)
    def objectif(w):
        penalty = 1000 * max(0, rendement_cible - portefeuillerendement(w))**2
        return portefeuille_variance(w) + penalty
    w0 = np.array([1/n]*n)
    result = minimize(objectif, w0, bounds=bounds, constraints=constraints)
    if not result.success:
        raise Exception("Optimisation échouée")
    return result.x
def validate_covariance_matrix(matrix: list[list[float]], n: int):
    if len(matrix) != n:
        raise HTTPException(status_code=400, detail="La taille de la matrice doit correspondre au nombre d'actifs")

    for i, row in enumerate(matrix):
        if len(row) != n:
            raise HTTPException(status_code=400, detail="Matrice non carrée")
        for j, value in enumerate(row):
            if not -1 <= value <= 1:
                raise HTTPException(status_code=400, detail=f"Valeur de corrélation invalide ({value}) à la position [{i},{j}] (doit être entre -1 et 1)")
            if i == j and value != 1.0:
                raise HTTPException(status_code=400, detail=f"La diagonale doit être égale à 1 à la position [{i},{j}]")
            if i > j and matrix[i][j] != matrix[j][i]:
                raise HTTPException(status_code=400, detail=f"La matrice doit être symétrique : élément [{i},{j}] ≠ [{j},{i}]")
@router.get("/portefeuilles")
def get_portefeuilles():
    db: Session = SessionLocal()
    portefeuilles = db.query(Portefeuille).all()
    result = [{"id": p.id, "nom": p.nom} for p in portefeuilles]
    db.close()
    return result

@router.get("/portefeuilles/{portefeuille_id}/actifs")
def get_actifs(portefeuille_id: int):
    db: Session = SessionLocal()
    portefeuille = db.query(Portefeuille).filter(Portefeuille.id == portefeuille_id).first()
    if not portefeuille:
        db.close()
        raise HTTPException(status_code=404, detail="Portefeuille non trouvé")
    actifs = portefeuille.actifs
    result = [{
        "id": a.id,
        "nom": a.nom,
        "rendement": a.rendement,
        "volatilite": a.volatilite,
        "pourcentage": a.pourcentage
    } for a in actifs]
    db.close()
    return result
@router.post("/optimiser-portefeuille", response_model=OptimisationResponse)
def optimiser_portefeuille(req: OptimisationRequest):
    noms, rendements, volatilites, allocation_actuelle = get_portefeuille_data(req.portefeuille_id)
    n = len(noms)
    
    # Validation complète de la matrice (taille, symétrie, valeurs, diagonale)
    validate_covariance_matrix(req.covariance_matrix, n)
    
    # Conversion matrice corrélation -> covariance (avec volatilités)
    D = np.diag(volatilites)
    corr_matrix = np.array(req.covariance_matrix)
    cov_matrix = D @ corr_matrix @ D
    
    allocation_optimisee = optimiser_markowitz(rendements, cov_matrix).tolist()

    # Calcul frontière efficiente
    rendements_frontiere = np.linspace(min(rendements), max(rendements), 10)
    frontiere = []
    for r_target in rendements_frontiere:
        def obj(w):
            return w.T @ cov_matrix @ w
        cons = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: np.dot(w, rendements) - r_target}
        )
        bounds = [(0, 1)] * n
        w0 = np.ones(n) / n
        res = minimize(obj, w0, bounds=bounds, constraints=cons)
        if res.success:
            risque = float(np.sqrt(res.fun))
            frontiere.append({"rendement": r_target, "risque": risque})

    message = (
        "Nous avons ajusté vos allocations pour réduire le risque tout en maintenant un rendement attendu similaire. "
        "Cela signifie que votre argent travaille plus efficacement avec une meilleure stabilité."
    )

    return {
        "allocation_actuelle": allocation_actuelle,
        "allocation_optimisee": allocation_optimisee,
        "message": message,
        "frontiere": frontiere
    }
