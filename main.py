from fastapi import FastAPI

import models
from routes.users import router as users_router
from routes.auth import router as auth_router
from routes.products import router as products_router

from fastapi.middleware.cors import CORSMiddleware  

from database import create_tables

create_tables()  # Create tables at startup (for development; consider migrations for production)
app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(products_router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}