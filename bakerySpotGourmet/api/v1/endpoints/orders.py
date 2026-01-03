"""
Order API Endpoints.
"""
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from bakerySpotGourmet.api.v1 import dependencies as deps
from bakerySpotGourmet.domain.users.entities import UserIdentity
from bakerySpotGourmet.schemas.order import OrderCreate, OrderResponse
from bakerySpotGourmet.services.order_service import OrderService

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_in: OrderCreate,
    current_user: Annotated[UserIdentity, Depends(deps.get_current_user)],
    order_service: Annotated[OrderService, Depends(deps.get_order_service)],
) -> Any:
    """
    Create a new order.
    """
    return order_service.create_order(current_user.id, order_in)
