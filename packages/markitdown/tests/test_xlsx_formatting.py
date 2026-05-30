from pathlib import Path

from openpyxl import Workbook

from markitdown import MarkItDown


def test_xlsx_currency_format_is_preserved(tmp_path: Path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Invoice"
    sheet.append(["Item", "Cost"])
    sheet.append(["Breakfast", 5])
    sheet.append(["Laptop", 1199])
    sheet["B2"].number_format = "$#,##0"
    sheet["B3"].number_format = "$#,##0"

    filename = tmp_path / "invoice.xlsx"
    workbook.save(filename)

    result = MarkItDown().convert(filename)

    assert "| Breakfast | $5 |" in result.markdown
    assert "| Laptop | $1,199 |" in result.markdown
