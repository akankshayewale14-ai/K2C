from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, business, collectors, offers, pickups, prices, recyclers, scrap, traceability
from app.core.config import get_settings
from app.db.base import Base  # noqa: F401
from app.db.seed import seed
from app.db.session import SessionLocal, engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="KABADIWALA2CONNECT API",
        description="Satara-first circular recycling marketplace. Demo data is labeled DEMO. Live prices require a configured provider.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    app.include_router(auth.router)
    app.include_router(prices.router)
    app.include_router(scrap.router)
    app.include_router(offers.router)
    app.include_router(pickups.router)
    app.include_router(collectors.router)
    app.include_router(recyclers.router)
    app.include_router(traceability.router)
    app.include_router(business.router)
    app.include_router(admin.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
