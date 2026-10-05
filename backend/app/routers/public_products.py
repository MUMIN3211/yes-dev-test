from fastapi import APIRouter, Depends, Query, Response
from supabase import Client

from app.db.supabase import get_supabase
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Category, PublicProduct, PublicProductList
from app.services.product_service import ProductService
from app.services.qr_service import MEDIA_TYPES, QrFormat

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


@router.get("/{sku}/qr", response_class=Response, responses={200: {"content": {"image/svg+xml": {}, "image/png": {}}}})
def get_product_qr(
    sku: str,
    format: QrFormat = "svg",
    scale: int = Query(4, ge=1, le=20, description="Pixels per QR module"),
    service: ProductService = Depends(get_product_service),
):
    """QR of an active product, shown on the landing page cards. It encodes only the
    product's public URL, so it is safe to serve without login."""
    return Response(
        service.get_public_qr(sku, format, scale),
        media_type=MEDIA_TYPES[format],
        headers={"Cache-Control": "public, max-age=3600"},
    )
