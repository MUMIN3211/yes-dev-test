from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.db.supabase import get_supabase
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Category, PublicProduct, PublicProductList
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/public/products", tags=["public-products"])


def get_product_service(client: Client = Depends(get_supabase)) -> ProductService:
    return ProductService(ProductRepository(client))


@router.get("", response_model=PublicProductList)
def list_products(
    category: Category | None = None,
    q: str | None = Query(default=None, max_length=100),
    service: ProductService = Depends(get_product_service),
):
    """Active products for the public landing page."""
    return service.list_public(category=category, search=q)


@router.get("/{sku}", response_model=PublicProduct)
def get_product(sku: str, service: ProductService = Depends(get_product_service)):
    """Single active product — this is what a scanned QR code resolves to."""
    return service.get_public(sku)
