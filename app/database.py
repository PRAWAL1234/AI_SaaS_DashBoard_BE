from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Fix common URL prefix issues (e.g. Render's postgres:// or accidental postgresql+postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql+postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():

    with Session(engine) as session:
        yield session