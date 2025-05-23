from fastapi import APIRouter,  Depends
from pydantic import BaseModel
from typing import List
import numpy as np
from scipy.optimize import minimize
from schemas import DraftInput 
from models import DraftModel  
from sqlalchemy.orm import Session
from database import get_db


router = APIRouter()

class OptimisationInput(BaseModel):
    expected_returns: List[float]
    cov_matrix: List[List[float]]
    target_return: float
    current_weights: List[float]  # Ajout pour comparaison
class ApplyOptimizationPayload(BaseModel):
     optimal_weights: List[float]

@router.post("/efficient-frontier")
def efficient_frontier(data: OptimisationInput):
    mu = np.array(data.expected_returns)
    cov = np.array(data.cov_matrix)
    n = len(mu)

    def portfolio_variance(w):
        return w.T @ cov @ w

    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'eq', 'fun': lambda w: w @ mu - data.target_return}
    ]

    bounds = [(0, 1)] * n
    initial_weights = np.ones(n) / n

    result = minimize(portfolio_variance, initial_weights, bounds=bounds, constraints=constraints)

    if not result.success:
        return {"error": "Optimisation échouée."}

    optimal_weights = result.x
    optimal_return = optimal_weights @ mu
    optimal_variance = result.fun
    optimal_std_dev = np.sqrt(optimal_variance)

    # Génération de la frontière efficiente (optionnel)
    risks = []
    returns = []

    target_returns = np.linspace(min(mu), max(mu), 30)
    for r in target_returns:
        cons = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: w @ mu - r}
        ]
        res = minimize(portfolio_variance, initial_weights, bounds=bounds, constraints=cons)
        if res.success:
            risks.append(np.sqrt(res.fun))
            returns.append(r)

    return {
        "current_weights": data.current_weights,
        "optimal_weights": optimal_weights.tolist(),
        "expected_return": float(optimal_return),
        "standard_deviation": float(optimal_std_dev),
        "risks": risks,
        "returns": returns,
        "message": "Nous avons ajusté vos allocations pour réduire le risque tout en maintenant un rendement attendu similaire. Cela signifie que votre argent travaille plus efficacement avec une meilleure stabilité."
    }
@router.post("/apply-optimization")
def apply_optimization(payload: ApplyOptimizationPayload):
    print("Poids optimisés reçus :", payload.optimal_weights)
    # Logique pour mettre à jour le portefeuille ici
    return {"message": "Optimisation appliquée"}
@router.post("/save-draft")
def save_draft(data: DraftInput, db: Session = Depends(get_db)):
    new_draft = DraftModel(
        name=data.draft_name,
        expected_returns=data.expected_returns,
        cov_matrix=data.cov_matrix,
        target_return=data.target_return,
        current_weights=data.current_weights,
        optimal_weights=data.optimal_weights
    )
    db.add(new_draft)
    db.commit()
    return {"message": "Brouillon sauvegardé avec succès"}