from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

# Corrected imports: Pydantic models from schemas.py
from .database import SessionLocal, engine, Base as DBBase, create_db_and_tables, Note as DBNote
from . import crud
from . import schemas # Import schemas.py
from .config import OPENAI_API_KEY, CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME

# --- Initialize ChromaDB ---
import chromadb
try:
    # Path for ChromaDB should be accessible by the process.
    # If running uvicorn from /app/MemoryVault/, then 'backend/chroma_data' is correct
    # relative to that launch directory.
    # However, main.py is in /app/MemoryVault/backend.
    # Let's use an absolute path structure or one clearly relative to main.py's location
    # For PersistentClient, the path is relative to where the Python script is run.
    # If uvicorn runs from /app/MemoryVault, path should be "backend/chroma_data"
    # If uvicorn runs from /app/MemoryVault/backend, path should be "chroma_data"
    # The config.py currently has "MemoryVault/backend/chroma_data", which assumes running from /app.
    # Let's adjust it for running from /app/MemoryVault (as established for uvicorn)
    
    # Correct path if uvicorn is run from /app/MemoryVault:
    chroma_client = chromadb.PersistentClient(path="backend/chroma_data") 
    # Or use the one from config if it's set up to be relative to /app
    # chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY.replace("MemoryVault/", ""))


    print(f"Attempting to use ChromaDB persistent directory: backend/chroma_data")
    
    note_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    print(f"ChromaDB collection '{CHROMA_COLLECTION_NAME}' loaded/created successfully.")
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    note_collection = None # Ensure it's defined even on failure

# --- Configure OpenAI ---
import openai
if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
    openai.api_key = OPENAI_API_KEY
    print("OpenAI API key configured.")
else:
    print("OpenAI API key not found or is a placeholder. Please configure it in config.py.")


# Call to create SQL database tables on startup
create_db_and_tables() 

app = FastAPI()

# --- Database Dependency (SQLAlchemy) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "MemoryVault API is running. Navigate to /docs for API documentation."}

@app.post("/add_note/", response_model=schemas.Note) # Use schemas.Note
def create_api_note(note: schemas.NoteCreate, db: Session = Depends(get_db)): # Use schemas.NoteCreate
    """
    Adds a new note to the MemoryVault.
    - **content**: The content of the note.
    """
    db_note = crud.create_note(db=db, note=note)
    # Future step: Add embedding of db_note.content to ChromaDB
    if note_collection is not None:
        try:
            # Example: Add to ChromaDB (needs actual embedding later)
            # For now, just storing the note ID and content as metadata.
            # Real implementation would require an embedding function.
            note_collection.add(
                documents=[db_note.content],
                metadatas=[{"sql_id": db_note.id, "timestamp": db_note.timestamp.isoformat()}],
                ids=[str(db_note.id)] # ChromaDB IDs must be strings
            )
            print(f"Note {db_note.id} content (placeholder) added to ChromaDB.")
        except Exception as e:
            print(f"Error adding note {db_note.id} to ChromaDB: {e}")
    return db_note

@app.get("/get_notes/", response_model=List[schemas.Note]) # Use List[schemas.Note]
def read_api_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of notes from the MemoryVault, sorted by newest first.
    - **skip**: Number of notes to skip from the beginning.
    - **limit**: Maximum number of notes to return.
    """
    notes = crud.get_notes(db, skip=skip, limit=limit)
    return notes
