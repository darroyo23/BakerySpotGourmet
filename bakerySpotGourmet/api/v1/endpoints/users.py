"""
User API Endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """
    List users endpoint placeholder.
    """
    return {"message": "Users endpoint"}
