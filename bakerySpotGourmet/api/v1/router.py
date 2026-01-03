from fastapi import APIRouter
from bakerySpotGourmet.api.v1.endpoints import health, users, items, orders

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
