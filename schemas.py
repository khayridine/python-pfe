from pydantic import BaseModel, Field
from typing import List, Optional

class ActifCreate(BaseModel):
    nom: str
    categorie: Optional[str]
    type: Optional[str]
    pourcentage: float
    rendement: float
    volatilite: float

class PortefeuilleCreate(BaseModel):
    nom: str = Field(..., min_length=1)
    montant_total: float
    actifs: List[ActifCreate]

class OptimisationRequest(BaseModel):
    portefeuille_id: int
    covariance_matrix: List[List[float]]

