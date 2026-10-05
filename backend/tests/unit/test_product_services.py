"""Feature 1 (public products) and Feature 4 (admin product list / QR) services."""

import pytest
from fastapi import HTTPException

from app.repositories.product_repository import ProductRepository
from app.services.admin_product_service import AdminProductService
from app.services.product_service import ProductService

pytestmark = pytest.mark.unit


@pytest.fixture
def public(db) -> ProductService:
    return ProductService(ProductRepository(db))


@pytest.fixture
def admin(db) -> AdminProductService:
    return AdminProductService(ProductRepository(db))


@pytest.fixture
def catalog(db):
    db.add_product(sku="LS-0002", name="Hydrating Toner", category="Toner")
    db.add_product(sku="LS-0001", name="Gentle Foam Cleanser", category="Cleanser")
    db.add_product(sku="LS-0003", name="Vitamin C Serum", category="Serum")
    db.add_product(sku="LS-0004", name="Clay Mask", category="Mask", status="inactive")


# --- public (Feature 1) ---


def test_public_list_hides_inactive_and_is_sorted_by_sku(public, catalog):
    result = public.list_public(category=None, search=None)
    assert [p.sku for p in result.items] == ["LS-0001", "LS-0002", "LS-0003"]
    assert result.total == 3


def test_public_list_filters_by_category(public, catalog):
    assert [p.sku for p in public.list_public(category="Toner", search=None).items] == ["LS-0002"]


@pytest.mark.parametrize("term, expected", [("serum", ["LS-0003"]), ("ls-0002", ["LS-0002"]), ("zzz", []), ("clay", [])])
def test_public_search_matches_name_or_sku_case_insensitively(public, catalog, term, expected):
    assert [p.sku for p in public.list_public(category=None, search=term).items] == expected


def test_search_cannot_inject_extra_filter_conditions(public, catalog):
    # Without stripping ",()%" this would add "sku.ilike.%" and match every product
    assert public.list_public(category=None, search="zzz,sku.ilike.%").items == []
    # A term made only of filter characters is treated as no search at all
    assert public.list_public(category=None, search="%,()").total == 3


def test_public_product_never_exposes_status_or_internal_fields(public, catalog):
    product = public.get_public("LS-0001").model_dump()
    assert "status" not in product and "id" not in product and "updated_at" not in product


def test_public_detail_accepts_lowercase_and_spaces(public, catalog):
    assert public.get_public("  ls-0001 ").sku == "LS-0001"


@pytest.mark.parametrize("sku", ["LS-0004", "LS-9999"])
def test_inactive_and_unknown_products_are_404(public, catalog, sku):
    with pytest.raises(HTTPException) as exc:
        public.get_public(sku)
    assert exc.value.status_code == 404


def test_public_qr_only_for_active_products(public, catalog):
    assert public.get_public_qr("ls-0001", "svg", 4).startswith(b"<?xml")
    with pytest.raises(HTTPException):
        public.get_public_qr("LS-0004", "svg", 4)


# --- admin (Feature 4) ---


def test_admin_list_includes_inactive_with_qr_url(admin, catalog):
    result = admin.list_all()
    assert result.total == 4
    by_sku = {p.sku: p for p in result.items}
    assert by_sku["LS-0004"].status == "inactive"
    assert by_sku["LS-0001"].qr_url == "http://frontend.test/products/LS-0001?src=qr"


def test_admin_qr_works_for_inactive_products(admin, catalog):
    assert admin.qr_image("LS-0004", "png", 4).startswith(b"\x89PNG")


def test_admin_qr_normalizes_sku(admin, catalog):
    assert admin.qr_image(" ls-0001 ", "png", 4) == admin.qr_image("LS-0001", "png", 4)


def test_admin_qr_for_unknown_product_is_404(admin, catalog):
    with pytest.raises(HTTPException) as exc:
        admin.qr_image("LS-9999", "png", 4)
    assert exc.value.status_code == 404
