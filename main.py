from fastapi import FastAPI

import models
from routes.users import router as users_router
from routes.auth import router as auth_router
from routes.products import router as products_router


app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(products_router)






@app.get("/")
async def root():
    return {"message": "Hello World"}