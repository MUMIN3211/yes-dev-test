from fastapi import HTTPException, status

from app.repositories.product_repository import ProductRepository
from app.schemas.product import PublicProduct, PublicProductList
from app.services.qr_service import QrFormat, render_qr


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def list_public(self, category: str | None, search: str | None) -> PublicProductList:
        rows = self.repo.list_active(category=category, search=search)
        items = [PublicProduct(**row) for row in rows]
        return PublicProductList(items=items, total=len(items))

    def get_public(self, sku: str) -> PublicProduct:
        row = self.repo.get_active_by_sku(sku.strip().upper())
        if row is None:
            # Inactive products are treated as not found on public pages
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return PublicProduct(**row)

    def get_public_qr(self, sku: str, fmt: QrFormat, scale: int) -> bytes:
        # get_public raises 404 for unknown and inactive products
        product = self.get_public(sku)
        return render_qr(product.sku, fmt, scale)
