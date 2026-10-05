"""Feature 3: ProductImportService decides create / update / unchanged and only writes what changed."""

import pytest
from fastapi import HTTPException

from app.repositories.product_repository import ProductRepository
from app.services.product_import import MAX_FILE_BYTES, ProductImportService
from tests.fakes import FakeSupabase, make_xlsx, valid_row

pytestmark = pytest.mark.unit


@pytest.fixture
def service(db: FakeSupabase) -> ProductImportService:
    return ProductImportService(ProductRepository(db))


def run(service, rows, dry_run=False, name="products.xlsx"):
    return service.run(name, make_xlsx(rows), dry_run)


def test_new_rows_are_created(service, db):
    result = run(service, [valid_row(sku="LS-2001"), valid_row(sku="LS-2002")])
    assert (result.created, result.updated, result.unchanged, result.failed) == (2, 0, 0, 0)
    assert [r.action for r in result.rows] == ["create", "create"]
    assert sorted(p["sku"] for p in db.tables["products"]) == ["LS-2001", "LS-2002"]


def test_dry_run_reports_the_same_but_writes_nothing(service, db):
    result = run(service, [valid_row(sku="LS-2001")], dry_run=True)
    assert result.dry_run is True
    assert result.created == 1
    assert db.tables["products"] == []
    assert db.writes("products") == []


def test_changed_fields_are_listed_as_old_and_new(service, db):
    db.add_product(sku="LS-2001", name="Serum A", category="Serum", price=390, size="30 ml",
                   description="desc", how_to_use="use", status="active")
    result = run(service, [valid_row(sku="LS-2001", price=420, status="inactive")])

    assert result.updated == 1
    changes = {c.field: (c.old, c.new) for c in result.rows[0].changes}
    assert changes == {"price": (390, 420.0), "status": ("active", "inactive")}
    stored = db.tables["products"][0]
    assert stored["price"] == 420.0 and stored["status"] == "inactive"


def test_identical_rows_are_unchanged_and_not_written(service, db):
    db.add_product(sku="LS-2001", name="Serum A", category="Serum", price=500.0, size="30 ml",
                   description="desc", how_to_use="use", status="active")
    result = run(service, [valid_row(sku="LS-2001", price=500)])
    assert result.unchanged == 1
    assert result.rows[0].changes == []
    assert db.writes("products") == []


def test_empty_excel_cell_and_null_in_database_count_as_equal(service, db):
    db.add_product(sku="LS-2001", name="Serum A", category="Serum", price=500, size=None,
                   description=None, how_to_use=None, status="active")
    result = run(service, [["LS-2001", "Serum A", "Serum", 500, "", None, "  ", None]])
    assert result.unchanged == 1


def test_reimport_keeps_the_product_image(service, db):
    db.add_product(sku="LS-2001", image_url="https://cdn.test/serum.png", price=390)
    run(service, [valid_row(sku="LS-2001", price=420)])
    assert db.tables["products"][0]["image_url"] == "https://cdn.test/serum.png"


def test_products_missing_from_the_file_are_left_alone(service, db):
    db.add_product(sku="LS-0001", name="Old product")
    run(service, [valid_row(sku="LS-2001")])
    assert {p["sku"] for p in db.tables["products"]} == {"LS-0001", "LS-2001"}
    assert next(p for p in db.tables["products"] if p["sku"] == "LS-0001")["name"] == "Old product"


def test_invalid_rows_are_reported_and_valid_rows_still_imported(service, db):
    result = run(service, [valid_row(sku="LS-2001"), valid_row(sku="LS-2002", price="abc")])
    assert (result.created, result.failed) == (1, 1)
    assert result.errors[0].row == 3
    assert result.errors[0].sku == "LS-2002"
    assert [p["sku"] for p in db.tables["products"]] == ["LS-2001"]


def test_warnings_are_only_listed_for_rows_without_errors(service):
    result = run(service, [valid_row(sku="ls-2001"), valid_row(sku="ls-2002", name=None)])
    assert [w.row for w in result.warnings] == [2]
    assert [e.row for e in result.errors] == [3]


def test_totals_match_the_rows(service):
    result = run(service, [valid_row(sku="LS-2001"), valid_row(sku=None), [None] * 8])
    assert result.total_rows == 2
    assert result.created + result.updated + result.unchanged + result.failed == result.total_rows


@pytest.mark.parametrize("name", ["products.csv", "products.xls", "products", "products.xlsx.exe"])
def test_only_xlsx_files_are_accepted(service, name):
    with pytest.raises(HTTPException) as exc:
        service.run(name, make_xlsx([valid_row()]), dry_run=True)
    assert exc.value.detail == "รองรับเฉพาะไฟล์ .xlsx"


def test_uppercase_extension_is_accepted(service):
    assert service.run("PRODUCTS.XLSX", make_xlsx([valid_row()]), dry_run=True).created == 1


def test_empty_file_is_rejected(service):
    with pytest.raises(HTTPException) as exc:
        service.run("products.xlsx", b"", dry_run=True)
    assert exc.value.detail == "ไฟล์ว่างเปล่า"


def test_file_over_5_mb_is_rejected(service):
    with pytest.raises(HTTPException) as exc:
        service.run("products.xlsx", b"x" * (MAX_FILE_BYTES + 1), dry_run=True)
    assert "ใหญ่เกิน 5 MB" in exc.value.detail


def test_customer_files_in_order(service, db, excel_file):
    first = service.run("luma_products.xlsx", excel_file("luma_products.xlsx"), dry_run=False)
    assert (first.created, first.updated, first.unchanged, first.failed) == (21, 0, 0, 9)

    again = service.run("luma_products.xlsx", excel_file("luma_products.xlsx"), dry_run=False)
    assert (again.created, again.updated, again.unchanged) == (0, 0, 21)

    update = service.run("luma_products_update.xlsx", excel_file("luma_products_update.xlsx"), dry_run=False)
    assert (update.created, update.updated, update.unchanged, update.failed) == (2, 3, 0, 1)
    by_sku = {r.sku: r for r in update.rows}
    assert {c.field for c in by_sku["LS-1001"].changes} == {"price", "description"}
    assert {c.field for c in by_sku["LS-1003"].changes} == {"size", "description"}
    assert [(c.field, c.old, c.new) for c in by_sku["LS-1010"].changes] == [("status", "active", "inactive")]
    assert {by_sku["LS-1031"].action, by_sku["LS-1032"].action} == {"create"}
    assert len(db.tables["products"]) == 23
