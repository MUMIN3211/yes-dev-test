from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import admin_products, admin_users, auth, public_products

settings = get_settings()

app = FastAPI(title="Luma Skin Care API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_products.router)
app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(admin_products.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
