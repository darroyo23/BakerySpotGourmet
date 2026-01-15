from uuid import uuid4
import pytest
from bakerySpotGourmet.domain.catalog.product import Product
from bakerySpotGourmet.domain.catalog.category import Category

def test_product_margin_calculation():
    product = Product(
        id=uuid4(),
        category_id=uuid4(),
        name="Bread",
        cost_price=5.0,
        sale_price=10.0
    )
    assert product.margin_percentage() == 0.5

def test_product_margin_zero_price():
    product = Product(
        id=uuid4(),
        category_id=uuid4(),
        name="Free Sample",
        cost_price=5.0,
        sale_price=0.0
    )
    assert product.margin_percentage() == 0.0

def test_category_creation():
    id_ = uuid4()
    category = Category(id=id_, name="Bakery")
    assert category.id == id_
    assert category.name == "Bakery"
    assert category.is_active is True
