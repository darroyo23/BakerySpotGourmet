"""
Admin API endpoints for order management.
Requires ADMIN or STAFF role.
"""
from typing import Annotated, Any, Optional, List
import structlog

from fastapi import APIRouter, Depends, HTTPException, Query, status

from bakerySpotGourmet.api.v1 import dependencies as deps
from bakerySpotGourmet.core.exceptions import EntityNotFoundException
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.exceptions import InvalidOrderStatusTransitionException
from bakerySpotGourmet.schemas.order import OrderResponse, OrderStatusUpdate
from bakerySpotGourmet.services.order_service import OrderService


logger = structlog.get_logger()
router = APIRouter()


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    current_user: Annotated[UserIdentity, Depends(deps.RoleChecker([Role.ADMIN, Role.STAFF]))],
    order_service: Annotated[OrderService, Depends(deps.get_order_service)],
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
) -> Any:
    """
    List all orders with optional filtering and pagination.
    
    Requires ADMIN or STAFF role.
    """
    logger.info(
        "admin_list_orders",
        admin_user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status.value if status else None,
    )
    
    orders = order_service.list_orders(skip=skip, limit=limit, status_filter=status)
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: Annotated[UserIdentity, Depends(deps.RoleChecker([Role.ADMIN, Role.STAFF]))],
    order_service: Annotated[OrderService, Depends(deps.get_order_service)],
) -> Any:
    """
    Retrieve a single order by ID.
    
    Requires ADMIN or STAFF role.
    """
    logger.info(
        "admin_get_order",
        admin_user_id=current_user.id,
        order_id=order_id,
    )
    
    order = order_service.get_order_by_id(order_id)
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: Annotated[UserIdentity, Depends(deps.RoleChecker([Role.ADMIN, Role.STAFF]))],
    order_service: Annotated[OrderService, Depends(deps.get_order_service)],
) -> Any:
    """
    Update order status.
    
    ADMIN can perform all transitions.
    STAFF can perform all transitions except to CANCELLED.
    
    Raises:
        403: If STAFF user attempts to cancel an order
        400: If status transition is invalid
        404: If order not found
    """
    # Check if STAFF is trying to cancel
    if current_user.role == Role.STAFF and status_update.status == OrderStatus.CANCELLED:
        logger.warning(
            "staff_cancel_attempt_denied",
            admin_user_id=current_user.id,
            order_id=order_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="STAFF users cannot cancel orders. Only ADMIN can cancel."
        )
    
    logger.info(
        "admin_update_order_status_attempt",
        admin_user_id=current_user.id,
        admin_role=current_user.role.value,
        order_id=order_id,
        new_status=status_update.status.value,
    )
    
    try:
        updated_order = order_service.update_order_status(
            order_id=order_id,
            new_status=status_update.status,
            admin_user_id=current_user.id
        )
        return updated_order
    except InvalidOrderStatusTransitionException as e:
        logger.warning(
            "invalid_status_transition",
            admin_user_id=current_user.id,
            order_id=order_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
