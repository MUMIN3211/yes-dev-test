from fastapi import APIRouter, Depends, File, Form, UploadFile
from supabase import Client

from app.core.deps import get_current_admin
from app.db.supabase import get_supabase
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ImportResult
from app.services.product_import import MAX_FILE_BYTES, ProductImportService

# Admin and Super Admin can both manage products
router = APIRouter(prefix="/api/admin/products", tags=["admin-products"], dependencies=[Depends(get_current_admin)])


def get_import_service(client: Client = Depends(get_supabase)) -> ProductImportService:
    return ProductImportService(ProductRepository(client))


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

