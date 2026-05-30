from pathlib import Path

import pytest

from markitdown import MarkItDown


def test_convert_many_preserves_order_with_parallel_workers(tmp_path: Path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first file", encoding="utf-8")
    second.write_text("second file", encoding="utf-8")

    results = MarkItDown().convert_many([first, second], max_workers=2)

    assert [result.markdown for result in results] == ["first file", "second file"]


def test_convert_many_validates_stream_info_length(tmp_path: Path):
    path = tmp_path / "file.txt"
    path.write_text("text", encoding="utf-8")

    with pytest.raises(ValueError, match="stream_infos"):
        MarkItDown().convert_many([path], stream_infos=[])
