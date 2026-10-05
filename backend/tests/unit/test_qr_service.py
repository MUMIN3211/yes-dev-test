"""Feature 4: what a QR code points to, and the image it renders."""

from io import BytesIO

import pytest
import segno

from app.core.config import get_settings
from app.services.qr_service import product_qr_url, render_qr

pytestmark = pytest.mark.unit

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def expected_png(url: str, scale: int = 10) -> bytes:
    buffer = BytesIO()
    segno.make_qr(url, error="m").save(buffer, kind="png", scale=scale, border=4)
    return buffer.getvalue()


def png_size(data: bytes) -> tuple[int, int]:
    # Width and height are the first two fields of the IHDR chunk
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def use_settings(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def test_qr_points_to_the_public_product_page_marked_as_a_scan():
    assert product_qr_url("LS-1001") == "http://frontend.test/products/LS-1001?src=qr"


def test_qr_base_url_overrides_frontend_url(monkeypatch):
    use_settings(monkeypatch, QR_BASE_URL="http://192.168.1.10:3000/")
    assert product_qr_url("LS-1001") == "http://192.168.1.10:3000/products/LS-1001?src=qr"


def test_empty_qr_base_url_falls_back_to_frontend_url(monkeypatch):
    use_settings(monkeypatch, QR_BASE_URL="", FRONTEND_URL="https://luma.example/")
    assert product_qr_url("LS-1001") == "https://luma.example/products/LS-1001?src=qr"


def test_sku_is_url_encoded():
    assert product_qr_url("LS 1/1").endswith("/products/LS%201/1?src=qr")


def test_png_encodes_exactly_the_product_url():
    data = render_qr("LS-1001")
    assert data.startswith(PNG_SIGNATURE)
    assert data == expected_png("http://frontend.test/products/LS-1001?src=qr")


def test_same_sku_always_gives_the_same_qr():
    # A printed QR must keep matching what the system shows later
    assert render_qr("LS-1001") == render_qr("LS-1001")
    assert render_qr("LS-1001") != render_qr("LS-1002")


def test_scale_sets_pixels_per_module():
    small_w, small_h = png_size(render_qr("LS-1001", "png", 2))
    big_w, big_h = png_size(render_qr("LS-1001", "png", 10))
    assert small_w == small_h and big_w == big_h  # square
    assert big_w == small_w * 5


def test_svg_output():
    data = render_qr("LS-1001", "svg", 4)
    assert b"<svg" in data
    assert data.rstrip().endswith(b"</svg>")
