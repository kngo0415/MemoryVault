from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base # updated import for modern SQLAlchemy
import datetime

DATABASE_URL = "sqlite:///./notes.db"  # Will create notes.db in the same directory as main.py (backend directory)

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy model for the Note
class Note(Base): # Renamed from Notes to Note to match Pydantic model naming convention (singular)
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text) # Using Text for potentially longer notes
    timestamp = Column(DateTime, default=datetime.datetime.utcnow) # utcnow is generally preferred for server-side timestamps

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# Optional: Call it here to ensure tables are created when this module is loaded,
# or call it explicitly in main.py startup.
# For now, it's better to call it on app startup in main.py.
# create_db_and_tables()
