from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from user import router as user_router
from operation import router as operation_router
from calcul import router as calcul_router
from portefeuille import router as portefeuille_router





app = FastAPI()


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(operation_router)
app.include_router(calcul_router)

app.include_router(portefeuille_router, prefix="/portefeuille", tags=["Portefeuille"])




