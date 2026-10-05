"""Feature 3: row-by-row validation of the Excel file (parse_workbook, no database)."""

import pytest
from fastapi import HTTPException

from app.services.product_import import MAX_DATA_ROWS, parse_workbook
from tests.fakes import make_xlsx, valid_row

pytestmark = pytest.mark.unit


def parse_one(row: list) -> "object":
    rows = parse_workbook(make_xlsx([row]))
    assert len(rows) == 1
    return rows[0]


def test_valid_row_is_parsed_into_clean_data():
    row = parse_one(valid_row(sku="LS-2001", name="  Serum A  ", price=890))
    assert row.errors == []
    assert row.warnings == []
    assert row.row == 2  # Excel row number: header is row 1
    assert row.sku == "LS-2001"
    assert row.data == {
        "name": "Serum A",
        "category": "Serum",
        "price": 890.0,
        "size": "30 ml",
        "description": "desc",
        "how_to_use": "use",
        "status": "active",
    }


# --- sku ---


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_missing_sku_is_an_error(raw):
    assert parse_one(valid_row(sku=raw)).errors == ["ไม่มี SKU"]


@pytest.mark.parametrize("raw", ["LS-12", "LS-12345", "AB-1234", "LS1234", "LS-12a4", "1234"])
def test_sku_with_wrong_format_is_an_error(raw):
    row = parse_one(valid_row(sku=raw))
    assert len(row.errors) == 1
    assert "ไม่ตรงรูปแบบ LS-0000" in row.errors[0]


@pytest.mark.parametrize("raw", [" LS-1024 ", "ls-1030", "Ls-1030"])
def test_sku_spaces_and_case_are_fixed_with_a_warning(raw):
    row = parse_one(valid_row(sku=raw))
    assert row.errors == []
    assert row.sku == raw.strip().upper()
    assert len(row.warnings) == 1 and "ปรับ SKU" in row.warnings[0]


def test_duplicate_sku_keeps_first_row_and_rejects_later_ones():
    rows = parse_workbook(
        make_xlsx(
            [
                valid_row(sku="LS-1004", name="Calm Cica Toner"),
                valid_row(sku="LS-1005"),
                valid_row(sku="ls-1004", name="Calm Cica Toner Refill"),
            ]
        )
    )
    assert rows[0].errors == []
    assert rows[1].errors == []
    assert rows[2].errors == ["SKU LS-1004 ซ้ำกับแถวที่ 2 (ใช้ข้อมูลจากแถวที่ 2)"]


# --- name ---


@pytest.mark.parametrize("raw", [None, "", "  "])
def test_missing_name_is_an_error(raw):
    assert parse_one(valid_row(name=raw)).errors == ["ไม่มีชื่อสินค้า"]


def test_name_longer_than_200_characters_is_an_error():
    assert "ยาวเกิน 200" in parse_one(valid_row(name="x" * 201)).errors[0]


# --- category ---


def test_missing_category_is_an_error():
    assert parse_one(valid_row(category=None)).errors == ["ไม่มีหมวดหมู่ (category)"]


def test_unknown_category_is_an_error_listing_allowed_values():
    error = parse_one(valid_row(category="Lotion")).errors[0]
    assert '"Lotion"' in error
    for allowed in ("Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen", "Mask"):
        assert allowed in error


@pytest.mark.parametrize("raw", ["serum", "SERUM", " Serum "])
def test_category_is_case_insensitive(raw):
    row = parse_one(valid_row(category=raw))
    assert row.errors == []
    assert row.data["category"] == "Serum"


# --- price ---


@pytest.mark.parametrize("raw, expected", [(390, 390.0), (390.5, 390.5), (99.999, 100.0), ("590", 590.0)])
def test_numeric_prices_are_accepted(raw, expected):
    row = parse_one(valid_row(price=raw))
    assert row.errors == []
    assert row.data["price"] == expected


@pytest.mark.parametrize("raw, expected", [("1,290", 1290.0), ("฿590", 590.0), ("590 บาท", 590.0), (" 1,290.50 ", 1290.5)])
def test_price_text_with_separators_is_converted_with_a_warning(raw, expected):
    row = parse_one(valid_row(price=raw))
    assert row.errors == []
    assert row.data["price"] == expected
    assert any("แปลงราคา" in w for w in row.warnings)


@pytest.mark.parametrize("raw", [0, -350, "0", "-1"])
def test_price_must_be_greater_than_zero(raw):
    assert "ราคาต้องมากกว่า 0" in parse_one(valid_row(price=raw)).errors[0]


@pytest.mark.parametrize("raw", ["ราคาพิเศษ", "free", "12abc"])
def test_non_numeric_price_is_an_error(raw):
    assert parse_one(valid_row(price=raw)).errors == [f'ราคา "{raw}" ไม่ใช่ตัวเลข']


def test_missing_price_is_an_error():
    assert parse_one(valid_row(price=None)).errors == ["ไม่มีราคา"]


def test_boolean_price_is_an_error():
    assert "ไม่ใช่ตัวเลข" in parse_one(valid_row(price=True)).errors[0]


def test_price_above_numeric_10_2_is_an_error():
    assert "ราคาสูงเกินไป" in parse_one(valid_row(price=100_000_000)).errors[0]


# --- status ---


@pytest.mark.parametrize("raw", [None, "", "  "])
def test_empty_status_means_active(raw):
    row = parse_one(valid_row(status=raw))
    assert row.errors == []
    assert row.data["status"] == "active"


@pytest.mark.parametrize("raw, expected", [(" active ", "active"), ("INACTIVE", "inactive"), ("Active", "active")])
def test_status_is_trimmed_and_lowercased(raw, expected):
    assert parse_one(valid_row(status=raw)).data["status"] == expected


@pytest.mark.parametrize("raw", ["yes", "enabled", "1"])
def test_unknown_status_is_an_error(raw):
    assert f'สถานะ "{raw}" ไม่ถูกต้อง' in parse_one(valid_row(status=raw)).errors[0]


# --- optional text ---


def test_optional_columns_may_be_empty():
    row = parse_one(["LS-2001", "Serum", "Serum", 500, None, None, None, None])
    assert row.errors == []
    assert row.data["size"] is None
    assert row.data["description"] is None
    assert row.data["how_to_use"] is None


def test_numeric_size_is_stored_as_text_without_decimal():
    assert parse_one(valid_row(size=30.0)).data["size"] == "30"


def test_very_long_description_is_an_error():
    assert "description ยาวเกิน" in parse_one(valid_row(description="x" * 5001)).errors[0]


def test_one_row_can_report_several_errors():
    row = parse_one(["LS-1029", "Travel Kit", None, 0, "4 ชิ้น", None, None, "active"])
    assert row.errors == ["ไม่มีหมวดหมู่ (category)", "ราคาต้องมากกว่า 0 (พบ 0)"]


# --- sheet layout ---


def test_blank_rows_are_skipped_and_row_numbers_stay_excel_numbers():
    rows = parse_workbook(make_xlsx([valid_row(sku="LS-2001"), [None] * 8, valid_row(sku="LS-2002")]))
    assert [r.row for r in rows] == [2, 4]


def test_headers_are_matched_case_and_space_insensitively_in_any_order():
    header = ["Name", " SKU ", "Price", "Category", "How To Use"]
    rows = parse_workbook(make_xlsx([["Serum A", "LS-2001", 500, "Serum", "daily"]], header=header))
    assert rows[0].errors == []
    assert rows[0].sku == "LS-2001"
    assert rows[0].data["how_to_use"] == "daily"
    assert rows[0].data["status"] == "active"  # missing optional column


def test_missing_required_column_rejects_the_file():
    with pytest.raises(HTTPException) as exc:
        parse_workbook(make_xlsx([["LS-2001", "Serum A"]], header=["sku", "name"]))
    assert exc.value.status_code == 400
    assert "category" in exc.value.detail and "price" in exc.value.detail


def test_empty_sheet_is_rejected():
    from io import BytesIO

    from openpyxl import Workbook

    buffer = BytesIO()
    Workbook().save(buffer)
    with pytest.raises(HTTPException) as exc:
        parse_workbook(buffer.getvalue())
    assert exc.value.detail == "ไฟล์ไม่มีข้อมูล"


def test_file_that_is_not_xlsx_is_rejected():
    with pytest.raises(HTTPException) as exc:
        parse_workbook(b"this is not a zip file")
    assert exc.value.status_code == 400
    assert "ไม่สามารถเปิดไฟล์ได้" in exc.value.detail


def test_too_many_rows_is_rejected():
    rows = [valid_row(sku=f"LS-{i % 10000:04d}") for i in range(MAX_DATA_ROWS + 1)]
    with pytest.raises(HTTPException) as exc:
        parse_workbook(make_xlsx(rows))
    assert f"เกิน {MAX_DATA_ROWS} แถว" in exc.value.detail


# --- the customer's real files ---


def test_first_customer_file_reports_every_bad_row(excel_file):
    rows = parse_workbook(excel_file("luma_products.xlsx"))
    errors = {r.row: r.errors for r in rows if r.errors}

    assert len(rows) == 30  # 31 data lines minus one blank line
    assert sum(not r.errors for r in rows) == 21
    assert sorted(errors) == [6, 9, 12, 15, 17, 20, 23, 30, 31]
    assert errors[6] == ["ไม่มีชื่อสินค้า"]
    assert errors[9] == ['ราคา "ราคาพิเศษ" ไม่ใช่ตัวเลข']
    assert "ซ้ำกับแถวที่ 5" in errors[12][0]
    assert errors[15] == ["ไม่มี SKU"]
    assert "ราคาต้องมากกว่า 0" in errors[17][0]
    assert 'สถานะ "yes"' in errors[20][0]
    assert '"Lotion"' in errors[23][0]
    assert errors[30] == ["ไม่มีหมวดหมู่ (category)"]
    assert len(errors[31]) == 2

    warnings = {r.row: r.warnings for r in rows if r.warnings and not r.errors}
    assert sorted(warnings) == [26, 27, 32]  # " LS-1024 ", "1,290", "ls-1030"


def test_second_customer_file_reports_missing_name(excel_file):
    rows = parse_workbook(excel_file("luma_products_update.xlsx"))
    assert len(rows) == 6
    assert [(r.row, r.errors) for r in rows if r.errors] == [(7, ["ไม่มีชื่อสินค้า"])]
