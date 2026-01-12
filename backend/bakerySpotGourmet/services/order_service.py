"""
Order service layer.
Orchestrates order operations and enforces business rules.
"""
from typing import List, Optional
import structlog
from fastapi import HTTPException

from bakerySpotGourmet.core.exceptions import EntityNotFoundException
from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.order_type import OrderType
from bakerySpotGourmet.domain.orders.exceptions import InvalidOrderStatusTransitionException
from bakerySpotGourmet.repositories.item_repository import ItemRepository
from bakerySpotGourmet.repositories.order_repository import OrderRepository
from bakerySpotGourmet.repositories.payment_repository import PaymentRepository
from bakerySpotGourmet.schemas.order import OrderCreate


logger = structlog.get_logger()


class OrderService:
    """Service for order operations."""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_repository: "PaymentRepository",
        item_repository: ItemRepository
    ):
        self.order_repository = order_repository
        self.payment_repository = payment_repository
        self.item_repository = item_repository

    def create_order(
        self, 
        customer_id: int, 
        order_in: OrderCreate, 
        order_type: OrderType = OrderType.PICKUP
    ) -> Order:
        """
        Create a new order.
        Validates products, creates domain entity, and saves it.
        
        Args:
            customer_id: ID of the customer creating the order
            order_in: Order creation data
            order_type: Type of fulfillment (PICKUP or DELIVERY)
            
        Returns:
            The created order
            
        Raises:
            HTTPException: If product not found or inactive
        """
        # 1. Create Order Aggregate
        order = Order(customer_id=customer_id, order_type=order_type)
        
        # 2. Add items to order (validating each)
        for item_in in order_in.items:
            product = self.item_repository.get_by_id(item_in.product_id)
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item_in.product_id} not found")
            if not product.is_active:
                raise HTTPException(status_code=400, detail=f"Product {item_in.product_id} is not active")
            
            order.add_item(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=item_in.quantity
            )
            
        # 3. Persist (should be transactional)
        saved_order = self.order_repository.save(order)
        
        logger.info(
            "order_created",
            order_id=saved_order.id,
            customer_id=customer_id,
            total_amount=saved_order.total_amount,
            order_type=order_type.value
        )
        
        return saved_order
    
    def attach_payment(self, order_id: int, payment_id: int) -> Order:
        """
        Associate a payment status with an order.
        Operational transitions remain unblocked by payment.
        """
        order = self.get_order_by_id(order_id)
        # In a real system, we'd fetch the payment to verify amount/etc.
        # For now, we update the informational payment_status on the order aggregate.
        # This demonstrates the association without logic coupling.
        
        # Simulating fetching payment status from PaymentService/Repo
        from bakerySpotGourmet.repositories.payment_repository import PaymentRepository
        # Assuming we can get the status from the repository
        # (This is just for demonstration of association)
        # In a multi-service setup, this might be via events or a read model.
        
        # For the sake of this task, we'll just update it to COMPLETED as an example
        from bakerySpotGourmet.domain.payments.status import PaymentStatus
        order.payment_status = PaymentStatus.COMPLETED
        
        updated_order = self.order_repository.update(order)
        
        logger.info(
            "order_payment_attached",
            order_id=order_id,
            payment_id=payment_id,
            payment_status=order.payment_status.value
        )
        return updated_order
    
    # Admin operations
    
    def list_orders(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[OrderStatus] = None
    ) -> List[Order]:
        """
        List orders with optional filtering and pagination.
        
        Args:
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            status_filter: Optional status filter
            
        Returns:
            List of orders
        """
        return self.order_repository.get_all(skip=skip, limit=limit, status=status_filter)
    
    def get_order_by_id(self, order_id: int) -> Order:
        """
        Retrieve a single order by ID.
        
        Args:
            order_id: The order ID
            
        Returns:
            The order
            
        Raises:
            EntityNotFoundException: If order not found
        """
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundException("Order", str(order_id))
        return order
    
    def update_order_status(
        self, 
        order_id: int, 
        new_status: OrderStatus, 
        admin_user_id: int
    ) -> Order:
        """
        Update order status with validation and audit logging.
        
        Args:
            order_id: The order ID
            new_status: The new status to transition to
            admin_user_id: ID of the admin user performing the action
            
        Returns:
            The updated order
            
        Raises:
            EntityNotFoundException: If order not found
            InvalidOrderStatusTransitionException: If transition is invalid
        """
        # Retrieve order
        order = self.get_order_by_id(order_id)
        
        old_status = order.status
        
        # Validate and apply transition (domain enforces rules)
        order.change_status(new_status)
        
        # Persist
        updated_order = self.order_repository.update(order)
        
        # Audit log
        logger.info(
            "order_status_updated",
            order_id=order_id,
            old_status=old_status.value,
            new_status=new_status.value,
            admin_user_id=admin_user_id,
        )
        
        return updated_order
