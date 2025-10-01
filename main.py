import uvicorn
from fastapi import FastAPI
from app.api.authentication import router as auth_router


app = FastAPI(title="IntelliGrid")

app.include_router(auth_router, prefix="/intelligrid")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
