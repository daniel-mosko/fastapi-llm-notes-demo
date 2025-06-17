from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db.database import Base, SessionLocal, engine
from services.notes import router as basics_router

app = FastAPI()

app.include_router(basics_router, prefix="/basics", tags=["Basics"])

# Initialize DB schema
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root(db: Session = Depends(get_db)):  # dependency injection
    return {"message": "Connected to PostgreSQL"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
