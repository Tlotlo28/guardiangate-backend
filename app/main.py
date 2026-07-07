from fastapi import FastAPI

from app.api import auth, pickups, notices, absences, learners, admin
from app.core.config import settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_TAGLINE,
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(pickups.router)
app.include_router(notices.router)
app.include_router(absences.router)
app.include_router(learners.router)
app.include_router(admin.router)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "brand_color": settings.BRAND_COLOR,
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}