from fastapi import HTTPException, status

from app.repositories.product_repository import ProductRepository
from app.schemas.product import AdminProduct, AdminProductList
from app.services.qr_service import QrFormat, product_qr_url, render_qr


class AdminProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def list_all(self) -> AdminProductList:
        items = [AdminProduct(**row, qr_url=product_qr_url(row["sku"])) for row in self.repo.list_all()]
        return AdminProductList(items=items, total=len(items))

    def qr_image(self, sku: str, fmt: QrFormat, scale: int) -> bytes:
        sku = sku.strip().upper()
        # Inactive products get a QR too: it starts working once they are re-activated
        if self.repo.get_by_sku(sku) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบสินค้านี้")
        return render_qr(sku, fmt, scale)
