from typing import Literal

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
