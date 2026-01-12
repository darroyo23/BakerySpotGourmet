"""
Order API Endpoints.
"""
from typing import Annotated, Any, Optional
import structlog

from fastapi import APIRouter, Depends, Request, status

from bakerySpotGourmet.api.v1 import dependencies as deps
from bakerySpotGourmet.domain.users.entities import UserIdentity
from bakerySpotGourmet.schemas.order import OrderCreate, OrderResponse
from bakerySpotGourmet.services.order_service import OrderService
from bakerySpotGourmet.utils.idempotency import require_idempotency_key, get_idempotency_store


logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: Annotated[UserIdentity, Depends(deps.get_current_user)],
    order_service: Annotated[OrderService, Depends(deps.get_order_service)],
    _: Annotated[None, Depends(deps.rate_limit_dependency("orders"))] = None,
    idempotency_key: str = Depends(require_idempotency_key),
) -> Any:
    """
    Create a new order.
    
    Requires an Idempotency-Key header to prevent duplicate orders.
    """
    # Check idempotency store
    idempotency_store = get_idempotency_store()
    cached_response = idempotency_store.get(idempotency_key)
    
    if cached_response:
        logger.info(
            "idempotent_request_cached",
            idempotency_key=idempotency_key,
            user_id=current_user.id,
        )
        return cached_response
    
    # Create new order
    logger.info(
        "creating_order",
        user_id=current_user.id,
        items_count=len(order_in.items),
        order_type=order_in.order_type.value
    )
    
    order = order_service.create_order(
        customer_id=current_user.id, 
        order_in=order_in,
        order_type=order_in.order_type
    )
    
    # Convert to response model
    response_data = OrderResponse.model_validate(order)
    
    # Store in idempotency cache
    idempotency_store.set(idempotency_key, response_data.model_dump())
    
    logger.info(
        "order_created",
        order_id=order.id,
        user_id=current_user.id,
        status=order.status.value,
        payment_status=order.payment_status.value
    )
    
    return response_data
