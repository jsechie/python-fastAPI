from fastapi import FastAPI
from . import models, cors
from .database import engine
from .routers import posts, users, auth, votes
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def check_api_status():
    return {"message": "API is up and running"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(votes.router)