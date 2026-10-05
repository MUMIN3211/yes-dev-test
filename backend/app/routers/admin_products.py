from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from supabase import Client

from app.core.deps import get_current_admin
from app.db.supabase import get_supabase
from app.repositories.product_repository import ProductRepository
from app.schemas.product import AdminProductList, ImportResult
from app.services.admin_product_service import AdminProductService
from app.services.product_import import MAX_FILE_BYTES, ProductImportService
from app.services.qr_service import MEDIA_TYPES, QrFormat

# Admin and Super Admin can both manage products
router = APIRouter(prefix="/api/admin/products", tags=["admin-products"], dependencies=[Depends(get_current_admin)])


def get_admin_product_service(client: Client = Depends(get_supabase)) -> AdminProductService:
    return AdminProductService(ProductRepository(client))


def get_import_service(client: Client = Depends(get_supabase)) -> ProductImportService:
    return ProductImportService(ProductRepository(client))


@router.get("", response_model=AdminProductList)
def list_products(service: AdminProductService = Depends(get_admin_product_service)):
    """Every product, including inactive ones."""
    return service.list_all()


@router.post("/import", response_model=ImportResult)
async def import_products(
    file: UploadFile = File(..., description="Excel file (.xlsx); the first row is the header"),
    dry_run: bool = Form(True, description="true = validate and preview only, nothing is saved"),
    service: ProductImportService = Depends(get_import_service),
):
    """Validates every row and upserts the valid ones by SKU. Invalid rows are
    skipped and reported with their Excel row number."""
    # Read one byte past the limit so oversized files are rejected without loading them whole
    content = await file.read(MAX_FILE_BYTES + 1)
    return service.run(file.filename or "", content, dry_run)


@router.get("/{sku}/qr", response_class=Response, responses={200: {"content": {"image/png": {}, "image/svg+xml": {}}}})
def product_qr(
    sku: str,
    format: QrFormat = "png",
    scale: int = Query(10, ge=1, le=40, description="Pixels per QR module"),
    service: AdminProductService = Depends(get_admin_product_service),
):
    """QR code image that opens the product's public page."""
    return Response(service.qr_image(sku, format, scale), media_type=MEDIA_TYPES[format])
