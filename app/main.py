from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine,Base
from app.routers import auth,habits,todos
from app.config import get_settings

settings=get_settings()


Base.metadata.create_all(bind=engine)


app=FastAPI(
    title=settings.app_name,
    description="A habit tracker app",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(todos.router)


@app.get("/")
async def root():
    return {"message": "welcome to Todo Habit Tracker",
            'docs': '/docs',
            'version': '0.0.1'}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)