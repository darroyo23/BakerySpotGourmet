from bakerySpotGourmet.api.v1.endpoints import health, users, items

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
