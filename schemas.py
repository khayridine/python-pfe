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

class OptimisationRequest(BaseModel):
    portefeuille_id: int
    covariance_matrix: List[List[float]]

