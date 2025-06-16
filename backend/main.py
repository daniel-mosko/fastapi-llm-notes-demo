from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db.database import Base, SessionLocal, engine

app = FastAPI()


# Initialize DB schema
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Connected to PostgreSQL"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
