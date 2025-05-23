from pydantic import BaseModel
from typing import List, Optional

class ActifCreate(BaseModel):
    nom: str
    categorie: Optional[str]
    type: Optional[str]
    pourcentage: float
    rendement: float
    volatilite: float

class PortefeuilleCreate(BaseModel):
    montant_total: float
    actifs: List[ActifCreate]

class DraftInput(BaseModel):
    draft_name: str
    expected_returns: List[float]
    cov_matrix: List[List[float]]
    target_return: float
    current_weights: List[float]
    optimal_weights: List[float]
