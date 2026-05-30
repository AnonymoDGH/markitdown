from pathlib import Path

from markitdown import MarkItDown


def test_empty_text_file_converts_to_empty_string(tmp_path: Path):
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")

    result = MarkItDown().convert(path)

    assert result.markdown == ""


def test_text_file_falls_back_to_replacement_decode(tmp_path: Path):
    path = tmp_path / "broken.txt"
    path.write_bytes(b"hello \xff world")

    result = MarkItDown().convert(path)

    assert "hello" in result.markdown
    assert "world" in result.markdown
