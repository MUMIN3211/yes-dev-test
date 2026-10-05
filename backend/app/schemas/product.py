from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

Category = Literal["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen", "Mask"]


class PublicProduct(BaseModel):
    """Fields that are safe to show on the public pages (no internal ids/status)."""

    sku: str
    name: str
    category: Category
    price: float
    size: str | None = None
    description: str | None = None
    how_to_use: str | None = None
    image_url: str | None = None


class PublicProductList(BaseModel):
    items: list[PublicProduct]
    total: int


ProductStatus = Literal["active", "inactive"]


class AdminProduct(PublicProduct):
    """Back-office view: every product (inactive too) plus the URL its QR code encodes."""

    status: ProductStatus
    updated_at: datetime
    qr_url: str


class AdminProductList(BaseModel):
    items: list[AdminProduct]
    total: int


# --- Excel import (Feature 3) ---------------------------------------------------

ImportAction = Literal["create", "update", "unchanged"]


class FieldChange(BaseModel):
    field: str
    old: Any = None
    new: Any = None


class ImportRow(BaseModel):
    """A valid row and what importing it does to the database."""

    row: int
    sku: str
    name: str
    action: ImportAction
    changes: list[FieldChange] = []


class ImportIssue(BaseModel):
    """`row` is the Excel row number (the header is row 1)."""

    row: int
    sku: str | None = None
    messages: list[str]


class ImportResult(BaseModel):
    dry_run: bool
    file_name: str
    total_rows: int
    created: int
    updated: int
    unchanged: int
    failed: int
    rows: list[ImportRow]
    errors: list[ImportIssue]
    warnings: list[ImportIssue]
