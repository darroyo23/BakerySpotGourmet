class BakeryException(Exception):
    """Base exception for BakerySpotGourmet."""
    pass


class EntityNotFoundException(BakeryException):
    """Raised when an entity is not found in the database."""
    def __init__(self, entity: str, identifier: str):
        self.message = f"{entity} with id {identifier} not found"
        super().__init__(self.message)


class BusinessRuleException(BakeryException):
    """Raised when a business rule is violated."""
    def __init__(self, message: str):
        super().__init__(message)
