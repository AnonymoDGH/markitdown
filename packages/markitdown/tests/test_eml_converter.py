from pathlib import Path

from markitdown import MarkItDown, StreamInfo


def test_convert_eml_plain_text(tmp_path: Path):
    message = tmp_path / "message.eml"
    message.write_text(
        "From: sender@example.com\n"
        "To: receiver@example.com\n"
        "Subject: Hello EML\n"
        "Date: Sat, 30 May 2026 12:00:00 +0000\n"
        "Content-Type: text/plain; charset=utf-8\n"
        "\n"
        "This is the email body.\n",
        encoding="utf-8",
    )

    result = MarkItDown().convert(message)

    assert "**From:** sender@example.com" in result.markdown
    assert "**To:** receiver@example.com" in result.markdown
    assert "**Subject:** Hello EML" in result.markdown
    assert "This is the email body." in result.markdown
    assert result.title == "Hello EML"


def test_convert_eml_html_when_plain_text_missing(tmp_path: Path):
    message = tmp_path / "message.eml"
    message.write_text(
        "From: sender@example.com\n"
        "Subject: HTML EML\n"
        "Content-Type: text/html; charset=utf-8\n"
        "\n"
        "<h1>Hello</h1><p>HTML body</p>",
        encoding="utf-8",
    )

    result = MarkItDown().convert(
        message.open("rb"), stream_info=StreamInfo(extension=".eml")
    )

    assert "# Hello" in result.markdown
    assert "HTML body" in result.markdown
