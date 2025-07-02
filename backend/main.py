from backend.api.main import api_router
from backend.config import api_version
from backend.db.database import Base, engine
from fastapi import FastAPI

app = FastAPI()

app.include_router(api_router, prefix=f"/api/{api_version}")

# Initialize DB schema
Base.metadata.create_all(bind=engine)


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
