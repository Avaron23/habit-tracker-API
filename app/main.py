from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.habit import router as habit_router


app = FastAPI()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(habit_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Hello world!!!"
    }