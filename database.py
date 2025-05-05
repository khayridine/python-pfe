
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
 

DATABASE_URL = "postgresql://postgres:12345@localhost:8080/Pfedb"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Pas de create_all ici ! (à déplacer dans `create_tables.py`)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
