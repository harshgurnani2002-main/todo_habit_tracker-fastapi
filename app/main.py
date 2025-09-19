from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine,Base
from app.routers import auth_router, todos_router, habits_router, dashboard_router, admin_router, pomodoro_router
from app.config import get_settings

settings=get_settings()


Base.metadata.create_all(bind=engine)


app=FastAPI(
    title=settings.app_name,
    description="A habit tracker app",
    version="0.0.1"
)

# Add CORS middleware - this should be before including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(habits_router)
app.include_router(todos_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(pomodoro_router)


@app.get("/")
async def root():
    return {"message": "welcome to Todo Habit Tracker",
            'docs': '/docs',
            'version': '00.1'}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)