from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env Datei laden
load_dotenv()

# Datenbankverbindung aus .env laden
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine erstellen
engine = create_engine(DATABASE_URL)

# SessionLocal Klasse erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Klasse für Models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()