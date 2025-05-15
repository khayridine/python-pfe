from fastapi import APIRouter
import numpy as np
from pydantic import BaseModel

router = APIRouter()

class PortfolioRequest(BaseModel):
    
    expected_returns: list[float]
    cov_matrix: list[list[float]]

@router.post("/efficient-frontier")
def efficient_frontier(req: PortfolioRequest):
    R = np.array(req.expected_returns)
    V = np.array(req.cov_matrix)
    V_inv = np.linalg.inv(V)
    I = np.ones(len(R))

    a = R @ V_inv @ R
    b = R @ V_inv @ I
    c = I @ V_inv @ I
    d = a * c - b ** 2

    returns = np.linspace(min(R), max(R), 100)
    variances = []
    for Rp in returns:
        var = (a - 2 * b * Rp + c * Rp ** 2) / d
        variances.append(var)

    std_devs = [np.sqrt(v) for v in variances]
    return {
        "returns": returns.tolist(),
        "risks": std_devs
    }
