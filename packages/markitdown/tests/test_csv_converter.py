from pathlib import Path

from markitdown import MarkItDown


def test_csv_escapes_markdown_pipes_and_keeps_extra_columns(tmp_path: Path):
    path = tmp_path / "data.csv"
    path.write_text("Name,Note\nAlice,a | b,extra\n", encoding="utf-8")

    result = MarkItDown().convert(path)

    assert "| Name | Note |  |" in result.markdown
    assert r"| Alice | a \| b | extra |" in result.markdown


def test_csv_sniffs_semicolon_delimiter(tmp_path: Path):
    path = tmp_path / "data.csv"
    path.write_text("Name;Value\nAlice;42\n", encoding="utf-8")

    result = MarkItDown().convert(path)

    assert "| Name | Value |" in result.markdown
    assert "| Alice | 42 |" in result.markdown


def test_tsv_extension_uses_tab_delimiter(tmp_path: Path):
    path = tmp_path / "data.tsv"
    path.write_text("Name\tValue\nAlice\t42\n", encoding="utf-8")

    result = MarkItDown().convert(path)

    assert "| Name | Value |" in result.markdown
    assert "| Alice | 42 |" in result.markdown
