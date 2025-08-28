from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite:///library.db"

# Engine & session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()
