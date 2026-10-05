"""QR codes (Feature 4).

A product's QR only encodes the URL of its public page, which is built from the
SKU. Nothing about it is stored: every product has a QR as soon as it exists,
and editing or re-importing the product never changes what a printed QR opens.
"""

from io import BytesIO
from typing import Literal
from urllib.parse import quote

import segno

from app.core.config import get_settings

QrFormat = Literal["png", "svg"]

MEDIA_TYPES = {"png": "image/png", "svg": "image/svg+xml"}

# `src=qr` tells the product page the visit came from a scan (for the scan log, Feature 10)
QR_SOURCE_PARAM = "src=qr"


def product_qr_url(sku: str) -> str:
    return f"{get_settings().public_site_url}/products/{quote(sku)}?{QR_SOURCE_PARAM}"


def render_qr(sku: str, fmt: QrFormat = "png", scale: int = 10) -> bytes:
    """`scale` = pixels per QR module. Error correction "M" survives small print damage."""
    qr = segno.make_qr(product_qr_url(sku), error="m")
    buffer = BytesIO()
    qr.save(buffer, kind=fmt, scale=scale, border=4)
    return buffer.getvalue()
