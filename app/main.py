from fastapi import FastAPI
from app.api.auth import router as auth_router


app = FastAPI()


app.include_router(auth_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Hello world!!!"
    }